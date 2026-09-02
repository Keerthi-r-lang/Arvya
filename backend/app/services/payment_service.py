from hashlib import sha256

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.payment_link import PaymentLink
from app.db.models.recommendation import Recommendation
from app.integrations.razorpay.client import RazorpayIntegrationError, create_payment_link, has_razorpay_test_credentials
from app.schemas.shopping import CheckoutRequest
from app.services.audit_service import write_audit_log
from app.services.shopping_service import _best_coupon, _discount, checkout_idempotency_key


def _get_approved_recommendation(db: Session, recommendation_id: int) -> Recommendation:
    recommendation = db.get(Recommendation, recommendation_id)
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Approved offer not found")
    if recommendation.status != "approved":
        raise HTTPException(status_code=409, detail="This offer cannot be checked out until the merchant approves it")
    return recommendation


def create_checkout_link(db: Session, recommendation_id: int, request: CheckoutRequest) -> PaymentLink:
    recommendation = _get_approved_recommendation(db, recommendation_id)
    base_amount = recommendation.action_payload_json.get("proposed_price_paise") or recommendation.action_payload_json.get("original_price_paise")
    if not base_amount:
        raise HTTPException(status_code=422, detail="Approved offer does not have a payable amount")
    coupon = _best_coupon(db, recommendation.merchant_id, base_amount, request.coupon_code)
    amount = base_amount - _discount(coupon, base_amount)
    key = checkout_idempotency_key(recommendation.id, request.customer_email, coupon.code if coupon else None)
    existing = db.scalar(select(PaymentLink).where(PaymentLink.merchant_id == recommendation.merchant_id, PaymentLink.idempotency_key == key))
    if existing and existing.status in {"created", "issued", "paid"}:
        return existing
    if existing and existing.status == "demo_created" and not has_razorpay_test_credentials():
        return existing
    if existing:
        # A prior demo fallback or failed attempt is safe to retry when the customer submits the same checkout.
        payment_link = existing
        payment_link.amount_paise = amount
        payment_link.customer_name = request.customer_name
        payment_link.customer_email = request.customer_email
        payment_link.coupon_code = coupon.code if coupon else None
        payment_link.status = "execution_pending"
        payment_link.provider = "razorpay"
        payment_link.failure_reason = None
        payment_link.provider_response_json = {}
    else:
        payment_link = PaymentLink(merchant_id=recommendation.merchant_id, recommendation_id=recommendation.id, amount_paise=amount, currency="INR", customer_name=request.customer_name, customer_email=request.customer_email, coupon_code=coupon.code if coupon else None, idempotency_key=key)
        db.add(payment_link)
        db.flush()
        write_audit_log(db, recommendation.merchant_id, "payment_link_requested", "payment_link", str(payment_link.id), "Customer selected a merchant-approved offer for checkout.", actor_type="customer", actor_id=request.customer_email)
    if not has_razorpay_test_credentials():
        payment_link.provider = "demo"
        payment_link.status = "demo_created"
        payment_link.failure_reason = "Demo checkout created. Configure Razorpay Test Mode credentials to create a live Test Mode payment link."
        db.commit()
        return payment_link
    try:
        reference_id = f"arvya-{payment_link.id}-{key[:8]}"
        result = create_payment_link(amount_paise=amount, currency="INR", reference_id=reference_id, description=f"Arvya approved offer: {recommendation.title}", customer_name=request.customer_name, customer_email=request.customer_email, notes={"arvya_recommendation_id": str(recommendation.id), "arvya_payment_link_id": str(payment_link.id)})
        payment_link.razorpay_payment_link_id = result.get("id")
        payment_link.short_url = result.get("short_url")
        payment_link.status = result.get("status", "created")
        payment_link.provider_response_json = {"id": result.get("id"), "short_url": result.get("short_url"), "status": result.get("status")}
        write_audit_log(db, recommendation.merchant_id, "payment_link_created", "payment_link", str(payment_link.id), f"Razorpay Test Mode payment link created for ₹{amount / 100:.2f}.", actor_type="system", actor_id="RazorpayPaymentAgent")
        db.commit()
        return payment_link
    except RazorpayIntegrationError as error:
        payment_link.status = "execution_failed"
        payment_link.failure_reason = str(error)
        write_audit_log(db, recommendation.merchant_id, "payment_link_failed", "payment_link", str(payment_link.id), str(error), actor_type="system", actor_id="RazorpayPaymentAgent")
        db.commit()
        raise HTTPException(status_code=502, detail="Payment link creation failed safely. No charge was attempted.") from error


def list_payment_links(db: Session, merchant_id: int) -> list[PaymentLink]:
    return list(db.scalars(select(PaymentLink).where(PaymentLink.merchant_id == merchant_id).order_by(PaymentLink.created_at.desc())))
