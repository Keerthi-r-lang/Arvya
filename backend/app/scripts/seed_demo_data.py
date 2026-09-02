from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.merchant import Merchant
from app.db.models.product import Product
from app.db.models.coupon import Coupon
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
    ("Bean Street", "hello@beanstreet.demo", "Coffee & beverages", [
        ("BS-BR-01", "South Indian Filter Coffee", "Coffee", 34900, 12800, 150),
        ("BS-BR-02", "Single Origin Arabica Beans", "Coffee", 64900, 25500, 80),
        ("BS-AC-01", "Stainless Steel Coffee Filter", "Brewing Equipment", 79900, 33000, 45),
        ("BS-AC-02", "Ceramic Pour Over Dripper", "Brewing Equipment", 99900, 42000, 32),
        ("BS-GF-01", "Coffee Discovery Gift Box", "Gift Sets", 119900, 52000, 20),
    ]),
    ("Urban Trail", "hello@urbantrail.demo", "Fitness & outdoor", [
        ("UT-YM-01", "Non-Slip Yoga Mat", "Yoga", 89900, 34000, 72),
        ("UT-YB-01", "Resistance Band Set", "Strength Training", 59900, 21000, 95),
        ("UT-YB-02", "Cork Yoga Block Pair", "Yoga", 49900, 18000, 60),
        ("UT-HY-01", "Insulated Steel Water Bottle", "Accessories", 74900, 28500, 110),
        ("UT-GF-01", "Weekend Wellness Kit", "Gift Sets", 189900, 79000, 25),
    ]),
]


def seed_database(db: Session) -> None:
    for name, email, industry, products in SEED_DATA:
        merchant = db.scalar(select(Merchant).where(Merchant.email == email))
        is_new_merchant = merchant is None
        if merchant is None:
            merchant = Merchant(name=name, email=email, industry=industry)
            db.add(merchant)
            db.flush()
        seeded_count = 0
        for sku, product_name, category, price, cost, inventory in products:
            exists = db.scalar(select(Product.id).where(Product.merchant_id == merchant.id, Product.sku == sku))
            if exists is None:
                db.add(Product(merchant_id=merchant.id, sku=sku, name=product_name, category=category, price_paise=price, cost_paise=cost, inventory_count=inventory))
                seeded_count += 1
        if is_new_merchant:
            write_audit_log(db, merchant.id, "merchant_onboarded", "merchant", str(merchant.id), "Demo merchant and catalog were initialized.", actor_type="system", actor_id="seed")
        if seeded_count:
            write_audit_log(db, merchant.id, "catalog_seeded", "catalog", str(merchant.id), f"Initialized {seeded_count} demo products.", actor_type="system", actor_id="seed")
        coupon_code = {"Beauty & wellness": "GLOW10", "Coffee & beverages": "BREW10", "Fitness & outdoor": "MOVE10"}.get(industry)
        if coupon_code and db.scalar(select(Coupon.id).where(Coupon.merchant_id == merchant.id, Coupon.code == coupon_code)) is None:
            db.add(Coupon(merchant_id=merchant.id, code=coupon_code, discount_percent=10, max_discount_paise=20000, min_order_paise=50000))
    db.commit()
