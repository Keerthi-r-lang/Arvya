from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.merchant import Merchant
from app.db.models.product import Product
from app.services.audit_service import write_audit_log

SEED_DATA = [
    ("Glow Naturals", "hello@glownaturals.demo", "Beauty & wellness", [
        ("GN-FW-01", "Neem Face Wash", "Cleanser", 29900, 11200, 120),
        ("GN-MO-01", "Daily Hydration Moisturizer", "Moisturizer", 49900, 18500, 90),
        ("GN-SS-01", "SPF 50 Sunscreen", "Sun Protection", 69900, 24000, 75),
        ("GN-SE-01", "Vitamin C Brightening Serum", "Serum", 89900, 38500, 55),
        ("GN-TK-01", "Travel Skincare Kit", "Gift Sets", 99900, 44000, 30),
    ]),
    ("SkinCraft", "hello@skincraft.demo", "Beauty & wellness", [
        ("SC-FW-01", "Gentle Gel Cleanser", "Cleanser", 34900, 13000, 100),
        ("SC-MO-01", "Ceramide Barrier Cream", "Moisturizer", 54900, 21500, 80),
        ("SC-SS-01", "Invisible SPF 50", "Sun Protection", 74900, 29000, 65),
        ("SC-SE-01", "Niacinamide Repair Serum", "Serum", 84900, 36000, 40),
    ]),
    ("PureBloom", "hello@purebloom.demo", "Beauty & wellness", [
        ("PB-FW-01", "Aloe Foaming Cleanser", "Cleanser", 27900, 9800, 140),
        ("PB-MO-01", "Lightweight Daily Moisturizer", "Moisturizer", 45900, 17000, 110),
        ("PB-SS-01", "Mineral SPF 40", "Sun Protection", 62900, 23500, 50),
        ("PB-SE-01", "Glow Renewal Serum", "Serum", 79900, 32200, 45),
    ]),
]


def seed_database(db: Session) -> None:
    if db.scalar(select(Merchant.id).limit(1)) is not None:
        return
    for name, email, industry, products in SEED_DATA:
        merchant = Merchant(name=name, email=email, industry=industry)
        db.add(merchant)
        db.flush()
        for sku, product_name, category, price, cost, inventory in products:
            db.add(Product(merchant_id=merchant.id, sku=sku, name=product_name, category=category, price_paise=price, cost_paise=cost, inventory_count=inventory))
        write_audit_log(db, merchant.id, "merchant_onboarded", "merchant", str(merchant.id), "Demo merchant and catalog were initialized.", actor_type="system", actor_id="seed")
        write_audit_log(db, merchant.id, "catalog_seeded", "catalog", str(merchant.id), f"Initialized {len(products)} demo products.", actor_type="system", actor_id="seed")
    db.commit()

