from fastapi import APIRouter, Depends
<<<<<<< HEAD
from sqlmodel import Session

from db.sqlite import get_session
from models import HealthResponse, ErrorResponse
from services.repo import latest_sensor, latest_stage

=======
from sqlmodel import Session, select

from models import HealthResponse
from db.sqlite import get_session, SensorReading
from services.health_score import compute_health
>>>>>>> bb67116 (feat: add MQTT-driven sensor persistence and UI dashboard)

router = APIRouter()


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Plant Health Score",
<<<<<<< HEAD
    description="Aggregated 0–100 score combining soil moisture, temperature, humidity, and light compliance. Mocked values until live data arrives.",
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {"application/json": {"example": {"detail": "Database unavailable"}}},
        },
    },
)
def get_health(session: Session = Depends(get_session)):
    sensor = latest_sensor(session)
    stage = latest_stage(session)

    score = 82.5
    components = {"soil": 0.8, "temp": 0.9, "humidity": 0.85, "light": 0.75}

    if sensor:
        components["light"] = min(1.0, sensor.lux / 1000) if hasattr(sensor, "lux") else components["light"]

    if stage:
        score = min(100.0, score + (stage.stage * 1.5))

=======
    description="Aggregated 0–100 score combining soil moisture, temperature, humidity, and light compliance.",
)
def get_health(session: Session = Depends(get_session)):
    latest = session.exec(select(SensorReading).order_by(SensorReading.ts.desc()).limit(1)).first()
    score, components = compute_health(latest)
>>>>>>> bb67116 (feat: add MQTT-driven sensor persistence and UI dashboard)
    return HealthResponse(score=score, components=components)
