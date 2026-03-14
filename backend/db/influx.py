# backend/db/influx.py
import os

USE_INFLUX = bool(os.getenv("INFLUX_URL") and os.getenv("INFLUX_TOKEN") and os.getenv("INFLUX_BUCKET"))

if USE_INFLUX:
    from influxdb_client_3 import InfluxDBClient3, Point

    client = InfluxDBClient3(
        host=os.getenv("INFLUX_URL"),
        token=os.getenv("INFLUX_TOKEN"),
        database=os.getenv("INFLUX_BUCKET"),
    )

    def write_sensor(measurement: str, field: str, value: float, tags: dict = None):
        tags = tags or {}
        point = Point(measurement).field(field, value)
        for k, v in tags.items():
            point = point.tag(k, v)
        client.write(record=point)
else:
    def write_sensor(measurement: str, field: str, value: float, tags: dict = None):
        # Stub: no-op for development without Influx configured
        return None
