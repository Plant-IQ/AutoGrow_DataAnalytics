from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

<<<<<<< HEAD
from models import HistoryResponse, HistoryPoint, ErrorResponse
=======
from models import HistoryResponse, HistoryPoint
from db.sqlite import get_session, SensorReading
>>>>>>> bb67116 (feat: add MQTT-driven sensor persistence and UI dashboard)

router = APIRouter()


@router.get(
    "/",
    response_model=HistoryResponse,
    summary="Past week sensor timeline",
<<<<<<< HEAD
    description="Returns a time-series of sensor readings (mocked hourly points for now).",
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {"application/json": {"example": {"detail": "Database unavailable"}}},
        },
    },
=======
    description="Returns a time-series of sensor readings (falls back to mock data if DB is empty).",
>>>>>>> bb67116 (feat: add MQTT-driven sensor persistence and UI dashboard)
)
def get_history(session: Session = Depends(get_session)):
    rows = session.exec(select(SensorReading).order_by(SensorReading.ts.desc()).limit(168)).all()

    if rows:
        pts = [
            HistoryPoint(ts=r.ts, soil=r.soil, temp=r.temp, humidity=r.humidity, light=r.light)
            for r in reversed(rows)
        ]
    else:
        now = datetime.utcnow()
        pts = [
            HistoryPoint(
                ts=now - timedelta(hours=i),
                soil=45 + i * 0.05,
                temp=24 + (i % 5) * 0.1,
                humidity=60 + (i % 4) * 0.2,
                light=280 + (i % 6) * 5,
            )
            for i in range(24)
        ]

    return HistoryResponse(points=pts)
