import json
import os

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from db.influx import write_sensor

load_dotenv()

TOPICS = {
    "autogrow/soil": ("soil", "moisture"),
    "autogrow/temp": ("climate", "temperature"),
    "autogrow/humidity": ("climate", "humidity"),
    "autogrow/light": ("light", "lux"),
    "autogrow/vibration": ("pump", "vibration"),
}


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode())
    if topic in TOPICS:
        measurement, field = TOPICS[topic]
        write_sensor(measurement, field, float(payload["value"]))
        print(f"[MQTT] {topic} → {payload['value']}")


def start_subscriber():
    """Start MQTT listener or short-circuit if hardware/broker is not ready."""

    broker = os.getenv("MQTT_BROKER")
    port = os.getenv("MQTT_PORT")

    if not broker or not port:
        print("[MQTT] Skipping subscriber (MQTT_BROKER/MQTT_PORT not set).")
        return

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_message = on_message
        client.connect(broker, int(port))
        for topic in TOPICS:
            client.subscribe(topic)
        client.loop_start()
        print(f"[MQTT] Subscriber started on {broker}:{port}")
    except Exception as e:
        print(f"[MQTT] Could not connect: {e} — running without MQTT")
