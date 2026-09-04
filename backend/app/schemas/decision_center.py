from datetime import datetime

from pydantic import BaseModel


class ScoreComponent(BaseModel):
    label: str
    score: int
    weight: int
    detail: str


class DecisionEvent(BaseModel):
    step: int
    title: str
    detail: str
    actor: str
    status: str


class AuditReference(BaseModel):
    id: int
    event_type: str
    detail: str
    created_at: datetime


class DecisionCenterResponse(BaseModel):
    recommendation_id: int
    title: str
    recommendation_type: str
    approval_status: str
    confidence_score: int
    confidence_formula: str
    confidence_components: list[ScoreComponent]
    risk_score: int
    risk_level: str
    risk_reasons: list[str]
    guardrails: list[dict]
    why_selected: list[str]
    why_rejected: list[str]
    evidence_sources: list[str]
    original_price_paise: int
    offer_price_paise: int
    coupon_code: str | None
    coupon_discount_paise: int
    final_price_paise: int
    margin_after_discount_percent: float | None
    expected_monthly_uplift_inr: int
    expected_incremental_orders: int
    assumptions: list[str]
    decision_trace: list[DecisionEvent]
    audit_references: list[AuditReference]


class CommerceSimulationResponse(BaseModel):
    simulation_id: str
    mode: str
    safety_notice: str
    decision: DecisionCenterResponse
    events: list[DecisionEvent]
    audit_references: list[AuditReference]
