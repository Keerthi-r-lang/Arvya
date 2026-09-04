from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_merchant
from app.db.models.merchant import Merchant
from app.db.session import get_db
from app.schemas.shopping import CheckoutRequest, PaymentLinkResponse, ShoppingSearchRequest, ShoppingSearchResponse
from app.services.payment_service import create_checkout_link, list_payment_links, retry_payment_link
from app.services.shopping_service import search_approved_offers

router = APIRouter(tags=["customer-shopping-agent"])


@router.post("/shopping/search", response_model=ShoppingSearchResponse)
def search_offers(payload: ShoppingSearchRequest, db: Session = Depends(get_db)):
    return search_approved_offers(db, payload.query, payload.budget_paise, payload.merchant_id)


@router.post("/shopping/offers/{recommendation_id}/checkout", response_model=PaymentLinkResponse, status_code=201)
def checkout(recommendation_id: int, payload: CheckoutRequest, x_idempotency_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    return create_checkout_link(db, recommendation_id, payload, checkout_token=x_idempotency_key)


@router.get("/payment-links", response_model=list[PaymentLinkResponse])
def merchant_payment_links(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return list_payment_links(db, merchant.id)


@router.post("/payment-links/{payment_link_id}/retry", response_model=PaymentLinkResponse)
def retry_link(payment_link_id: int, merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return retry_payment_link(db, merchant.id, payment_link_id)
