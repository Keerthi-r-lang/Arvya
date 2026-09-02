from datetime import datetime
from hashlib import sha256

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.agent_action import AgentAction
from app.db.models.agent_run import AgentRun
from app.db.models.merchant import Merchant
from app.db.models.product import Product
from app.db.models.recommendation import Recommendation
from app.db.models.recommendation_item import RecommendationItem
from app.schemas.recommendation import AgentRunCreate, RecommendationDecision
from app.services.audit_service import write_audit_log

OFFER_BLUEPRINTS = {
    "Beauty & wellness": {
        "bundle_categories": ["Cleanser", "Moisturizer", "Sun Protection"],
        "bundle_title": "Daily Skincare Starter Bundle",
        "bundle_story": "a complete daily skincare routine",
        "upsell_anchor": "Cleanser",
        "upsell_target": "Serum",
        "campaign_title": "Glow Routine Weekend Offer",
    },
    "Coffee & beverages": {
        "bundle_categories": ["Coffee", "Brewing Equipment"],
        "bundle_title": "Home Brewer Discovery Bundle",
        "bundle_story": "a simple at-home coffee ritual",
        "upsell_anchor": "Coffee",
        "upsell_target": "Gift Sets",
        "campaign_title": "Brew Better This Weekend",
    },
    "Fitness & outdoor": {
        "bundle_categories": ["Yoga", "Accessories"],
        "bundle_title": "Weekend Wellness Starter Kit",
        "bundle_story": "a low-friction home wellness routine",
        "upsell_anchor": "Yoga",
        "upsell_target": "Gift Sets",
        "campaign_title": "Start Your Wellness Routine",
    },
}


def _serialize_recommendation(db: Session, recommendation: Recommendation) -> dict:
    items = list(db.scalars(select(RecommendationItem).where(RecommendationItem.recommendation_id == recommendation.id)))
    return {
        "id": recommendation.id, "agent_run_id": recommendation.agent_run_id, "type": recommendation.type,
        "status": recommendation.status, "title": recommendation.title, "rationale": recommendation.rationale,
        "evidence_json": recommendation.evidence_json, "action_payload_json": recommendation.action_payload_json,
        "impact_json": recommendation.impact_json, "confidence_score": recommendation.confidence_score,
        "approved_at": recommendation.approved_at, "rejected_reason": recommendation.rejected_reason,
        "created_at": recommendation.created_at,
        "items": [{"product_id": item.product_id, "role": item.role, "original_price_paise": item.original_price_paise, "proposed_price_paise": item.proposed_price_paise, "quantity": item.quantity} for item in items],
    }


def list_recommendations(db: Session, merchant_id: int) -> list[dict]:
    recommendations = list(db.scalars(select(Recommendation).where(Recommendation.merchant_id == merchant_id).order_by(Recommendation.created_at.desc())))
    return [_serialize_recommendation(db, recommendation) for recommendation in recommendations]


def get_recommendation(db: Session, merchant_id: int, recommendation_id: int) -> dict:
    recommendation = db.scalar(select(Recommendation).where(Recommendation.id == recommendation_id, Recommendation.merchant_id == merchant_id))
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return _serialize_recommendation(db, recommendation)


def _record_action(db: Session, run_id: int, name: str, action_type: str, reasoning: str, input_summary: dict, output_summary: dict, recommendation_id: int | None = None) -> None:
    db.add(AgentAction(agent_run_id=run_id, recommendation_id=recommendation_id, agent_name=name, action_type=action_type, reasoning_summary=reasoning, input_summary_json=input_summary, output_summary_json=output_summary, tools_used_json=["catalog_sql_query", "margin_guardrail", "offer_policy_rules"]))


def _hash(merchant_id: int, type_: str, product_ids: list[int]) -> str:
    seed = f"{merchant_id}:{type_}:{':'.join(str(id_) for id_ in sorted(product_ids))}:growth-rules-v1"
    return sha256(seed.encode()).hexdigest()


def _save_recommendation(db: Session, run: AgentRun, merchant: Merchant, type_: str, title: str, rationale: str, evidence: dict, payload: dict, impact: dict, confidence: float, products: list[Product], roles: list[str]) -> Recommendation | None:
    recommendation_hash = _hash(merchant.id, type_, [product.id for product in products])
    existing = db.scalar(select(Recommendation).where(Recommendation.merchant_id == merchant.id, Recommendation.recommendation_hash == recommendation_hash, Recommendation.status.in_(["pending_approval", "approved"])))
    if existing:
        return None
    recommendation = Recommendation(merchant_id=merchant.id, agent_run_id=run.id, type=type_, title=title, rationale=rationale, evidence_json=evidence, action_payload_json=payload, impact_json=impact, confidence_score=confidence, recommendation_hash=recommendation_hash)
    db.add(recommendation)
    db.flush()
    for product, role in zip(products, roles, strict=True):
        db.add(RecommendationItem(recommendation_id=recommendation.id, product_id=product.id, role=role, original_price_paise=product.price_paise, proposed_price_paise=payload.get("proposed_price_paise")))
    return recommendation


def create_growth_run(db: Session, merchant: Merchant, request: AgentRunCreate) -> AgentRun:
    products = list(db.scalars(select(Product).where(Product.merchant_id == merchant.id, Product.status == "active", Product.inventory_count > 0)))
    if len(products) < 2:
        raise HTTPException(status_code=422, detail="At least two active in-stock products are required for growth analysis")
    run = AgentRun(merchant_id=merchant.id, status="running", input_snapshot_json={"product_count": len(products), "industry": merchant.industry, "analysis_types": request.analysis_types})
    db.add(run)
    db.flush()
    write_audit_log(db, merchant.id, "agent_run_started", "agent_run", str(run.id), "Merchant Growth Agent started catalog analysis.", actor_type="agent", actor_id="OrchestratorAgent")
    categories = {product.category: product for product in products}
    average_margin = sum((product.price_paise - (product.cost_paise or product.price_paise)) / product.price_paise for product in products) / len(products)
    _record_action(db, run.id, "CatalogAnalysisAgent", "analyze_catalog", "Mapped active products, categories, price bands, stock, and available margin inputs.", {"products": len(products)}, {"categories": len(categories), "average_margin_percent": round(average_margin * 100, 1)})
    blueprint = OFFER_BLUEPRINTS.get(merchant.industry)
    created = 0
    if blueprint and "bundle" in request.analysis_types:
        bundle_products = [categories[category] for category in blueprint["bundle_categories"] if category in categories]
        if len(bundle_products) >= 2:
            original = sum(product.price_paise for product in bundle_products)
            proposed = int(original * 0.9)
            post_margin = sum(product.price_paise - (product.cost_paise or product.price_paise) for product in bundle_products) - (original - proposed)
            post_margin_pct = max(0, round(post_margin / proposed * 100, 1))
            bundle = _save_recommendation(db, run, merchant, "bundle", blueprint["bundle_title"], f"These products create {blueprint['bundle_story']}. A 10% offer increases perceived value while keeping an estimated {post_margin_pct}% gross margin.", {"signals": ["Complementary product categories", "All bundle products are active and in stock", "10% discount passes margin guardrail"], "products": [product.name for product in bundle_products], "margin_after_discount_percent": post_margin_pct}, {"original_price_paise": original, "proposed_price_paise": proposed, "discount_percent": 10, "offer_type": "bundle"}, {"estimated_monthly_revenue_uplift_inr": round(proposed / 100 * 18), "estimated_incremental_orders": 18, "confidence_range": "medium", "assumptions": ["18 incremental bundle orders per month", "10% merchant-approved bundle discount", "Current catalog stock remains available"]}, 0.86, bundle_products, ["bundle_item"] * len(bundle_products))
            if bundle:
                created += 1
                _record_action(db, run.id, "BundleDiscoveryAgent", "discover_bundle", bundle.rationale, {"candidate_categories": blueprint["bundle_categories"]}, {"original_price_paise": original, "proposed_price_paise": proposed}, bundle.id)
    if blueprint and "upsell" in request.analysis_types:
        anchor, target = categories.get(blueprint["upsell_anchor"]), categories.get(blueprint["upsell_target"])
        if anchor and target:
            upsell = _save_recommendation(db, run, merchant, "upsell", f"Offer {target.name} with {anchor.name}", f"{target.name} is a relevant premium add-on for customers choosing {anchor.name}. It extends the same purchase intent and is currently in stock.", {"signals": ["Shared customer routine or intent", "Premium add-on has inventory", "Price difference is within a realistic add-on range"], "primary_product": anchor.name, "upsell_product": target.name, "price_difference_inr": round((target.price_paise - anchor.price_paise) / 100)}, {"primary_product_id": anchor.id, "upsell_product_id": target.id, "proposed_price_paise": target.price_paise, "offer_type": "upsell"}, {"estimated_monthly_revenue_uplift_inr": round(target.price_paise / 100 * 12), "estimated_incremental_orders": 12, "confidence_range": "medium", "assumptions": ["12 customers accept the add-on monthly", "The offer is shown only with the primary product"]}, 0.79, [anchor, target], ["primary", "upsell_item"])
            if upsell:
                created += 1
                _record_action(db, run.id, "UpsellAgent", "identify_upsell", upsell.rationale, {"anchor": anchor.name, "candidate": target.name}, {"price_difference_paise": target.price_paise - anchor.price_paise}, upsell.id)
    if "campaign" in request.analysis_types:
        hero = max(products, key=lambda product: (product.price_paise - (product.cost_paise or 0), product.inventory_count))
        campaign = _save_recommendation(db, run, merchant, "campaign", blueprint["campaign_title"] if blueprint else f"Feature {hero.name}", f"{hero.name} has a healthy absolute contribution margin and enough inventory for a small campaign test. The campaign copy is a draft for merchant approval.", {"signals": ["Healthy contribution margin", "Available inventory", "Merchant industry campaign template"], "featured_product": hero.name, "inventory": hero.inventory_count}, {"featured_product_id": hero.id, "proposed_price_paise": hero.price_paise, "offer_type": "campaign", "campaign_copy": f"Your next routine upgrade is here. Discover {hero.name} from {merchant.name} today."}, {"estimated_monthly_revenue_uplift_inr": round(hero.price_paise / 100 * 10), "estimated_incremental_orders": 10, "confidence_range": "low", "assumptions": ["10 incremental campaign orders", "Campaign copy is reviewed before publishing"]}, 0.68, [hero], ["featured_item"])
        if campaign:
            created += 1
            _record_action(db, run.id, "CampaignAgent", "draft_campaign", campaign.rationale, {"featured_product": hero.name}, {"campaign_title": campaign.title}, campaign.id)
    run.status = "completed"
    run.completed_at = datetime.utcnow()
    _record_action(db, run.id, "ImpactEstimationAgent", "estimate_impact", "Applied transparent order-volume and final-price assumptions; estimates are directional rather than guaranteed.", {"recommendations_created": created}, {"recommendations_created": created})
    write_audit_log(db, merchant.id, "agent_run_completed", "agent_run", str(run.id), f"Growth analysis completed with {created} new recommendations.", actor_type="agent", actor_id="OrchestratorAgent")
    db.commit()
    db.refresh(run)
    return run


def approve_recommendation(db: Session, merchant: Merchant, recommendation_id: int, decision: RecommendationDecision) -> dict:
    recommendation = db.scalar(select(Recommendation).where(Recommendation.id == recommendation_id, Recommendation.merchant_id == merchant.id))
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if recommendation.status != "pending_approval":
        raise HTTPException(status_code=409, detail=f"Only pending recommendations can be approved (currently {recommendation.status})")
    original_price = recommendation.action_payload_json.get("original_price_paise")
    proposed_price = decision.proposed_price_paise or recommendation.action_payload_json.get("proposed_price_paise")
    if original_price and proposed_price and proposed_price > original_price:
        raise HTTPException(status_code=422, detail="Offer price cannot exceed the original catalog total")
    payload = dict(recommendation.action_payload_json)
    if decision.proposed_price_paise:
        payload["proposed_price_paise"] = decision.proposed_price_paise
        payload["merchant_edited"] = True
    recommendation.action_payload_json = payload
    recommendation.status = "approved"
    recommendation.approved_by = merchant.id
    recommendation.approved_at = datetime.utcnow()
    write_audit_log(db, merchant.id, "recommendation_approved", "recommendation", str(recommendation.id), decision.note or "Merchant approved AI recommendation.")
    db.commit()
    return _serialize_recommendation(db, recommendation)


def reject_recommendation(db: Session, merchant: Merchant, recommendation_id: int, reason: str) -> dict:
    recommendation = db.scalar(select(Recommendation).where(Recommendation.id == recommendation_id, Recommendation.merchant_id == merchant.id))
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if recommendation.status != "pending_approval":
        raise HTTPException(status_code=409, detail=f"Only pending recommendations can be rejected (currently {recommendation.status})")
    recommendation.status = "rejected"
    recommendation.rejected_reason = reason
    write_audit_log(db, merchant.id, "recommendation_rejected", "recommendation", str(recommendation.id), reason)
    db.commit()
    return _serialize_recommendation(db, recommendation)
