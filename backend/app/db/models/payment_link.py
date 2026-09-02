from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PaymentLink(Base):
    __tablename__ = "payment_links"
    __table_args__ = (UniqueConstraint("merchant_id", "idempotency_key", name="uq_payment_link_merchant_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), nullable=False, index=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("recommendations.id"), nullable=False, index=True)
    razorpay_payment_link_id: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True)
    short_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[str] = mapped_column(String(40), default="execution_pending", index=True)
    provider: Mapped[str] = mapped_column(String(30), default="razorpay")
    idempotency_key: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    coupon_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    provider_response_json: Mapped[dict] = mapped_column(JSON, default=dict)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

