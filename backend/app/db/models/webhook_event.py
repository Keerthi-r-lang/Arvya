from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(40), default="razorpay")
    provider_event_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payment_link_external_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    signature_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    payload_summary_json: Mapped[dict] = mapped_column(JSON, default=dict)
    processing_status: Mapped[str] = mapped_column(String(30), default="received")
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
