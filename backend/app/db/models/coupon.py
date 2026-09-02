from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Coupon(Base):
    __tablename__ = "coupons"
    __table_args__ = (UniqueConstraint("merchant_id", "code", name="uq_coupon_merchant_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    max_discount_paise: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_order_paise: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

