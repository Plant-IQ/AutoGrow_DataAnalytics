def test_create_and_list_observations(client):
    payload = {
        "height_cm": 12.5,
        "leaf_count": 6,
        "root_visible": True,
        "canopy_score": 8,
    }
    created = client.post("/observations/", json=payload)
    assert created.status_code == 200
    body = created.json()
    assert body["height_cm"] == 12.5
    assert body["leaf_count"] == 6

    listed = client.get("/observations/?limit=5")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
