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

class ErrorResponse(BaseModel):
<<<<<<< HEAD
    detail: str
=======
    detail: str


class ObservationCreate(BaseModel):
    height_cm: float
    leaf_count: int
    root_visible: bool
    canopy_score: int
>>>>>>> bb67116 (feat: add MQTT-driven sensor persistence and UI dashboard)
