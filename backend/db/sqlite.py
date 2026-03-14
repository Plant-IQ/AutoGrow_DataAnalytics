import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine

load_dotenv()

# Allow overriding via env; default lives alongside backend code
DB_PATH = os.getenv("SQLITE_PATH", "./autogrow.db")
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
    ts: datetime = Field(default_factory=datetime.utcnow, index=True)
    soil: float
    temp: float
    humidity: float
    light: float


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
