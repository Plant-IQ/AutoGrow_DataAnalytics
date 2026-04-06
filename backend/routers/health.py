from fastapi import APIRouter
from models import HealthResponse
from services.health_score import compute_health

router = APIRouter()


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Plant Health Score",
    description="Aggregated 0–100 score combining soil moisture, temperature, humidity, and light compliance.",
)
def get_health():
    score, components = compute_health(None)
    return HealthResponse(score=score, components=components)
