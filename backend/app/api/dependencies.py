from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models.merchant import Merchant
from app.db.session import get_db

bearer_scheme = HTTPBearer()


def get_current_merchant(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Merchant:
    merchant_id = decode_access_token(credentials.credentials)
    merchant = db.get(Merchant, merchant_id)
    if merchant is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Merchant account not found")
    return merchant

