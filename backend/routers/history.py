from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

# ดึงทุกอย่างมาจาก db.sqlite ที่เราเตรียมไว้แล้ว
from db.sqlite import AutogrowReading, PlantInstance, engine, get_mysql_session
from models import HistoryResponse, HistoryPoint

router = APIRouter()

@router.get("/", response_model=HistoryResponse)
def get_history(
    until_stage: str | None = Query(None),
    session: Session = Depends(get_mysql_session),
):
    # คืนค่าว่างเมื่อไม่มี active plant เพื่อไม่ให้ข้อมูล session เก่าปรากฏ
    with Session(engine) as sqlite_session:
        active = sqlite_session.exec(
            select(PlantInstance)
            .where(PlantInstance.is_active == True)  # noqa: E712
            .order_by(PlantInstance.started_at.desc())
            .limit(1)
        ).first()
    if not active:
        return HistoryResponse(points=[])

    # ดึงข้อมูลจาก MySQL (Autogrow Table)
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

    # กรองข้อมูลตาม Stage (ถ้ามี)
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
