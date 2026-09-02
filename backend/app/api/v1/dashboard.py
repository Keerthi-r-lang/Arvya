from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_merchant
from app.db.models.audit_log import AuditLog
from app.db.models.merchant import Merchant
from app.db.models.payment_link import PaymentLink
from app.db.models.recommendation import Recommendation
from app.db.session import get_db
from app.schemas.audit import AuditLogResponse
from app.schemas.product import CatalogSummary
from app.services.catalog_service import get_catalog_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    paid_revenue = db.scalar(select(func.coalesce(func.sum(PaymentLink.amount_paise), 0)).where(PaymentLink.merchant_id == merchant.id, PaymentLink.status == "paid"))
    payment_links_created = db.scalar(select(func.count(PaymentLink.id)).where(PaymentLink.merchant_id == merchant.id))
    paid_links = db.scalar(select(func.count(PaymentLink.id)).where(PaymentLink.merchant_id == merchant.id, PaymentLink.status == "paid"))
    approved_offers = db.scalar(select(func.count(Recommendation.id)).where(Recommendation.merchant_id == merchant.id, Recommendation.status == "approved"))
    estimated_uplift = sum((recommendation.impact_json or {}).get("estimated_monthly_revenue_uplift_inr", 0) for recommendation in db.scalars(select(Recommendation).where(Recommendation.merchant_id == merchant.id, Recommendation.status == "approved")))
    return {
        "merchant": {"id": merchant.id, "name": merchant.name, "industry": merchant.industry},
        "catalog": get_catalog_summary(db, merchant.id),
        "growth_agent_status": "Growth Agent is ready to create governed offers.",
        "commerce_metrics": {"actual_paid_revenue_paise": paid_revenue, "payment_links_created": payment_links_created, "paid_links": paid_links, "approved_offers": approved_offers, "estimated_monthly_uplift_inr": estimated_uplift},
    }


@router.get("/recent-activity", response_model=list[AuditLogResponse])
def recent_activity(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return list(db.scalars(select(AuditLog).where(AuditLog.merchant_id == merchant.id).order_by(AuditLog.created_at.desc()).limit(8)))
