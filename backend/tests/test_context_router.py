def test_weather_context_success(client, monkeypatch):
    monkeypatch.setattr(
        "routers.context.get_weather_bundle",
        lambda session, lat, lon: {"source": "stub", "lat": lat or 1, "lon": lon or 2},
    )
    res = client.get("/context/weather?lat=13.7&lon=100.5")
    assert res.status_code == 200
    payload = res.json()
    assert payload["source"] == "stub"
    assert payload["lat"] == 13.7
    assert payload["lon"] == 100.5


def test_weather_context_wraps_error_as_502(client, monkeypatch):
    def _boom(session, lat, lon):
        raise RuntimeError("provider down")

    monkeypatch.setattr("routers.context.get_weather_bundle", _boom)
    res = client.get("/context/weather")
    assert res.status_code == 502
    assert res.json()["detail"] == "provider down"


def test_outdoor_daily_avg_success(client, monkeypatch):
    monkeypatch.setattr(
        "routers.context.get_outdoor_daily_avg",
        lambda session, lat, lon, past_days: {"points": [{"date": "2026-01-01", "avg_temp": 28.0}]},
    )
    res = client.get("/outdoor/daily-avg?past_days=3")
    assert res.status_code == 200
    assert res.json()["points"][0]["avg_temp"] == 28.0
