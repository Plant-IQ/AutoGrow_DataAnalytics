import json

from mqtt import subscriber


class _Msg:
    def __init__(self, topic: str, payload: bytes):
        self.topic = topic
        self.payload = payload


def test_on_message_ignores_invalid_json(monkeypatch):
    writes = []
    monkeypatch.setattr(subscriber, "write_sensor", lambda *args, **kwargs: writes.append((args, kwargs)))

    subscriber.on_message(None, None, _Msg("autogrow/temp", b"not-json"))
    assert writes == []


def test_on_message_handles_simple_sensor_topic(monkeypatch):
    captured = {"influx": [], "sqlite": []}

    monkeypatch.setattr(subscriber, "write_sensor", lambda *args: captured["influx"].append(args))
    monkeypatch.setattr(subscriber, "record_sensor", lambda *args: captured["sqlite"].append(args))

    payload = json.dumps({"value": "26.5"}).encode()
    subscriber.on_message(None, None, _Msg("autogrow/temp", payload))

    assert captured["influx"] == [("climate", "temperature", 26.5)]
    assert captured["sqlite"] == [("temp", 26.5)]


def test_on_message_handles_combined_sensor_topic(monkeypatch):
    recorded = {"combined": None}

    monkeypatch.setattr(subscriber, "_record_combined_sensor", lambda payload: recorded.__setitem__("combined", payload))

    payload = {"soil": 40, "temp1": 24, "humidity": 60}
    subscriber.on_message(None, None, _Msg("device-1/autogrow/sensors", json.dumps(payload).encode()))

    assert recorded["combined"] == payload


def test_record_combined_sensor_uses_db_stage_not_payload(monkeypatch):
    calls = {"combined": None, "write": []}

    monkeypatch.setattr(subscriber, "_get_active_stage", lambda: (1, "Veg"))
    monkeypatch.setattr(subscriber, "record_sensor_combined", lambda **kwargs: calls.__setitem__("combined", kwargs))
    monkeypatch.setattr(subscriber, "write_sensor", lambda *args: calls["write"].append(args))

    payload = {
        "soil_pct": 48,
        "temp1": 24,
        "temp2": 26,
        "humidity": 70,
        "light_lux": 350,
        "vibration": 0.2,
        "stage": 99,
        "stage_name": "Wrong",
        "health_score": 88,
        "harvest_eta_days": 12,
    }
    subscriber._record_combined_sensor(payload)

    assert calls["combined"]["stage"] == 1
    assert calls["combined"]["stage_name"] == "Veg"
    assert calls["combined"]["temp"] == 25.0
    assert calls["combined"]["soil"] == 48.0
    assert ("autogrow", "stage", 1.0) in calls["write"]
    assert ("autogrow", "health_score", 88.0) in calls["write"]
