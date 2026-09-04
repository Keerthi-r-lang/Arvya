from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.agent_action import AgentAction
from app.db.models.audit_log import AuditLog
from app.db.models.coupon import Coupon
from app.db.models.merchant import Merchant
from app.db.models.product import Product
from app.db.models.recommendation import Recommendation
from app.db.models.recommendation_item import RecommendationItem
from app.services.audit_service import write_audit_log
from app.services.shopping_service import _best_coupon, _discount


def _selected_recommendation(db: Session, merchant_id: int) -> Recommendation:
    recommendations = list(db.scalars(select(Recommendation).where(Recommendation.merchant_id == merchant_id).order_by(Recommendation.created_at.desc())))
    recommendation = next((item for item in recommendations if item.status == "approved"), None) or next((item for item in recommendations if item.status == "pending_approval"), None)
    if recommendation is None:
        raise HTTPException(status_code=422, detail="Generate a merchant recommendation before opening the AI Decision Center")
    return recommendation


def _risk_level(score: int) -> str:
    return "low" if score <= 25 else "medium" if score <= 55 else "high"


def _audit_references(db: Session, merchant_id: int, recommendation: Recommendation) -> list[dict]:
    events = list(db.scalars(select(AuditLog).where(AuditLog.merchant_id == merchant_id).order_by(AuditLog.created_at.desc()).limit(20)))
    relevant = [event for event in events if event.entity_id in {str(recommendation.id), str(recommendation.agent_run_id)}]
    selected = (relevant or events)[:6]
    return [{"id": event.id, "event_type": event.event_type, "detail": event.detail, "created_at": event.created_at} for event in selected]


def build_decision_center(db: Session, merchant: Merchant) -> dict:
    recommendation = _selected_recommendation(db, merchant.id)
    item_rows = list(db.scalars(select(RecommendationItem).where(RecommendationItem.recommendation_id == recommendation.id)))
    product_ids = [item.product_id for item in item_rows]
    products = list(db.scalars(select(Product).where(Product.id.in_(product_ids)))) if product_ids else []
    payload = recommendation.action_payload_json or {}
    original_price = payload.get("original_price_paise") or sum(product.price_paise for product in products)
    offer_price = payload.get("proposed_price_paise") or original_price
    coupon = _best_coupon(db, merchant.id, offer_price)
    coupon_discount = _discount(coupon, offer_price)
    final_price = offer_price - coupon_discount
    known_costs = [product.cost_paise for product in products if product.cost_paise is not None]
    cost_total = sum(known_costs)
    margin_after = round(((final_price - cost_total) / final_price) * 100, 1) if products and len(known_costs) == len(products) and final_price else None
    minimum_inventory = min((product.inventory_count for product in products), default=0)

    intent_score = 92 if recommendation.type == "bundle" else 84 if recommendation.type == "upsell" else 74
    margin_score = 50 if margin_after is None else max(0, min(100, round(margin_after * 2)))
    inventory_score = 100 if minimum_inventory >= 30 else 82 if minimum_inventory >= 10 else 40 if minimum_inventory > 0 else 0
    coupon_score = 100 if coupon else 65
    data_score = round((len(known_costs) / len(products)) * 100) if products else 0
    components = [
        {"label": "Intent relevance", "score": intent_score, "weight": 35, "detail": "Offer type and catalog categories align with the buyer journey."},
        {"label": "Margin safety", "score": margin_score, "weight": 25, "detail": f"Post-discount margin is {margin_after}%" if margin_after is not None else "Cost data is incomplete; merchant review is required."},
        {"label": "Inventory confidence", "score": inventory_score, "weight": 20, "detail": f"Lowest included inventory is {minimum_inventory} units."},
        {"label": "Coupon eligibility", "score": coupon_score, "weight": 10, "detail": f"{coupon.code} is eligible for this offer." if coupon else "No eligible coupon changes the final price."},
        {"label": "Catalog data quality", "score": data_score, "weight": 10, "detail": f"{len(known_costs)}/{len(products)} included products have cost data."},
    ]
    confidence = round(sum(component["score"] * component["weight"] for component in components) / 100)
    risk_score = 0
    risk_reasons: list[str] = []
    if recommendation.status != "approved":
        risk_score += 45
        risk_reasons.append("Merchant approval is still required before any live payment action.")
    if margin_after is None:
        risk_score += 25
        risk_reasons.append("Missing cost data prevents a complete margin calculation.")
    elif margin_after < 25:
        risk_score += 45
        risk_reasons.append(f"Post-discount margin ({margin_after}%) is below the 25% commercial guardrail.")
    if minimum_inventory <= 0:
        risk_score += 35
        risk_reasons.append("At least one included product is out of stock.")
    elif minimum_inventory < 10:
        risk_score += 20
        risk_reasons.append(f"Low inventory warning: only {minimum_inventory} units remain for one included product.")
    if not risk_reasons:
        risk_reasons.append("No blocking commercial guardrail is currently triggered.")
    risk_score = min(risk_score, 100)
    guardrails = [
        {"name": "Merchant approval gate", "status": "passed" if recommendation.status == "approved" else "blocked", "detail": "Merchant approval is required before creating a live payment link."},
        {"name": "Margin protection", "status": "passed" if margin_after is not None and margin_after >= 25 else "review", "detail": f"{margin_after}% margin after discount." if margin_after is not None else "Cost data is missing."},
        {"name": "Inventory protection", "status": "passed" if minimum_inventory >= 10 else "review", "detail": f"Minimum included inventory: {minimum_inventory} units."},
        {"name": "Coupon validation", "status": "passed" if coupon else "neutral", "detail": f"{coupon.code} reduces the payable amount by ₹{coupon_discount / 100:.0f}." if coupon else "No eligible coupon was applied."},
    ]
    signals = list((recommendation.evidence_json or {}).get("signals", []))
    why_selected = signals + [
        f"Final payable price is ₹{final_price / 100:.0f} after governed coupon validation.",
        "The offer stays within merchant-controlled pricing and approval boundaries.",
    ]
    why_rejected = [
        "Candidates that drop post-discount margin below 25% are blocked by policy.",
        "Candidates containing out-of-stock products are removed before checkout.",
        "Offers without merchant approval cannot create a live Razorpay Payment Link.",
    ]
    actions = list(db.scalars(select(AgentAction).where(AgentAction.agent_run_id == recommendation.agent_run_id).order_by(AgentAction.started_at)))
    trace = [{"step": index + 1, "title": action.agent_name.replace("Agent", " Agent"), "detail": action.reasoning_summary, "actor": action.agent_name, "status": action.status} for index, action in enumerate(actions)]
    trace.append({"step": len(trace) + 1, "title": "Approval gate", "detail": "Merchant approval recorded; offer is eligible for customer checkout." if recommendation.status == "approved" else "Offer is held until the merchant explicitly approves it.", "actor": "Merchant", "status": "completed" if recommendation.status == "approved" else "awaiting_approval"})
    impact = recommendation.impact_json or {}
    return {
        "recommendation_id": recommendation.id,
        "title": recommendation.title,
        "recommendation_type": recommendation.type,
        "approval_status": recommendation.status,
        "confidence_score": confidence,
        "confidence_formula": "35% intent relevance + 25% margin safety + 20% inventory confidence + 10% coupon eligibility + 10% catalog data quality",
        "confidence_components": components,
        "risk_score": risk_score,
        "risk_level": _risk_level(risk_score),
        "risk_reasons": risk_reasons,
        "guardrails": guardrails,
        "why_selected": why_selected,
        "why_rejected": why_rejected,
        "evidence_sources": ["Catalog price and cost snapshot", "Live inventory counts", "Merchant coupon rules", "Merchant approval record", "Recorded agent actions"],
        "original_price_paise": original_price,
        "offer_price_paise": offer_price,
        "coupon_code": coupon.code if coupon else None,
        "coupon_discount_paise": coupon_discount,
        "final_price_paise": final_price,
        "margin_after_discount_percent": margin_after,
        "expected_monthly_uplift_inr": impact.get("estimated_monthly_revenue_uplift_inr", 0),
        "expected_incremental_orders": impact.get("estimated_incremental_orders", 0),
        "assumptions": impact.get("assumptions", []),
        "decision_trace": trace,
        "audit_references": _audit_references(db, merchant.id, recommendation),
    }


def run_commerce_simulation(db: Session, merchant: Merchant) -> dict:
    decision = build_decision_center(db, merchant)
    simulation_id = f"sim-{uuid4().hex[:8]}"
    start = write_audit_log(db, merchant.id, "commerce_simulation_started", "commerce_simulation", simulation_id, "Started a governed demo simulation. No live payment action will be created.", actor_type="system", actor_id="CommerceSimulation")
    db.flush()
    approved = decision["approval_status"] == "approved"
    events = [
        {"step": 1, "title": "Customer intent received", "detail": "Buyer Agent receives a budget-aware commerce request.", "actor": "Buyer Agent", "status": "completed"},
        {"step": 2, "title": "Buyer Agent activated", "detail": "Search is constrained to merchant-approved, governed offers.", "actor": "Buyer Agent", "status": "completed"},
        {"step": 3, "title": "Catalog analysis", "detail": "Catalog prices, costs, product availability, and categories are evaluated.", "actor": "Catalog Analysis Agent", "status": "completed"},
        {"step": 4, "title": "Offer discovery", "detail": f"Selected {decision['title']} as the best governed offer candidate.", "actor": "Offer Discovery Agent", "status": "completed"},
        {"step": 5, "title": "Merchant Agent evaluation", "detail": "Commercial evidence and expected impact are prepared for merchant review.", "actor": "Merchant Growth Agent", "status": "completed"},
        {"step": 6, "title": "Bundle opportunity found", "detail": "Complementary products are combined into a merchant-controlled offer.", "actor": "Bundle Discovery Agent", "status": "completed"},
        {"step": 7, "title": "Coupon applied", "detail": f"{decision['coupon_code'] or 'No eligible coupon'} is reflected in the payable amount.", "actor": "Coupon Validation Agent", "status": "completed"},
        {"step": 8, "title": "Risk check", "detail": f"Risk score: {decision['risk_score']}/100 ({decision['risk_level']}).", "actor": "Risk Engine", "status": "completed"},
        {"step": 9, "title": "Approval gate", "detail": "Merchant approval is recorded." if approved else "Simulation stops here until a merchant approves the offer.", "actor": "Merchant", "status": "completed" if approved else "awaiting_approval"},
        {"step": 10, "title": "Payment link generated", "detail": "Simulated payment link only — no Razorpay API request was sent.", "actor": "Razorpay Payment Agent", "status": "simulated" if approved else "not_started"},
        {"step": 11, "title": "Payment completed", "detail": "Simulated Test Mode completion only — no money was collected.", "actor": "Razorpay", "status": "simulated" if approved else "not_started"},
        {"step": 12, "title": "Revenue recorded", "detail": "Simulation-only revenue outcome displayed; production revenue requires a signed Razorpay webhook.", "actor": "Revenue Ledger", "status": "simulated" if approved else "not_started"},
        {"step": 13, "title": "Audit ledger updated", "detail": "Simulation execution is written to the audit ledger.", "actor": "Audit Agent", "status": "completed"},
    ]
    complete = write_audit_log(db, merchant.id, "commerce_simulation_completed", "commerce_simulation", simulation_id, f"Completed governed simulation for recommendation #{decision['recommendation_id']}. Simulated payment only; no live Razorpay action was attempted.", actor_type="system", actor_id="CommerceSimulation")
    db.commit()
    references = [{"id": start.id, "event_type": start.event_type, "detail": start.detail, "created_at": start.created_at}, {"id": complete.id, "event_type": complete.event_type, "detail": complete.detail, "created_at": complete.created_at}]
    return {"simulation_id": simulation_id, "mode": "safe_demo", "safety_notice": "This is a governed demonstration. It never creates a Razorpay payment link, captures money, or changes revenue metrics.", "decision": decision, "events": events, "audit_references": references}
