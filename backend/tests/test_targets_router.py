def test_targets_upsert_and_get(client, plant_type):
    payload = {
        "temp_min_c": 20,
        "temp_max_c": 28,
        "humidity_min": 50,
        "humidity_max": 75,
        "light_min_lux": 200,
        "light_max_lux": 500,
    }
    upsert = client.put(f"/targets/plant-types/{plant_type.id}/targets", json=payload)
    assert upsert.status_code == 200
    assert upsert.json()["plant_type_id"] == plant_type.id

    fetched = client.get(f"/targets/plant-types/{plant_type.id}/targets")
    assert fetched.status_code == 200
    assert fetched.json()["light_max_lux"] == 500.0


def test_targets_upsert_requires_existing_plant_type(client):
    payload = {
        "temp_min_c": 20,
        "temp_max_c": 28,
        "humidity_min": 50,
        "humidity_max": 75,
        "light_min_lux": 200,
        "light_max_lux": 500,
    }
    upsert = client.put("/targets/plant-types/9999/targets", json=payload)
    assert upsert.status_code == 404
    assert upsert.json()["detail"] == "Plant type not found"
