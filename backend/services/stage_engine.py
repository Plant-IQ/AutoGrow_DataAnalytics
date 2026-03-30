"""Stage lookup helper.

Keeps the stage logic in one place so routers stay thin. Today we simply read
the most recent GrowthStage row and default to Vegetative when none exists.
"""

from datetime import datetime
from typing import Tuple

from sqlmodel import Session, select

from db.sqlite import GrowthStage


DEFAULT_STAGE = (2, "Vegetative")  # index, name


def get_current_stage(session: Session) -> Tuple[int, str, int]:
    """Return (index, name, days_in_stage)."""
    result = session.exec(select(GrowthStage).order_by(GrowthStage.started_at.desc()).limit(1)).first()

    if result is None:
        stage_index, stage_name = DEFAULT_STAGE
        started_at = datetime.utcnow()
    else:
        stage_index, stage_name, started_at = result.stage_index, result.stage_name, result.started_at

    days_in_stage = max(1, (datetime.utcnow() - started_at).days + 1)
    return stage_index, stage_name, days_in_stage


def upsert_stage(session: Session, stage_index: int, stage_name: str):
    existing = session.exec(select(GrowthStage).order_by(GrowthStage.started_at.desc()).limit(1)).first()
    now = datetime.utcnow()
    if existing:
        existing.stage_index = stage_index
        existing.stage_name = stage_name
        existing.started_at = now
        session.add(existing)
    else:
        session.add(GrowthStage(stage_index=stage_index, stage_name=stage_name, started_at=now))
    session.commit()
