from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.webhook_service import process_razorpay_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/razorpay")
async def razorpay_webhook(request: Request, x_razorpay_signature: str | None = Header(default=None), x_razorpay_event_id: str | None = Header(default=None), db: Session = Depends(get_db)):
    return process_razorpay_webhook(db, await request.body(), x_razorpay_signature, x_razorpay_event_id)
