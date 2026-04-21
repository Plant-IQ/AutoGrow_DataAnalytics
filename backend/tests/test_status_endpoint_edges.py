
def test_light_and_pump_default_when_active_plant_has_no_sensor(client, active_plant):
    light = client.get("/light/")
    assert light.status_code == 200
    assert light.json() == {"spectrum": "", "hours_today": 0.0}

    pump = client.get("/pump-status/")
    assert pump.status_code == 200
    payload = pump.json()
    assert payload["ok"] is False
    assert payload["vibration"] == 0.0
