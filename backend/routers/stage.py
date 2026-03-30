from fastapi import APIRouter, Depends
from sqlmodel import Session
from db.sqlite import get_session
from models import StageResponse, ErrorResponse
from services.repo import latest_stage

router = APIRouter()


@router.get(
    "/",
    response_model=StageResponse,
    summary="Current growth stage",
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
