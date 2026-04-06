# from datetime import datetime, timedelta

# from fastapi import APIRouter

# from models import HarvestETAResponse, ErrorResponse

# router = APIRouter()


# @router.get(
#     "/",
#     response_model=HarvestETAResponse,
#     summary="Estimated days to harvest",
#     description="Simple linear projection based on current growth data. Mocked until trained on real observations.",
#     responses={
#         422: {"model": ErrorResponse, "description": "Validation error"},
#         500: {
#             "model": ErrorResponse,
#             "description": "Internal server error",
#             "content": {"application/json": {"example": {"detail": "Database unavailable"}}},
#         },
#     },
# )

# def get_harvest_eta():
#     days = 18
#     return HarvestETAResponse(
#         days_to_harvest=days,
#         projected_date=datetime.utcnow() + timedelta(days=days),
#     )

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from models import HarvestETAResponse, ErrorResponse
from db.sqlite import get_session, SensorReading

router = APIRouter()

@router.get("/", response_model=HarvestETAResponse)
def get_harvest_eta(session: Session = Depends(get_session)):
    latest = session.exec(select(SensorReading).order_by(SensorReading.ts.desc()).limit(1)).first()
    days = latest.harvest_eta_days if latest and latest.harvest_eta_days else 35
    return HarvestETAResponse(
        days_to_harvest=days,
        projected_date=datetime.utcnow() + timedelta(days=days),
    )