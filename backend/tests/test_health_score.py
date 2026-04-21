from services.health_score import TargetRange, _expand, compute_health


class Reading:
    def __init__(self, soil: float, temp: float, humidity: float, light: float):
        self.soil = soil
        self.temp = temp
        self.humidity = humidity
        self.light = light


def test_compute_health_without_reading_returns_default_band():
    score, components = compute_health(None)
    assert score > 0
    assert set(components.keys()) == {"soil", "temp", "humidity", "light"}


def test_compute_health_with_targets_scores_high_for_ideal_values():
    reading = Reading(soil=45.0, temp=25.0, humidity=60.0, light=300.0)
    targets = TargetRange(
        temp_min_c=20.0,
        temp_max_c=28.0,
        humidity_min=50.0,
        humidity_max=75.0,
        light_min_lux=200.0,
        light_max_lux=500.0,
    )
    score, components = compute_health(reading, targets=targets)
    assert score >= 95
    assert all(value > 0.9 for value in components.values())


def test_expand_adds_margin_to_range():
    low, high = _expand(10.0, 20.0, margin=0.2)
    assert low == 8.0
    assert high == 22.0
