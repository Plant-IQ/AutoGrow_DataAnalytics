<<<<<<< HEAD
from fastapi import Depends, APIRouter
from sqlmodel import Session, select
from db.sqlite import get_session, Observation
from models import ErrorResponse

router = APIRouter()

@router.post(
    "/observation",
    response_model=Observation,
    summary="Create observation",
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {"application/json": {"example": {"detail": "Database unavailable"}}},
        },
    },
)
def add_observation(obs: Observation, session: Session = Depends(get_session)):
=======
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from db.sqlite import Observation, get_session
from models import ObservationCreate

router = APIRouter()


@router.post("/", response_model=Observation, summary="Add a manual observation")
def add_observation(payload: ObservationCreate, session: Session = Depends(get_session)):
    obs = Observation(**payload.model_dump())
>>>>>>> bb67116 (feat: add MQTT-driven sensor persistence and UI dashboard)
    session.add(obs)
    session.commit()
    session.refresh(obs)
    return obs


@router.get("/", response_model=List[Observation], summary="List recent observations")
def list_observations(
    limit: int = Query(default=20, ge=1, le=200, description="Max number of observations to return."),
    session: Session = Depends(get_session),
):
    records = session.exec(select(Observation).order_by(Observation.created_at.desc()).limit(limit)).all()
    return records
