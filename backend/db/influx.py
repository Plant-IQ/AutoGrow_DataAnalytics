from influxdb_client_3 import InfluxDBClient3, Point
from dotenv import load_dotenv
import os

load_dotenv()

client = InfluxDBClient3(
    host=os.getenv("INFLUX_URL"),
    token=os.getenv("INFLUX_TOKEN"),
    database=os.getenv("INFLUX_BUCKET"),
)

def write_sensor(measurement: str, field: str, value: float, tags: dict = {}):
    point = Point(measurement).field(field, value)
    for k, v in tags.items():
        point = point.tag(k, v)
    client.write(record=point)