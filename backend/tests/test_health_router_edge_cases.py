from db.sqlite import SensorReading


def test_health_returns_zero_when_active_plant_has_no_sensor(client, active_plant):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"score": 0.0, "components": {}}


def test_health_uses_compute_health_without_targets_when_target_missing(client, db_session, active_plant, monkeypatch):
    row = SensorReading(
        plant_instance_id=active_plant.id,
        soil=40,
        temp=24,
        humidity=60,
        light=300,
    )
    db_session.add(row)
    db_session.commit()

    called = {"target": "unset"}

    def _fake_compute(reading, targets):
        called["target"] = targets
        return 77.7, {"soil": 0.8, "temp": 0.8, "humidity": 0.8, "light": 0.8}

    monkeypatch.setattr("routers.health.compute_health", _fake_compute)

    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["score"] == 77.7
    assert called["target"] is None
