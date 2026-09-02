from datetime import datetime

from pydantic import BaseModel, Field


class AgentRunCreate(BaseModel):
    analysis_types: list[str] = Field(default_factory=lambda: ["bundle", "upsell", "campaign"])
    max_recommendations: int = Field(default=3, ge=1, le=5)


class AgentRunResponse(BaseModel):
    id: int
    merchant_id: int
    status: str
    trigger_type: str
    model_provider: str
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class RecommendationItemResponse(BaseModel):
    product_id: int
    role: str
    original_price_paise: int
    proposed_price_paise: int | None
    quantity: int

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    id: int
    agent_run_id: int
    type: str
    status: str
    title: str
    rationale: str
    evidence_json: dict
    action_payload_json: dict
    impact_json: dict
    confidence_score: float
    approved_at: datetime | None
    rejected_reason: str | None
    created_at: datetime
    items: list[RecommendationItemResponse] = Field(default_factory=list)


class RecommendationDecision(BaseModel):
    proposed_price_paise: int | None = Field(default=None, gt=0)
    note: str | None = Field(default=None, max_length=500)


class RecommendationRejection(BaseModel):
    reason: str = Field(min_length=2, max_length=500)


class AgentActionResponse(BaseModel):
    id: int
    agent_run_id: int
    recommendation_id: int | None
    agent_name: str
    action_type: str
    status: str
    input_summary_json: dict
    output_summary_json: dict
    tools_used_json: list
    reasoning_summary: str
    started_at: datetime
    completed_at: datetime

    model_config = {"from_attributes": True}
