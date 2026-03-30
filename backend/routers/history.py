from datetime import datetime, timedelta

from fastapi import APIRouter

from models import HistoryResponse, HistoryPoint, ErrorResponse

router = APIRouter()


@router.get(
    "/",
    response_model=HistoryResponse,
    summary="Past week sensor timeline",
    description="Returns a time-series of sensor readings (mocked hourly points for now).",
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {"application/json": {"example": {"detail": "Database unavailable"}}},
        },
    },
)
def get_history():
    now = datetime.utcnow()
    pts = [
        HistoryPoint(
            ts=now - timedelta(hours=i),
            soil=40 + i * 0.1,
            temp=24,
            humidity=60,
            light=300,
        )
        for i in range(24)
    ]
    return HistoryResponse(points=pts)
