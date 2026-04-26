import json
from datetime import date, datetime, timedelta, timezone

from db.sqlite import WeatherCache
from services import external_weather


def test_parse_iso_datetime_handles_z_and_invalid_values():
    parsed = external_weather._parse_iso_datetime("2026-01-01T10:20:30Z")
    assert parsed is not None
    assert parsed.tzinfo is not None

    assert external_weather._parse_iso_datetime("not-a-datetime") is None
    assert external_weather._parse_iso_datetime(None) is None


def test_cache_get_returns_payload_when_fresh(db_session, monkeypatch):
    monkeypatch.setattr(external_weather, "WEATHER_CACHE_TTL_SECONDS", 3600)

    key = "weather:v3:Asia/Bangkok:13.848:100.570"
    payload = {"source": "open-meteo", "temp_c": 30.0}
    db_session.add(
        WeatherCache(
            key=key,
            payload=json.dumps(payload),
            ts=datetime.now(timezone.utc) - timedelta(minutes=10),
        )
    )
    db_session.commit()

    result = external_weather._cache_get(db_session, key)
    assert result == payload


def test_cache_get_returns_none_when_expired(db_session, monkeypatch):
    monkeypatch.setattr(external_weather, "WEATHER_CACHE_TTL_SECONDS", 60)

    key = "weather:v3:Asia/Bangkok:13.848:100.570"
    db_session.add(
        WeatherCache(
            key=key,
            payload=json.dumps({"source": "open-meteo"}),
            ts=datetime.now(timezone.utc) - timedelta(hours=2),
        )
    )
    db_session.commit()

    assert external_weather._cache_get(db_session, key) is None


def test_get_outdoor_daily_avg_groups_by_date(monkeypatch):
    monkeypatch.setattr(
        external_weather,
        "get_outdoor_history",
        lambda session, lat, lon, past_days, start_date=None, end_date=None: {
            "points": [
                {"ts": "2026-04-20T00:00:00Z", "temp": 30, "humidity": 60},
                {"ts": "2026-04-20T12:00:00Z", "temp": 32, "humidity": 70},
                {"ts": "2026-04-21T00:00:00Z", "temp": 28, "humidity": 55},
            ]
        },
    )

    payload = external_weather.get_outdoor_daily_avg(session=None, lat=13.7, lon=100.5, past_days=2)
    assert payload["source"] == "open-meteo"
    assert payload["points"] == [
        {"date": "2026-04-20", "avg_temp": 31.0, "avg_humidity": 65.0},
        {"date": "2026-04-21", "avg_temp": 28.0, "avg_humidity": 55.0},
    ]


def test_fetch_open_meteo_history_range_uses_archive_endpoint(monkeypatch):
    captured = {}

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "hourly": {
                    "time": ["2026-03-31T00:00", "2026-03-31T01:00"],
                    "temperature_2m": [29.5, 30.0],
                    "relative_humidity_2m": [80, 78],
                }
            }

    class DummyClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url, params):
            captured["url"] = url
            captured["params"] = params
            return DummyResponse()

    monkeypatch.setattr(external_weather.httpx, "Client", DummyClient)

    payload = external_weather.fetch_open_meteo_history_range(
        13.7,
        100.5,
        date(2026, 3, 31),
        date(2026, 4, 18),
    )

    assert captured["url"] == "https://archive-api.open-meteo.com/v1/archive"
    assert captured["params"]["start_date"] == "2026-03-31"
    assert captured["params"]["end_date"] == "2026-04-18"
    assert payload["start_date"] == "2026-03-31"
    assert payload["end_date"] == "2026-04-18"
    assert payload["points"][0] == {"ts": "2026-03-31T00:00", "temp": 29.5, "humidity": 80}


def test_get_outdoor_history_uses_date_range_when_provided(monkeypatch):
    seen = {}

    def fake_fetch(lat, lon, start_date, end_date):
        seen["args"] = (lat, lon, start_date, end_date)
        return {"source": "open-meteo", "lat": lat, "lon": lon, "points": []}

    monkeypatch.setattr(external_weather, "fetch_open_meteo_history_range", fake_fetch)
    monkeypatch.setattr(external_weather, "fetch_open_meteo_history", lambda *args, **kwargs: {"points": []})
    monkeypatch.setattr(external_weather, "_cache_get", lambda session, key: None)
    monkeypatch.setattr(external_weather, "_cache_set", lambda session, key, payload: payload)
    monkeypatch.setattr(external_weather, "_sync_weather_history_to_mysql", lambda payload: 0)

    payload = external_weather.get_outdoor_history(
        session=None,
        lat=13.7,
        lon=100.5,
        start_date=date(2026, 3, 31),
        end_date=date(2026, 4, 18),
    )

    assert seen["args"][2:] == (date(2026, 3, 31), date(2026, 4, 18))
    assert payload["lat"] == 13.7


def test_backfill_weather_cache_routes_payloads_by_key_prefix(db_session, test_engine, monkeypatch):
    monkeypatch.setattr(external_weather, "engine", test_engine)

    db_session.add(
        WeatherCache(
            key="weather:v3:Asia/Bangkok:13.848:100.570",
            payload=json.dumps({"fetched_at": "2026-04-21T00:00:00Z"}),
            ts=datetime.utcnow(),
        )
    )
    db_session.add(
        WeatherCache(
            key="outdoor-history:13.848:100.570:7",
            payload=json.dumps({"points": [{"ts": "2026-04-20T00:00:00Z"}]}),
            ts=datetime.utcnow(),
        )
    )
    db_session.commit()

    monkeypatch.setattr(external_weather, "_sync_current_weather_to_mysql", lambda payload: True)
    monkeypatch.setattr(external_weather, "_sync_weather_history_to_mysql", lambda payload: 3)

    migrated = external_weather.backfill_weather_cache_to_mysql()
    assert migrated == {"current": 1, "history": 3}
