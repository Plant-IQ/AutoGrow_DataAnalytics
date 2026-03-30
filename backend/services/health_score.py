"""Simple health score calculator.

Given the latest sensor reading (or None), return a 0–100 score and the
component weights that contributed to it. This is intentionally lightweight
until we have a trained model.
"""

from typing import Optional, Tuple, Dict

from db.sqlite import SensorReading


def _clamp(value: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(value, max_v))


def _score_range(value: float, ideal_min: float, ideal_max: float, hard_min: float, hard_max: float) -> float:
    """Return 0–1 score based on how close a value is to the ideal band."""
    if value < hard_min or value > hard_max:
        return 0.0
    if ideal_min <= value <= ideal_max:
        return 1.0
    # linearly decay toward hard limits
    if value < ideal_min:
        return (value - hard_min) / (ideal_min - hard_min)
    return (hard_max - value) / (hard_max - ideal_max)


def compute_health(reading: Optional[SensorReading]) -> Tuple[float, Dict[str, float]]:
    """Return (score, components) where score is 0–100.

    If no reading is provided, fall back to mid-range defaults.
    """

    if reading is None:
        components = {"soil": 0.8, "temp": 0.9, "humidity": 0.85, "light": 0.75}
    else:
        components = {
            "soil": _score_range(reading.soil, ideal_min=35, ideal_max=55, hard_min=20, hard_max=70),
            "temp": _score_range(reading.temp, ideal_min=22, ideal_max=26, hard_min=15, hard_max=32),
            "humidity": _score_range(reading.humidity, ideal_min=55, ideal_max=70, hard_min=30, hard_max=90),
            "light": _score_range(reading.light, ideal_min=250, ideal_max=450, hard_min=100, hard_max=700),
        }

    score = sum(components.values()) / len(components) * 100
    score = round(_clamp(score, 0, 100), 1)

    return score, components
