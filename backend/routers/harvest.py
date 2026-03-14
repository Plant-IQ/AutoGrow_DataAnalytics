from datetime import datetime, timedelta

from fastapi import APIRouter

from models import HarvestETAResponse

router = APIRouter()


@router.get(
    "/",
    response_model=HarvestETAResponse,
    summary="Estimated days to harvest",
    description="Simple linear projection based on current growth data. Mocked until trained on real observations.",
)
def get_harvest_eta():
    days = 18
    return HarvestETAResponse(
        days_to_harvest=days,
        projected_date=datetime.utcnow() + timedelta(days=days),
    )
