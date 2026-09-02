from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_merchant
from app.db.models.agent_action import AgentAction
from app.db.models.agent_run import AgentRun
from app.db.models.merchant import Merchant
from app.db.session import get_db
from app.schemas.recommendation import AgentActionResponse, AgentRunCreate, AgentRunResponse, RecommendationDecision, RecommendationRejection, RecommendationResponse
from app.services.recommendation_service import approve_recommendation, create_growth_run, get_recommendation, list_recommendations, reject_recommendation

router = APIRouter(tags=["growth-agent"])


@router.post("/agent-runs", response_model=AgentRunResponse, status_code=201)
def start_agent_run(payload: AgentRunCreate, merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return create_growth_run(db, merchant, payload)


@router.get("/agent-runs/{run_id}", response_model=AgentRunResponse)
def get_agent_run(run_id: int, merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    run = db.scalar(select(AgentRun).where(AgentRun.id == run_id, AgentRun.merchant_id == merchant.id))
    if run is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Agent run not found")
    return run


@router.get("/recommendations", response_model=list[RecommendationResponse])
def recommendations(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return list_recommendations(db, merchant.id)


@router.get("/recommendations/{recommendation_id}", response_model=RecommendationResponse)
def recommendation_detail(recommendation_id: int, merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return get_recommendation(db, merchant.id, recommendation_id)


@router.post("/recommendations/{recommendation_id}/approve", response_model=RecommendationResponse)
def approve(recommendation_id: int, payload: RecommendationDecision, merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return approve_recommendation(db, merchant, recommendation_id, payload)


@router.post("/recommendations/{recommendation_id}/reject", response_model=RecommendationResponse)
def reject(recommendation_id: int, payload: RecommendationRejection, merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return reject_recommendation(db, merchant, recommendation_id, payload.reason)


@router.get("/agent-actions", response_model=list[AgentActionResponse])
def agent_actions(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    owned_runs = select(AgentRun.id).where(AgentRun.merchant_id == merchant.id)
    return list(db.scalars(select(AgentAction).where(AgentAction.agent_run_id.in_(owned_runs)).order_by(AgentAction.created_at.desc() if hasattr(AgentAction, "created_at") else AgentAction.started_at.desc())))
