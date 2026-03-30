import json
import os

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from db.influx import write_sensor
from db.sqlite import record_sensor

load_dotenv()

TOPICS = {
    "autogrow/soil": ("soil", "moisture", "soil"),
    "autogrow/temp": ("climate", "temperature", "temp"),
    "autogrow/humidity": ("climate", "humidity", "humidity"),
    "autogrow/light": ("light", "lux", "light"),
    "autogrow/vibration": ("pump", "vibration", None),  # not in SensorReading table
}


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode())
    if topic in TOPICS:
        measurement, field, sqlite_field = TOPICS[topic]
        value = float(payload["value"])

        # Write to time-series (Influx if enabled)
        write_sensor(measurement, field, value)

        # Mirror into SQLite for UI/API history & health
        if sqlite_field:
            try:
                record_sensor(sqlite_field, value)
            except Exception as e:
                print(f"[MQTT] SQLite write failed: {e}")

        print(f"[MQTT] {topic} → {value}")


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
