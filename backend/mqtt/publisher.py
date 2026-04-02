import json
import os

import paho.mqtt.publish as publish
from dotenv import load_dotenv

load_dotenv()


def publish_light_color(plant_id: int, color_hex: str):
    """Publish desired light color for a plant to MQTT.

    Topic: autogrow/<plant_id>/light/set
    Payload: {"plant_id": <id>, "color": "#RRGGBB"}
    """
    broker = os.getenv("MQTT_BROKER")
    port = os.getenv("MQTT_PORT")
    if not broker or not port:
        # Running without MQTT configured; skip silently but log for debugging
        print("[MQTT] Skipping publish (MQTT_BROKER/MQTT_PORT not set).")
        return

    auth = None
    user = os.getenv("MQTT_USER")
    pwd = os.getenv("MQTT_PASS")
    if user and pwd:
        auth = {"username": user, "password": pwd}

    topic = f"autogrow/{plant_id}/light/set"
    payload = json.dumps({"plant_id": plant_id, "color": color_hex})
    try:
        publish.single(topic, payload, hostname=broker, port=int(port), auth=auth)
        print(f"[MQTT] Published light color {color_hex} to {topic}")
    except Exception as e:
        print(f"[MQTT] Failed to publish light color: {e}")
