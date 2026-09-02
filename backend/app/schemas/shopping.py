from datetime import datetime

from pydantic import BaseModel, Field


class ShoppingSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=300)
    budget_paise: int | None = Field(default=None, gt=0)
    merchant_id: int | None = None


class ShoppingOfferResponse(BaseModel):
    recommendation_id: int
    merchant_id: int
    merchant_name: str
    merchant_industry: str
    title: str
    type: str
    products: list[str]
    original_price_paise: int | None
    offer_price_paise: int
    coupon_code: str | None
    coupon_discount_paise: int
    final_price_paise: int
    relevance_score: int
    explanation: str
    confidence_score: float


class ShoppingSearchResponse(BaseModel):
    query: str
    recommendation_summary: str
    offers: list[ShoppingOfferResponse]


class CheckoutRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=120)
    customer_email: str = Field(min_length=5, max_length=255)
    coupon_code: str | None = Field(default=None, max_length=40)


class PaymentLinkResponse(BaseModel):
    id: int
    recommendation_id: int
    amount_paise: int
    currency: str
    status: str
    provider: str
    short_url: str | None
    coupon_code: str | None
    failure_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
