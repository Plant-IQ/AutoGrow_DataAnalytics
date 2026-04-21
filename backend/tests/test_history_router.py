from datetime import timedelta

from db.sqlite import AutogrowReading


def test_history_returns_empty_without_active_plant(client):
    res = client.get("/history/")
    assert res.status_code == 200
    assert res.json() == {"points": []}


def test_history_maps_autogrow_rows(client, db_session, active_plant):
    first = AutogrowReading(
        ts=active_plant.started_at + timedelta(minutes=1),
        stage=0,
        stage_name="Seed",
        spectrum="blue",
        temp1=24.1,
        humidity=61.0,
        soil_pct=45.0,
        light_lux=220.0,
        pump_on=0,
    )
    second = AutogrowReading(
        ts=active_plant.started_at + timedelta(minutes=2),
        stage=1,
        stage_name="Veg",
        spectrum="white",
        temp1=25.2,
        humidity=64.0,
        soil_pct=46.0,
        light_lux=310.0,
        pump_on=1,
    )
    db_session.add(first)
    db_session.add(second)
    db_session.commit()

    res = client.get("/history/")
    assert res.status_code == 200
    payload = res.json()
    assert len(payload["points"]) == 2
    newest = payload["points"][0]
    assert newest["stage_name"] == "Veg"
    assert newest["pump_on"] is True
    assert newest["light"] == 310.0


def test_history_until_stage_filters_from_matching_stage(client, db_session, active_plant):
    db_session.add(
        AutogrowReading(
            ts=active_plant.started_at + timedelta(minutes=1),
            stage=0,
            stage_name="Seed",
            temp1=24.1,
            humidity=61.0,
            soil_pct=45.0,
            light_lux=220.0,
            pump_on=0,
        )
    )
    db_session.add(
        AutogrowReading(
            ts=active_plant.started_at + timedelta(minutes=2),
            stage=1,
            stage_name="Veg",
            temp1=25.2,
            humidity=64.0,
            soil_pct=46.0,
            light_lux=310.0,
            pump_on=1,
        )
    )
    db_session.commit()

    res = client.get("/history/?until_stage=seed")
    assert res.status_code == 200
    payload = res.json()
    assert len(payload["points"]) == 1
    assert payload["points"][0]["stage_name"] == "Seed"
