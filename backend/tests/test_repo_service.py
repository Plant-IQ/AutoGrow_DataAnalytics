from datetime import datetime, timedelta

from db.sqlite import GrowthStage, Observation, SensorReading
from services import repo


def test_latest_sensor_returns_most_recent(db_session, active_plant):
    old = SensorReading(
        plant_instance_id=active_plant.id,
        ts=datetime.utcnow() - timedelta(hours=2),
        soil=30,
        temp=22,
        humidity=55,
        light=250,
    )
    latest = SensorReading(
        plant_instance_id=active_plant.id,
        ts=datetime.utcnow(),
        soil=45,
        temp=24,
        humidity=62,
        light=320,
    )
    db_session.add(old)
    db_session.add(latest)
    db_session.commit()

    result = repo.latest_sensor(db_session)
    assert result is not None
    assert result.id == latest.id


def test_recent_sensors_filters_by_hours(db_session, active_plant):
    stale = SensorReading(
        plant_instance_id=active_plant.id,
        ts=datetime.utcnow() - timedelta(hours=3),
        soil=30,
        temp=22,
        humidity=55,
        light=250,
    )
    fresh = SensorReading(
        plant_instance_id=active_plant.id,
        ts=datetime.utcnow() - timedelta(minutes=20),
        soil=40,
        temp=23,
        humidity=60,
        light=300,
    )
    db_session.add(stale)
    db_session.add(fresh)
    db_session.commit()

    rows = repo.recent_sensors(db_session, hours=1)
    assert len(rows) == 1
    assert rows[0].id == fresh.id


def test_latest_stage_returns_none_when_missing(db_session):
    assert repo.latest_stage(db_session) is None


def test_latest_stage_returns_latest_record(db_session):
    seed = GrowthStage(stage_index=0, stage_name="Seed", started_at=datetime.utcnow() - timedelta(days=2))
    veg = GrowthStage(stage_index=1, stage_name="Veg", started_at=datetime.utcnow())
    db_session.add(seed)
    db_session.add(veg)
    db_session.commit()

    result = repo.latest_stage(db_session)
    assert result is not None
    assert result.stage_name == "Veg"


def test_last_observation_returns_most_recent(db_session):
    first = Observation(
        created_at=datetime.utcnow() - timedelta(days=1),
        height_cm=10,
        leaf_count=3,
        root_visible=False,
        canopy_score=4,
    )
    second = Observation(
        created_at=datetime.utcnow(),
        height_cm=12,
        leaf_count=5,
        root_visible=True,
        canopy_score=8,
    )
    db_session.add(first)
    db_session.add(second)
    db_session.commit()

    result = repo.last_observation(db_session)
    assert result is not None
    assert result.id == second.id
