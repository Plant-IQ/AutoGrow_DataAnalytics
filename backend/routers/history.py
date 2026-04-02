from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from models import HistoryResponse, HistoryPoint
from db.sqlite import get_session, SensorReading

router = APIRouter()


@router.get(
    "/",
    response_model=HistoryResponse,
    summary="Past week sensor timeline",
    description="Returns a time-series of sensor readings (falls back to mock data if DB is empty).",
)
def get_history(session: Session = Depends(get_session)):
    """Return up-to-date timeline; fall back to fresh mock data when readings are stale.

    We treat DB data older than 10 minutes as stale so the UI doesn't pin to a single
    timestamp (e.g., all points at 03:13 AM). In that case we generate a short mock
    series anchored to `now`, which keeps the chart time axis looking correct when
    no live sensor stream is running.
    """

    now = datetime.utcnow()
    rows = session.exec(select(SensorReading).order_by(SensorReading.ts.desc()).limit(168)).all()

    use_mock = not rows
    if rows:
        newest = rows[0].ts
        if (now - newest) > timedelta(minutes=10):
            use_mock = True

    if use_mock:
        # 24 points, 5‑minute spacing, gentle variation
        pts = [
            HistoryPoint(
                ts=now - timedelta(minutes=5 * (23 - i)),
                soil=45 + (i % 5) * 0.6,
                temp=24 + (i % 6) * 0.3,
                humidity=55 + (i % 7) * 1.1,
                light=220 + (i % 8) * 20,
            )
            for i in range(24)
        ]
    else:
        pts = [
            HistoryPoint(ts=r.ts, soil=r.soil, temp=r.temp, humidity=r.humidity, light=r.light)
            for r in reversed(rows)
        ]

    return HistoryResponse(points=pts)
