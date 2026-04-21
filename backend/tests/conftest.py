from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

import db.sqlite as sqlite_db
from db.sqlite import (
    AutogrowReading,
    PlantInstance,
    PlantType,
    PlantTypeTarget,
    SensorReading,
    get_mysql_session,
    get_session,
)
from routers import context, harvest, health, history, light, observations, plants, pump, stage, targets
from services import stage_engine


@pytest.fixture
def test_engine(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    monkeypatch.setattr(sqlite_db, "engine", engine)
    monkeypatch.setattr(history, "engine", engine)
    monkeypatch.setattr(plants, "engine", engine)
    monkeypatch.setattr(stage_engine, "engine", engine)

    return engine


@pytest.fixture
def app(test_engine):
    def _session_override() -> Generator[Session, None, None]:
        with Session(test_engine) as session:
            yield session

    api = FastAPI()
    api.include_router(stage.router, prefix="/stage")
    api.include_router(health.router, prefix="/health")
    api.include_router(light.router, prefix="/light")
    api.include_router(harvest.router, prefix="/harvest-eta")
    api.include_router(history.router, prefix="/history")
    api.include_router(pump.router, prefix="/pump-status")
    api.include_router(observations.router, prefix="/observations")
    api.include_router(context.router, prefix="/context")
    api.include_router(context.outdoor_router, prefix="/outdoor")
    api.include_router(targets.router, prefix="/targets")
    api.include_router(plants.router, prefix="/plants")
    api.include_router(plants.alias_router)

    api.dependency_overrides[get_session] = _session_override
    api.dependency_overrides[get_mysql_session] = _session_override
    return api


@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session(test_engine) -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def plant_type(db_session: Session) -> PlantType:
    row = PlantType(
        name="Lettuce",
        stage_durations_days=[7, 14, 7],
        stage_colors=["#4DA6FF", "#FFFFFF", "#FF6FA3"],
    )
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    return row


@pytest.fixture
def active_plant(db_session: Session, plant_type: PlantType) -> PlantInstance:
    row = PlantInstance(
        session_code="00001",
        label="Lettuce",
        plant_type_id=plant_type.id,
        started_at=datetime.utcnow(),
        stage_started_at=datetime.utcnow(),
        is_active=True,
        current_stage_index=0,
        pending_confirm=False,
    )
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    return row


@pytest.fixture
def latest_sensor(db_session: Session, active_plant: PlantInstance) -> SensorReading:
    row = SensorReading(
        plant_instance_id=active_plant.id,
        soil=45.0,
        temp=24.0,
        humidity=63.0,
        light=320.0,
        vibration=0.2,
        stage=0,
        stage_name="Seed",
        spectrum="white",
        pump_on=True,
        light_hrs_today=6.5,
    )
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    return row


@pytest.fixture
def target_range(db_session: Session, plant_type: PlantType) -> PlantTypeTarget:
    row = PlantTypeTarget(
        plant_type_id=plant_type.id,
        temp_min_c=20.0,
        temp_max_c=28.0,
        humidity_min=50.0,
        humidity_max=75.0,
        light_min_lux=200.0,
        light_max_lux=500.0,
    )
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    return row


@pytest.fixture
def autogrow_rows(db_session: Session, active_plant: PlantInstance):
    first = AutogrowReading(
        ts=active_plant.started_at,
        stage=0,
        stage_name="Seed",
        temp1=24.1,
        humidity=61.0,
        soil_pct=45.0,
        light_lux=220.0,
        pump_on=0,
    )
    second = AutogrowReading(
        ts=active_plant.started_at.replace(microsecond=0),
        stage=1,
        stage_name="Veg",
        temp1=25.2,
        humidity=64.0,
        soil_pct=46.0,
        light_lux=310.0,
        pump_on=1,
    )
    db_session.add(first)
    db_session.add(second)
    db_session.commit()
    return [first, second]
