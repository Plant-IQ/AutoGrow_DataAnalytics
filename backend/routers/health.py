from fastapi import APIRouter

from models import HealthResponse

router = APIRouter()


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Plant Health Score",
    description="Aggregated 0–100 score combining soil moisture, temperature, humidity, and light compliance. Mocked values until live data arrives.",
)
def get_health():
    return HealthResponse(score=82.5, components={"soil": 0.8, "temp": 0.9, "humidity": 0.85, "light": 0.75})
