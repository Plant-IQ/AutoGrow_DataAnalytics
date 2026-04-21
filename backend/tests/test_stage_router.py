from datetime import datetime, timedelta


def test_get_stage_without_active_plant_returns_harvested(client):
    response = client.get("/stage/")
    assert response.status_code == 200
    assert response.json() == {"stage": -1, "label": "Harvested", "days_in_stage": 0}


def test_get_stage_with_active_plant_returns_current_stage(client, db_session, active_plant):
    active_plant.current_stage_index = 1
    active_plant.started_at = datetime.utcnow() - timedelta(days=2)
    db_session.add(active_plant)
    db_session.commit()

    response = client.get("/stage/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["stage"] == 1
    assert payload["label"] == "Veg"
    assert payload["days_in_stage"] >= 2


def test_set_stage_writes_growth_stage(client):
    response = client.post("/stage/set", json={"stage": 2, "label": "Bloom"})
    assert response.status_code == 200
    assert response.json() == {"stage": 2, "label": "Bloom", "days_in_stage": 1}
