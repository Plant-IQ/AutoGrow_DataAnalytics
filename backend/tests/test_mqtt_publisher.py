import json

from mqtt import publisher


def test_publish_light_color_skips_when_mqtt_not_configured(monkeypatch):
    monkeypatch.delenv("MQTT_BROKER", raising=False)
    monkeypatch.delenv("MQTT_PORT", raising=False)

    called = {"value": False}

    def _fake_single(*args, **kwargs):
        called["value"] = True

    monkeypatch.setattr(publisher.publish, "single", _fake_single)
    publisher.publish_light_color(plant_id=5, color_hex="#FFFFFF")

    assert called["value"] is False


def test_publish_light_color_calls_publish_single(monkeypatch):
    monkeypatch.setenv("MQTT_BROKER", "broker.local")
    monkeypatch.setenv("MQTT_PORT", "1883")
    monkeypatch.setenv("MQTT_USER", "u1")
    monkeypatch.setenv("MQTT_PASS", "p1")

    captured = {}

    def _fake_single(topic, payload, hostname, port, auth):
        captured["topic"] = topic
        captured["payload"] = payload
        captured["hostname"] = hostname
        captured["port"] = port
        captured["auth"] = auth

    monkeypatch.setattr(publisher.publish, "single", _fake_single)

    publisher.publish_light_color(plant_id=7, color_hex="#4DA6FF")

    assert captured["topic"] == "autogrow/7/light/set"
    assert json.loads(captured["payload"]) == {"plant_id": 7, "color": "#4DA6FF"}
    assert captured["hostname"] == "broker.local"
    assert captured["port"] == 1883
    assert captured["auth"] == {"username": "u1", "password": "p1"}


def test_publish_stage_update_uses_user_topic(monkeypatch):
    monkeypatch.setenv("MQTT_BROKER", "broker.local")
    monkeypatch.setenv("MQTT_PORT", "1883")
    monkeypatch.setenv("MQTT_USER", "user123")
    monkeypatch.setenv("MQTT_PASS", "secret")

    captured = {}

    def _fake_single(topic, payload, hostname, port, auth):
        captured["topic"] = topic
        captured["payload"] = payload
        captured["auth"] = auth

    monkeypatch.setattr(publisher.publish, "single", _fake_single)

    publisher.publish_stage_update(plant_id=99, stage=2)

    assert captured["topic"] == "user123/autogrow/cmd"
    assert json.loads(captured["payload"]) == {"stage": 2}
    assert captured["auth"] == {"username": "user123", "password": "secret"}
