import re
from hashlib import sha256

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.coupon import Coupon
from app.db.models.merchant import Merchant
from app.db.models.product import Product
from app.db.models.recommendation import Recommendation
from app.db.models.recommendation_item import RecommendationItem

INTENT_ALIASES = {
    "skincare": {"skin", "skincare", "face", "facial", "cleanser", "moisturizer", "sunscreen", "serum", "glow", "beauty"},
    "coffee": {"coffee", "caffeine", "bean", "beans", "brew", "brewing", "dripper", "filter", "mug"},
    "fitness": {"fitness", "gym", "workout", "exercise", "yoga", "wellness", "resistance", "training", "mat"},
}

INDUSTRY_INTENT = {"Beauty & wellness": "skincare", "Coffee & beverages": "coffee", "Fitness & outdoor": "fitness"}


def _terms(text: str) -> set[str]:
    return {term for term in re.findall(r"[a-zA-Z]{3,}", text.lower()) if term not in {"for", "and", "with", "the", "under", "need", "want"}}


def _intent_labels(terms: set[str]) -> set[str]:
    return {intent for intent, aliases in INTENT_ALIASES.items() if terms.intersection(aliases)}


def _discount(coupon: Coupon | None, amount_paise: int) -> int:
    if coupon is None or amount_paise < coupon.min_order_paise:
        return 0
    discount = amount_paise * coupon.discount_percent // 100
    return min(discount, coupon.max_discount_paise) if coupon.max_discount_paise else discount


def _best_coupon(db: Session, merchant_id: int, amount_paise: int, requested_code: str | None = None) -> Coupon | None:
    coupons = list(db.scalars(select(Coupon).where(Coupon.merchant_id == merchant_id, Coupon.status == "active")))
    if requested_code:
        coupons = [coupon for coupon in coupons if coupon.code.lower() == requested_code.lower()]
        if not coupons:
            raise HTTPException(status_code=422, detail="Coupon is not valid for this merchant-approved offer")
    eligible = [coupon for coupon in coupons if amount_paise >= coupon.min_order_paise]
    return max(eligible, key=lambda coupon: _discount(coupon, amount_paise), default=None)


def search_approved_offers(db: Session, query: str, budget_paise: int | None = None, merchant_id: int | None = None) -> dict:
    statement = select(Recommendation, Merchant).join(Merchant, Recommendation.merchant_id == Merchant.id).where(Recommendation.status == "approved")
    if merchant_id:
        statement = statement.where(Recommendation.merchant_id == merchant_id)
    desired_terms = _terms(query)
    desired_intents = _intent_labels(desired_terms)
    results = []
    for recommendation, merchant in db.execute(statement):
        items = list(db.scalars(select(RecommendationItem).where(RecommendationItem.recommendation_id == recommendation.id)))
        product_names = []
        product_categories = []
        if items:
            product_ids = [item.product_id for item in items]
            product_records = list(db.execute(select(Product.name, Product.category).where(Product.id.in_(product_ids))))
            product_names = [record.name for record in product_records]
            product_categories = [record.category for record in product_records]
        payload = recommendation.action_payload_json
        offer_price = payload.get("proposed_price_paise") or payload.get("original_price_paise")
        if not offer_price:
            continue
        coupon = _best_coupon(db, merchant.id, offer_price)
        discount = _discount(coupon, offer_price)
        final_price = offer_price - discount
        if budget_paise and final_price > budget_paise:
            continue
        offer_intent = INDUSTRY_INTENT.get(merchant.industry)
        if desired_intents and offer_intent not in desired_intents:
            continue
        searchable_text = " ".join([recommendation.title, recommendation.rationale, merchant.name, merchant.industry, *product_names, *product_categories])
        matched_terms = desired_terms.intersection(_terms(searchable_text))
        score = len(matched_terms) * 25 + int(recommendation.confidence_score * 25) + (10 if coupon else 0) + (30 if offer_intent in desired_intents else 0)
        if not matched_terms and not desired_intents:
            continue
        if budget_paise:
            score += max(0, 15 - int((budget_paise - final_price) / max(budget_paise, 1) * 10))
        reason_bits = []
        if matched_terms:
            reason_bits.append(f"matches your intent: {', '.join(sorted(matched_terms))}")
        if coupon:
            reason_bits.append(f"applies merchant-approved coupon {coupon.code}")
        reason_bits.append(f"is an approved {recommendation.type} from {merchant.name}")
        results.append({"recommendation_id": recommendation.id, "merchant_id": merchant.id, "merchant_name": merchant.name, "merchant_industry": merchant.industry, "title": recommendation.title, "type": recommendation.type, "products": product_names, "original_price_paise": payload.get("original_price_paise"), "offer_price_paise": offer_price, "coupon_code": coupon.code if coupon else None, "coupon_discount_paise": discount, "final_price_paise": final_price, "relevance_score": score, "explanation": "This offer " + ", ".join(reason_bits) + ".", "confidence_score": recommendation.confidence_score})
    results.sort(key=lambda item: (-item["relevance_score"], item["final_price_paise"]))
    summary = "No approved offers match this search yet. Try skincare, coffee, or fitness terms, or ask a merchant to generate and approve an offer first." if not results else f"Compared {len(results)} merchant-approved offers for this intent. The ranking uses intent relevance, offer confidence, coupon eligibility, and final price."
    return {"query": query, "recommendation_summary": summary, "offers": results[:6]}


def checkout_idempotency_key(recommendation_id: int, email: str, coupon_code: str | None, checkout_token: str | None = None) -> str:
    """Create a bounded key for one checkout attempt.

    The browser supplies a different token for every deliberate checkout.  This
    keeps a network retry idempotent without permanently reusing a past Razorpay
    link merely because the customer chose the same offer with the same email.
    """
    return sha256(f"{recommendation_id}:{email.lower()}:{coupon_code or ''}:{checkout_token or ''}".encode()).hexdigest()
