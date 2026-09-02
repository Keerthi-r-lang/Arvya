from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_merchant
from app.db.models.audit_log import AuditLog
from app.db.models.merchant import Merchant
from app.db.session import get_db
from app.schemas.audit import AuditLogResponse
from app.schemas.product import CatalogSummary
from app.services.catalog_service import get_catalog_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return {
        "merchant": {"id": merchant.id, "name": merchant.name, "industry": merchant.industry},
        "catalog": get_catalog_summary(db, merchant.id),
        "growth_agent_status": "Catalog ready — generate growth opportunities on Day 2.",
    }


@router.get("/recent-activity", response_model=list[AuditLogResponse])
def recent_activity(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return list(db.scalars(select(AuditLog).where(AuditLog.merchant_id == merchant.id).order_by(AuditLog.created_at.desc()).limit(8)))

