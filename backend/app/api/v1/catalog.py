from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_merchant
from app.db.models.merchant import Merchant
from app.db.models.product import Product
from app.db.session import get_db
from app.schemas.product import CatalogSummary, ProductCreate, ProductResponse, UploadResult
from app.services.catalog_service import create_product, get_catalog_summary, import_catalog_csv

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/products", response_model=list[ProductResponse])
def list_products(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return list(db.scalars(select(Product).where(Product.merchant_id == merchant.id).order_by(Product.category, Product.name)))


@router.post("/products", response_model=ProductResponse, status_code=201)
def add_product(payload: ProductCreate, merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return create_product(db, merchant, payload)


@router.post("/upload", response_model=UploadResult)
async def upload_catalog(file: UploadFile = File(...), merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Upload a CSV file")
    return import_catalog_csv(db, merchant, await file.read())


@router.get("/summary", response_model=CatalogSummary)
def catalog_summary(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return get_catalog_summary(db, merchant.id)

