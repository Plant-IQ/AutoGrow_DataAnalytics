# AutoGrow

Minimal full-stack prototype to monitor grow stages, health, sensor history, and manual observations.

## Backend (FastAPI)

```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Environment flags:
- `SQLITE_PATH` (optional) custom sqlite location, defaults to `./autogrow.db`
- `MQTT_BROKER` / `MQTT_PORT` (optional) to enable the MQTT subscriber
- `INFLUX_URL`, `INFLUX_TOKEN`, `INFLUX_BUCKET` (optional) to stream sensor data to InfluxDB; otherwise stubbed

## Frontend (Next.js)

```
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

If `NEXT_PUBLIC_API_URL` is omitted the UI calls `http://localhost:8000` by default. Mock data is returned until real sensor readings exist in the database.
