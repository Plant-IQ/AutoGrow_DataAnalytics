from datetime import datetime, timedelta

from sqlmodel import Session

from db.sqlite import PlantInstance


VALID_TYPE_PAYLOAD = {
    "name": "Water Spinach",
    "stage_durations_days": [7, 21, 0],
    "stage_colors": ["#4DA6FF", "#FFFFFF", "#FF6FA3"],
}


def test_create_type_is_case_insensitive_upsert(client):
    first = client.post("/plants/types", json=VALID_TYPE_PAYLOAD)
    assert first.status_code == 200

    second_payload = {**VALID_TYPE_PAYLOAD, "name": "water spinach", "stage_durations_days": [5, 10, 0]}
    second = client.post("/plants/types", json=second_payload)
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["stage_durations_days"] == [5, 10, 0]

    listing = client.get("/plants/types")
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_start_and_harvest_active_plant(client):
    create_type = client.post("/plants/types", json=VALID_TYPE_PAYLOAD)
    assert create_type.status_code == 200

    start = client.post("/plants/start", json={"name": "Water Spinach"})
    assert start.status_code == 200
    started = start.json()
    assert started["label"] == "Water Spinach"
    assert started["is_active"] is True

    active_before = client.get("/plants/active")
    assert active_before.status_code == 200
    assert active_before.json()["id"] == started["id"]

    harvested = client.post("/plants/harvest-active")
    assert harvested.status_code == 200
    harvest_payload = harvested.json()
    assert harvest_payload["ok"] is True
    assert harvest_payload["stage"] == -1

    active_after = client.get("/plants/active")
    assert active_after.status_code == 200
    assert active_after.json() is None


def test_confirm_transition_increments_stage(client, db_session: Session, active_plant: PlantInstance):
    active_plant.current_stage_index = 0
    active_plant.pending_confirm = True
    active_plant.stage_started_at = datetime.utcnow() - timedelta(days=8)
    db_session.add(active_plant)
    db_session.commit()

    response = client.post(f"/plants/{active_plant.id}/confirm-transition")
    assert response.status_code == 200
    updated = response.json()
    assert updated["current_stage_index"] == 1
    assert updated["pending_confirm"] is False
