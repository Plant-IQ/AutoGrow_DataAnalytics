"""Local device config template.

Copy this file to config.py and edit values for your environment.
"""

WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

MQTT_BROKER = "broker.example.com"
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASS = ""

# Examples from backend subscribers:
# - autogrow/soil
# - autogrow/temp
# - autogrow/humidity
# - autogrow/light
# - autogrow/vibration
# - <user>/autogrow/sensors (combined payload)
SENSOR_TOPIC_BASE = "autogrow"
COMBINED_TOPIC = "b6710545652/autogrow/sensors"

PUBLISH_INTERVAL_SECONDS = 10
