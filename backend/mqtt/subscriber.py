import paho.mqtt.client as mqtt
from db.influx import write_sensor
import json, os
from dotenv import load_dotenv

load_dotenv()

TOPICS = {
    "autogrow/soil":      ("soil", "moisture"),
    "autogrow/temp":      ("climate", "temperature"),
    "autogrow/humidity":  ("climate", "humidity"),
    "autogrow/light":     ("light", "lux"),
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
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_message = on_message
        client.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")))
        for topic in TOPICS:
            client.subscribe(topic)
        client.loop_start()
        print("[MQTT] Subscriber started")
    except Exception as e:
        print(f"[MQTT] Could not connect: {e} — running without MQTT")