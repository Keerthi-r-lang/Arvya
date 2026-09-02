from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_merchant
from app.core.security import create_access_token
from app.db.models.merchant import Merchant
from app.db.session import get_db
from app.schemas.auth import DemoLoginRequest, LoginResponse, MerchantResponse
from app.services.audit_service import write_audit_log

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def demo_login(payload: DemoLoginRequest, db: Session = Depends(get_db)):
    merchant = db.get(Merchant, payload.merchant_id)
    if merchant is None:
        raise HTTPException(status_code=404, detail="Demo merchant not found")
    write_audit_log(db, merchant.id, "merchant_logged_in", "merchant", str(merchant.id), "Merchant signed in through demo login.")
    db.commit()
    return LoginResponse(access_token=create_access_token(merchant.id), merchant=merchant)


@router.get("/merchants", response_model=list[MerchantResponse])
def demo_merchants(db: Session = Depends(get_db)):
    return list(db.scalars(select(Merchant).order_by(Merchant.name)))


@router.get("/me", response_model=MerchantResponse)
def current_merchant(merchant: Merchant = Depends(get_current_merchant)):
    return merchant

