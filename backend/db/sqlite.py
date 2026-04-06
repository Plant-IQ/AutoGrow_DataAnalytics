import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import Column, JSON
from sqlmodel import Field, Session, SQLModel, create_engine, select

from datetime import datetime, timezone, timedelta

ICT = timezone(timedelta(hours=7))

load_dotenv()

# Make DB path stable no matter the working directory (defaults to backend/autogrow.db)
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("SQLITE_PATH", BASE_DIR / "autogrow.db"))
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


class Observation(SQLModel, table=True):
    """Manual observation log (entered by user)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    height_cm: float
    leaf_count: int
    root_visible: bool
    canopy_score: int


class SensorReading(SQLModel, table=True):
    """Time-series of sensor data; can be downsampled later."""

    id: Optional[int] = Field(default=None, primary_key=True)
    ts: datetime = Field(default_factory=lambda: datetime.now(ICT), index=True)
    soil: float
    temp: float
    humidity: float
    light: float
    # ── field ใหม่จาก ESP32 ──
    stage: int = Field(default=0)
    stage_name: str = Field(default="")
    spectrum: str = Field(default="")
    pump_on: bool = Field(default=False)
    pump_status: str = Field(default="")
    light_hrs_today: float = Field(default=0.0)
    harvest_eta_days: int = Field(default=0)
    health_score: int = Field(default=0)



class GrowthStage(SQLModel, table=True):
    """Tracks current stage and confirmation flag."""

    id: Optional[int] = Field(default=None, primary_key=True)
    stage_index: int
    stage_name: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed: bool = False


class WeatherCache(SQLModel, table=True):
    """Cache for external API payloads to avoid rate limits."""

    key: str = Field(primary_key=True)
    ts: datetime = Field(default_factory=datetime.utcnow, index=True)
    payload: str  # store raw JSON string


class PlantType(SQLModel, table=True):
    """Type of plant being grown."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    stage_durations_days: list[int] = Field(sa_column=Column(JSON))
    stage_colors: list[str] = Field(sa_column=Column(JSON)) # hex strings


class PlantInstance(SQLModel, table=True):
    """Instance of a plant type, e.g. 'Cucumber 1'."""

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str
    plant_type_id: int = Field(foreign_key="planttype.id")
    current_stage_index: int = 0
    stage_started_at: datetime = Field(default_factory=datetime.utcnow)
    pending_confirm: bool = False 


def init_db() -> None:
    """Create DB file/directories and ensure all tables exist."""

    # Make sure directory exists if DB_PATH points to a nested folder
    db_file = Path(DB_PATH)
    if db_file.parent and not db_file.parent.exists():
        db_file.parent.mkdir(parents=True, exist_ok=True)

    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency yielding a SQLModel session."""

    with Session(engine) as session:
        yield session


def record_sensor(field: str, value: float) -> None:
    """Store a sensor reading, carrying forward last known values for other fields.

    This lets us persist single-sensor MQTT updates into the wide SensorReading table
    without needing all metrics at once.
    """

    with Session(engine) as session:
        last = session.exec(select(SensorReading).order_by(SensorReading.ts.desc()).limit(1)).first()

        # Carry forward previous values so history/health stay smooth
        base = {
            "soil": last.soil if last else value,
            "temp": last.temp if last else value,
            "humidity": last.humidity if last else value,
            "light": last.light if last else value,
        }
        if field in base:
            base[field] = value

        row = SensorReading(**base)
        session.add(row)
        session.commit()


def record_sensor_combined(
    soil: float,
    temp: float,
    humidity: float,
    light: float,
    stage: int = 0,
    stage_name: str = "",
    spectrum: str = "",
    pump_on: bool = False,
    pump_status: str = "",
    light_hrs_today: float = 0.0,
    harvest_eta_days: int = 0,
    health_score: int = 0,
) -> None:
    """Store a complete sensor reading from combined ESP32 payload."""
    with Session(engine) as session:
        row = SensorReading(
            soil=soil,
            temp=temp,
            humidity=humidity,
            light=light,
            stage=stage,
            stage_name=stage_name,
            spectrum=spectrum,
            pump_on=pump_on,
            pump_status=pump_status,
            light_hrs_today=light_hrs_today,
            harvest_eta_days=harvest_eta_days,
            health_score=health_score,
        )
        session.add(row)
        session.commit()

