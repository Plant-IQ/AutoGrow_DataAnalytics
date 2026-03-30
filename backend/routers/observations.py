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
    session.add(obs)
    session.commit()
    session.refresh(obs)
    return obs