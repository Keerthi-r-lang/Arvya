from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    price_paise: int = Field(gt=0)
    cost_paise: int | None = Field(default=None, ge=0)
    inventory_count: int = Field(default=0, ge=0)
    status: str = "active"


class ProductResponse(ProductCreate):
    id: int
    merchant_id: int

    model_config = {"from_attributes": True}


class CatalogSummary(BaseModel):
    total_products: int
    active_products: int
    categories: int
    missing_cost_data: int
    out_of_stock: int
    average_price_paise: int


class UploadResult(BaseModel):
    imported_count: int
    failed_count: int
    warnings: list[str]

