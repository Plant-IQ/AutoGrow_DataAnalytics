from datetime import datetime, timedelta

from db.sqlite import PlantInstance, PlantType


def test_harvest_eta_without_active_plant_returns_zero(client):
    response = client.get("/harvest-eta/")
    assert response.status_code == 200

    payload = response.json()
    assert payload["days_to_harvest"] == 0
    assert "projected_date" in payload


def test_harvest_eta_without_matching_plant_type_returns_zero(client, db_session):
    row = PlantInstance(
        session_code="00001",
        label="Unknown",
        plant_type_id=9999,
        started_at=datetime.utcnow() - timedelta(days=5),
        stage_started_at=datetime.utcnow() - timedelta(days=5),
        is_active=True,
        current_stage_index=0,
        pending_confirm=False,
    )
    db_session.add(row)
    db_session.commit()

    response = client.get("/harvest-eta/")
    assert response.status_code == 200
    assert response.json()["days_to_harvest"] == 0


def test_harvest_eta_uses_stage_durations_and_elapsed_days(client, db_session, monkeypatch):
    fixed_now = datetime(2026, 4, 21, 12, 0, 0)

    class _FixedDateTime(datetime):
        @classmethod
        def utcnow(cls):
            return fixed_now

    monkeypatch.setattr("routers.harvest.datetime", _FixedDateTime)

    plant_type = PlantType(
        name="Basil",
        stage_durations_days=[7, 14, 10],
        stage_colors=["#4DA6FF", "#FFFFFF", "#FF6FA3"],
    )
    db_session.add(plant_type)
    db_session.commit()
    db_session.refresh(plant_type)

    active = PlantInstance(
        session_code="00002",
        label="Basil",
        plant_type_id=plant_type.id,
        started_at=fixed_now - timedelta(days=5),
        stage_started_at=fixed_now - timedelta(days=5),
        is_active=True,
        current_stage_index=0,
        pending_confirm=False,
    )
    db_session.add(active)
    db_session.commit()

    response = client.get("/harvest-eta/")
    assert response.status_code == 200

    payload = response.json()
    assert payload["days_to_harvest"] == 26
    assert payload["projected_date"].startswith("2026-05-17")
