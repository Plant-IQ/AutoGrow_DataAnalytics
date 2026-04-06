from fastapi import APIRouter, Depends
from sqlmodel import Session

from models import StageResponse, StageUpdate
from db.sqlite import get_session
from services.stage_engine import get_current_stage, upsert_stage

router = APIRouter()


@router.get(
    "/",
    response_model=StageResponse,
    summary="Current growth stage",
    description="Returns current stage index/name and days elapsed in stage.",
)
def get_stage(session: Session = Depends(get_session)):
    idx, name, days = get_current_stage(session)
    return StageResponse(stage=idx, label=name, days_in_stage=days)


@router.post(
    "/set",
    response_model=StageResponse,
    summary="Set current growth stage",
    description="Manually set the current stage index and label; resets days_in_stage to 1.",
)
def set_stage(payload: StageUpdate, session: Session = Depends(get_session)):
    upsert_stage(session, payload.stage, payload.label)
    idx, name, days = get_current_stage(session)
    return StageResponse(stage=idx, label=name, days_in_stage=days)


@router.post(
    "/reset",
    response_model=StageResponse,
    summary="Reset to seed stage",
    description="Convenience endpoint to start a new grow cycle at stage 0 (Seed).",
)
def reset_stage(session: Session = Depends(get_session)):
    upsert_stage(session, 0, "Seed")
    idx, name, days = get_current_stage(session)
    return StageResponse(stage=idx, label=name, days_in_stage=days)
