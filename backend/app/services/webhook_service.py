import hashlib
import hmac
import json
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.payment_link import PaymentLink
from app.db.models.webhook_event import WebhookEvent
from app.services.audit_service import write_audit_log


def verify_webhook_signature(raw_body: bytes, received_signature: str | None) -> None:
    secret = get_settings().razorpay_webhook_secret
    if not secret:
        raise HTTPException(status_code=503, detail="Razorpay webhook secret is not configured")
    if not received_signature:
        raise HTTPException(status_code=401, detail="Missing Razorpay webhook signature")
    expected_signature = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_signature, received_signature):
        raise HTTPException(status_code=401, detail="Invalid Razorpay webhook signature")


def process_razorpay_webhook(db: Session, raw_body: bytes, signature: str | None, event_id: str | None) -> dict:
    verify_webhook_signature(raw_body, signature)
    try:
        event = json.loads(raw_body)
    except json.JSONDecodeError as error:
        raise HTTPException(status_code=400, detail="Webhook payload is not valid JSON") from error
    provider_event_id = event_id or event.get("id")
    if not provider_event_id:
        raise HTTPException(status_code=400, detail="Webhook event ID is missing")
    existing = db.scalar(select(WebhookEvent).where(WebhookEvent.provider_event_id == provider_event_id))
    if existing:
        return {"status": "duplicate", "event_id": provider_event_id}
    event_type = event.get("event", "unknown")
    payload = event.get("payload", {})
    link_entity = payload.get("payment_link", {}).get("entity", {})
    payment_entity = payload.get("payment", {}).get("entity", {})
    external_link_id = link_entity.get("id")
    webhook_event = WebhookEvent(provider_event_id=provider_event_id, event_type=event_type, payment_link_external_id=external_link_id, signature_verified=True, payload_summary_json={"payment_link_status": link_entity.get("status"), "payment_id": payment_entity.get("id"), "amount": link_entity.get("amount")})
    db.add(webhook_event)
    payment_link = db.scalar(select(PaymentLink).where(PaymentLink.razorpay_payment_link_id == external_link_id)) if external_link_id else None
    if payment_link is None:
        webhook_event.processing_status = "unmatched"
        webhook_event.error_summary = "No local payment link matched this Razorpay payment link ID."
        webhook_event.processed_at = datetime.utcnow()
        db.commit()
        return {"status": "unmatched", "event_id": provider_event_id}
    next_status = {"payment_link.paid": "paid", "payment_link.partially_paid": "partially_paid", "payment_link.cancelled": "cancelled"}.get(event_type, link_entity.get("status", payment_link.status))
    response = dict(payment_link.provider_response_json or {})
    response.update({"webhook_event_id": provider_event_id, "payment_id": payment_entity.get("id"), "payment_link_status": link_entity.get("status"), "amount_paid": link_entity.get("amount_paid")})
    payment_link.status = next_status
    payment_link.provider_response_json = response
    payment_link.failure_reason = None if next_status == "paid" else payment_link.failure_reason
    webhook_event.processing_status = "processed"
    webhook_event.processed_at = datetime.utcnow()
    write_audit_log(db, payment_link.merchant_id, "razorpay_webhook_processed", "payment_link", str(payment_link.id), f"Verified Razorpay webhook {event_type}; payment link is now {next_status}.", actor_type="razorpay", actor_id=provider_event_id)
    db.commit()
    return {"status": "processed", "event_id": provider_event_id, "payment_link_status": next_status}
