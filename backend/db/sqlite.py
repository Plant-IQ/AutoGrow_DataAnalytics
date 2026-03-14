from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("SQLITE_PATH", "./autogrow.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

class Observation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    height_cm: float
    leaf_count: int
    root_visible: bool
    canopy_score: int

class GrowthStage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stage_index: int
    stage_name: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed: bool = False

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session