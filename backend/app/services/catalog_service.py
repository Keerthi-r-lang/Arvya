import csv
import io

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.merchant import Merchant
from app.db.models.product import Product
from app.schemas.product import CatalogSummary, ProductCreate, UploadResult
from app.services.audit_service import write_audit_log


def create_product(db: Session, merchant: Merchant, payload: ProductCreate) -> Product:
    product = Product(merchant_id=merchant.id, **payload.model_dump())
    db.add(product)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="SKU already exists in this catalog") from exc
    write_audit_log(
        db, merchant.id, "product_created", "product", str(product.id), f"Added {product.name} ({product.sku})."
    )
    db.commit()
    db.refresh(product)
    return product


def get_catalog_summary(db: Session, merchant_id: int) -> CatalogSummary:
    products = list(db.scalars(select(Product).where(Product.merchant_id == merchant_id)))
    if not products:
        return CatalogSummary(total_products=0, active_products=0, categories=0, missing_cost_data=0, out_of_stock=0, average_price_paise=0)
    return CatalogSummary(
        total_products=len(products),
        active_products=sum(p.status == "active" for p in products),
        categories=len({p.category for p in products}),
        missing_cost_data=sum(p.cost_paise is None for p in products),
        out_of_stock=sum(p.inventory_count == 0 for p in products),
        average_price_paise=int(sum(p.price_paise for p in products) / len(products)),
    )


def import_catalog_csv(db: Session, merchant: Merchant, raw_file: bytes) -> UploadResult:
    try:
        rows = list(csv.DictReader(io.StringIO(raw_file.decode("utf-8-sig"))))
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from exc
    required = {"sku", "name", "category", "price_inr"}
    if not rows or not required.issubset(set(rows[0].keys())):
        raise HTTPException(status_code=400, detail="CSV requires sku, name, category, price_inr columns")
    imported, failed, warnings = 0, 0, []
    for index, row in enumerate(rows, start=2):
        try:
            product = Product(
                merchant_id=merchant.id,
                sku=row["sku"].strip(),
                name=row["name"].strip(),
                category=row["category"].strip(),
                price_paise=int(float(row["price_inr"]) * 100),
                cost_paise=int(float(row["cost_inr"]) * 100) if row.get("cost_inr") else None,
                inventory_count=int(row.get("inventory_count") or 0),
                status=(row.get("status") or "active").strip(),
            )
            if not product.sku or not product.name or product.price_paise <= 0:
                raise ValueError("missing required product data")
            db.add(product)
            db.flush()
            imported += 1
        except (ValueError, IntegrityError):
            db.rollback()
            failed += 1
            warnings.append(f"Row {index} was skipped: invalid data or duplicate SKU.")
    write_audit_log(db, merchant.id, "catalog_uploaded", "catalog", str(merchant.id), f"Imported {imported} products; {failed} rows skipped.")
    db.commit()
    return UploadResult(imported_count=imported, failed_count=failed, warnings=warnings[:5])

