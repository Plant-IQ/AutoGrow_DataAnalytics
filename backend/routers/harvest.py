from datetime import datetime, timedelta

from fastapi import APIRouter

from models import HarvestETAResponse, ErrorResponse

router = APIRouter()


@router.get(
    "/",
    response_model=HarvestETAResponse,
    summary="Estimated days to harvest",
    description="Simple linear projection based on current growth data. Mocked until trained on real observations.",
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {"application/json": {"example": {"detail": "Database unavailable"}}},
        },
    },
)

def get_harvest_eta():
    days = 18
    return HarvestETAResponse(
        days_to_harvest=days,
        projected_date=datetime.utcnow() + timedelta(days=days),
    )
