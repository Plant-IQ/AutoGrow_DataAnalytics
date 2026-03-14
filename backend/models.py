from pydantic import BaseModel
from typing import List
from datetime import datetime

class StageResponse(BaseModel):
    stage: int
    label: str
    days_in_stage: int

class HealthResponse(BaseModel):
    score: float
    components: dict  # e.g., {"soil": 0.8, "temp": 0.9}

class LightResponse(BaseModel):
    spectrum: str      # "veg", "bloom", etc.
    hours_today: float

class HarvestETAResponse(BaseModel):
    days_to_harvest: int
    projected_date: datetime

class HistoryPoint(BaseModel):
    ts: datetime
    soil: float
    temp: float
    humidity: float
    light: float

class HistoryResponse(BaseModel):
    points: List[HistoryPoint]

class PumpStatusResponse(BaseModel):
    ok: bool
    vibration: float
    last_checked: datetime
