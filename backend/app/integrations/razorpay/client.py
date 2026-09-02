import base64
import json
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings


class RazorpayIntegrationError(Exception):
    pass


def has_razorpay_test_credentials() -> bool:
    settings = get_settings()
    return bool(settings.razorpay_key_id and settings.razorpay_key_secret)


def create_payment_link(*, amount_paise: int, currency: str, reference_id: str, description: str, customer_name: str, customer_email: str, notes: dict[str, str]) -> dict:
    settings = get_settings()
    if not has_razorpay_test_credentials():
        raise RazorpayIntegrationError("Razorpay Test Mode credentials are not configured. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to backend/.env.")
    credentials = base64.b64encode(f"{settings.razorpay_key_id}:{settings.razorpay_key_secret}".encode()).decode()
    payload = {
        "amount": amount_paise,
        "currency": currency,
        "accept_partial": False,
        "reference_id": reference_id,
        "description": description,
        "customer": {"name": customer_name, "email": customer_email},
        "notify": {"sms": False, "email": False},
        "reminder_enable": False,
        "expire_by": int((datetime.now(timezone.utc) + timedelta(days=2)).timestamp()),
        "notes": notes,
    }
    request = Request(
        "https://api.razorpay.com/v1/payment_links",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Basic {credentials}"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode())
    except HTTPError as error:
        body = error.read().decode(errors="replace")[:500]
        raise RazorpayIntegrationError(f"Razorpay API returned {error.code}: {body}") from error
    except URLError as error:
        raise RazorpayIntegrationError("Could not reach Razorpay API. The payment link was not created.") from error
