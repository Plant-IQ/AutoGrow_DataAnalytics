from fastapi import APIRouter

from models import LightResponse

router = APIRouter()


@router.get(
    "/",
    response_model=LightResponse,
    summary="Light spectrum recommendation",
    description="Returns the recommended spectrum/preset and light hours accumulated today (mock data).",
)
def get_light():
    return LightResponse(spectrum="veg", hours_today=12.0)
