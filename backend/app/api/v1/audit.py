from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_merchant
from app.db.models.audit_log import AuditLog
from app.db.models.merchant import Merchant
from app.db.session import get_db
from app.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return list(db.scalars(select(AuditLog).where(AuditLog.merchant_id == merchant.id).order_by(AuditLog.created_at.desc())))

