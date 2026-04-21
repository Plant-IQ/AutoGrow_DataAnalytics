from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

# Import everything from db.sqlite that this router needs
from db.sqlite import AutogrowReading, PlantInstance, engine, get_mysql_session
from models import HistoryResponse, HistoryPoint

router = APIRouter()

@router.get("/", response_model=HistoryResponse)
def get_history(
    until_stage: str | None = Query(None),
    session: Session = Depends(get_mysql_session),
):
    # Return empty data when there is no active plant to avoid showing old session records
    with Session(engine) as sqlite_session:
        active = sqlite_session.exec(
            select(PlantInstance)
            .where(PlantInstance.is_active == True)  # noqa: E712
            .order_by(PlantInstance.started_at.desc())
            .limit(1)
        ).first()
    if not active:
        return HistoryResponse(points=[])

    # Read data from MySQL (Autogrow table)
    statement = (
        select(AutogrowReading)
        .where(AutogrowReading.ts >= active.started_at)
        .order_by(AutogrowReading.ts.desc())
        .limit(168)
    )
    results = session.exec(statement).all()

    if not results:
        return HistoryResponse(points=[])

    rows = list(results)

    # Filter data by stage (if requested)
    if until_stage:
        normalized_stage = until_stage.strip().lower()
        cutoff_idx = None
        for i, row in enumerate(rows):
            if (row.stage_name or "").strip().lower() == normalized_stage:
                cutoff_idx = i
                break
        
        if cutoff_idx is not None:
            rows = rows[cutoff_idx:]

    pts = [
        HistoryPoint(
            ts=r.ts,
            soil=r.soil_pct,
            temp=r.temp1,
            humidity=r.humidity,
            light=r.light_lux,
            stage=r.stage,
            stage_name=r.stage_name,
            spectrum=r.spectrum,
            pump_on=bool(r.pump_on)
        )
        for r in rows
    ]

    return HistoryResponse(points=pts)
