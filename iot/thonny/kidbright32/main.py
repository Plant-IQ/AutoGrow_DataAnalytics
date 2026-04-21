"""AutoGrow MicroPython starter.

Publishes a combined sensor payload to MQTT at a fixed interval.
Replace mock sensor reads with real ADC/DHT/library reads on your board.
"""

import json
import time

from config import (
    COMBINED_TOPIC,
    MQTT_BROKER,
    MQTT_PASS,
    MQTT_PORT,
    MQTT_USER,
    PUBLISH_INTERVAL_SECONDS,
    WIFI_PASSWORD,
    WIFI_SSID,
)


def connect_wifi(timeout_s=20):
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        return wlan

    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > timeout_s:
            raise RuntimeError("Wi-Fi connection timeout")
        time.sleep(0.2)
    return wlan


def connect_mqtt():
    from umqtt.simple import MQTTClient

    client_id = b"autogrow_kidbright32"
    user = MQTT_USER if MQTT_USER else None
    pwd = MQTT_PASS if MQTT_PASS else None

    client = MQTTClient(
        client_id=client_id,
        server=MQTT_BROKER,
        port=MQTT_PORT,
        user=user,
        password=pwd,
        keepalive=60,
    )
    client.connect()
    return client


def read_sensors():
    # TODO: Replace with real reads from DHT11, LDR, soil sensor, etc.
    return {
        "temp1": 26.5,
        "temp2": 26.1,
        "humidity": 62.0,
        "soil_pct": 48.0,
        "light_lux": 345.0,
        "vibration": 0.02,
        "pump_on": False,
        "pump_status": "healthy",
        "light_hrs_today": 9.3,
        "harvest_eta_days": 21,
        "health_score": 84,
        "spectrum": "white",
    }


def main():
    connect_wifi()
    client = connect_mqtt()

    while True:
        payload = read_sensors()
        payload_str = json.dumps(payload)
        client.publish(COMBINED_TOPIC, payload_str)
        time.sleep(PUBLISH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
