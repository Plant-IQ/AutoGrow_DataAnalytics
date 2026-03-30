from datetime import datetime, timedelta
from sqlmodel import Session, select
from db.sqlite import Observation, SensorReading, GrowthStage

def latest_sensor(session: Session) -> SensorReading | None:
    stmt = select(SensorReading).order_by(SensorReading.ts.desc()).limit(1)
    return session.exec(stmt).first()

def recent_sensors(session: Session, hours: int = 24) -> list[SensorReading]:
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    stmt = select(SensorReading).where(SensorReading.ts >= cutoff).order_by(SensorReading.ts.desc())
    return list(session.exec(stmt))

def latest_stage(session: Session) -> GrowthStage | None:
    stmt = select(GrowthStage).order_by(GrowthStage.started_at.desc()).limit(1)
    return session.exec(stmt).first()

def last_observation(session: Session) -> Observation | None:
    stmt = select(Observation).order_by(Observation.created_at.desc()).limit(1)
    return session.exec(stmt).first()