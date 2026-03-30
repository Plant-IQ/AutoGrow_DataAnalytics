from fastapi import APIRouter, Depends
from sqlmodel import Session
<<<<<<< HEAD
from db.sqlite import get_session
from models import StageResponse, ErrorResponse
from services.repo import latest_stage
=======

from models import StageResponse
from db.sqlite import get_session
from services.stage_engine import get_current_stage
>>>>>>> bb67116 (feat: add MQTT-driven sensor persistence and UI dashboard)

router = APIRouter()


@router.get(
    "/",
    response_model=StageResponse,
    summary="Current growth stage",
<<<<<<< HEAD
    description="Returns current stage index/name and days elapsed in stage (mocked until live logic is wired).",
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {"application/json": {"example": {"detail": "Database unavailable"}}},
        },
    },
)
def get_stage(session: Session = Depends(get_session)):
    stage = latest_stage(session)
    if not stage:
        return StageResponse(stage=1, label="Seedling", days_in_stage=0)
    return StageResponse(stage=stage.stage, label=stage.label, days_in_stage=stage.days_in_stage)
=======
    description="Returns current stage index/name and days elapsed in stage.",
)
def get_stage(session: Session = Depends(get_session)):
    idx, name, days = get_current_stage(session)
    return StageResponse(stage=idx, label=name, days_in_stage=days)
>>>>>>> bb67116 (feat: add MQTT-driven sensor persistence and UI dashboard)
