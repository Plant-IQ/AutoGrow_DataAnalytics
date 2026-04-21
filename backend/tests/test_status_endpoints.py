from sqlmodel import Session

from db.sqlite import SensorReading


def test_light_and_pump_defaults_without_active_plant(client):
    light = client.get("/light/")
    assert light.status_code == 200
    assert light.json() == {"spectrum": "", "hours_today": 0.0}

    pump = client.get("/pump-status/")
    assert pump.status_code == 200
    payload = pump.json()
    assert payload["ok"] is False
    assert payload["vibration"] == 0.0


def test_health_defaults_without_active_plant(client):
    res = client.get("/health/")
    assert res.status_code == 200
    assert res.json() == {"score": 0.0, "components": {}}


def test_status_endpoints_with_active_plant_and_sensor(client, latest_sensor: SensorReading, target_range):
    light = client.get("/light/")
    assert light.status_code == 200
    assert light.json() == {"spectrum": "white", "hours_today": 6.5}

    pump = client.get("/pump-status/")
    assert pump.status_code == 200
    pump_payload = pump.json()
    assert pump_payload["ok"] is True
    assert pump_payload["vibration"] == 0.2

    health = client.get("/health/")
    assert health.status_code == 200
    health_payload = health.json()
    assert health_payload["score"] > 0
    assert set(health_payload["components"].keys()) == {"soil", "temp", "humidity", "light"}
