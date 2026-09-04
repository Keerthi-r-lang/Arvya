from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_merchant
from app.db.models.merchant import Merchant
from app.db.session import get_db
from app.schemas.decision_center import CommerceSimulationResponse, DecisionCenterResponse
from app.services.decision_center_service import build_decision_center, run_commerce_simulation

router = APIRouter(tags=["ai-decision-center"])


@router.get("/decision-center", response_model=DecisionCenterResponse)
def decision_center(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return build_decision_center(db, merchant)


@router.post("/commerce-simulations", response_model=CommerceSimulationResponse, status_code=201)
def commerce_simulation(merchant: Merchant = Depends(get_current_merchant), db: Session = Depends(get_db)):
    return run_commerce_simulation(db, merchant)
