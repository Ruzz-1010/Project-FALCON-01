# FALCON Edge Service v4.0

Local-first Python service for the Project FALCON Mini PC. It collects ESP32 telemetry, validates approved sensors, evaluates deterministic alerts, stores operational records in SQLite, serves the dashboard, and provides AI-assisted wave-height predictions.

## Run the Presentation Simulator

From the repository root:

```powershell
cd "C:\Users\Admin\Documents\PlatformIO\Projects\Project FALCON-01\edge"
python -m falcon_edge.service
```

Open `http://127.0.0.1:8765/`.

## Approved v4 API

- `GET /status`
- `GET /wave`
- `GET /gps`
- `GET /battery`
- `GET /solar`
- `GET /ai?horizon=5`
- `GET /ai?horizon=15`
- `POST /restart`
- `POST /calibrate`

Dashboard v5 presentation extensions:

- `GET /prediction?horizon=10`
- `GET /logs?limit=60`

The route remains `GET /ai`; `horizon` selects one of the two approved prediction windows. Legacy `/api/...` routes remain temporarily for presentation compatibility. The dashboard uses `/api/scenario` only for the clearly labeled virtual sensor lab.

The AI predicts wave height only. It returns current and predicted values, confidence, model status, and Calm, Moderate, or Rough classification. It does not predict other sensors and is not validated for safety decisions.

Presentation scenarios use gradual state transitions. Rough Sea ramps wave height, wind, roll, and pitch over multiple samples and settles gradually when Normal operation is restored, preventing unrealistic graph steps.

## Local Database

The default database is `edge/data/falcon.db`. Startup performs a non-destructive additive schema migration.

- `telemetry` — raw timestamped source payloads
- `alerts` — deterministic alerts linked to telemetry
- `wave_predictions` — stored 5- and 15-minute predictions
- `system_events` — audited restart and calibration requests

Runtime database files are ignored by Git.

## Read from the ESP32

Connect the Mini PC or laptop to the ESP32 endpoint and run:

```powershell
python -m falcon_edge.service --source esp32 --esp32-url http://192.168.4.1
```

ESP32 connection failures are reported explicitly. The service never silently replaces physical-source failures with simulated readings.

## Tests

```powershell
cd edge
python -m unittest discover -s tests -v
```

The test suite covers the two approved prediction horizons, wave-only output, sea-condition classification, invalid horizons, wave backtesting, sensor validation, and presentation alert scenarios.
