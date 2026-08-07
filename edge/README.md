# FALCON Edge Service

Laptop-first foundation for the future FALCON mini PC. It collects telemetry,
validates sensor values, evaluates deterministic safety rules, and stores every
sample in SQLite. It uses only the Python standard library.

## Run with simulated telemetry

From the repository root:

```powershell

cd "C:\Users\Admin\Documents\PlatformIO\Projects\Project FALCON-01\edge"
python -m falcon_edge.service

```

Open the integrated dashboard:

- `http://127.0.0.1:8765/`

The service also provides these local endpoints:

- `http://127.0.0.1:8765/health`
- `http://127.0.0.1:8765/api/latest`
- `http://127.0.0.1:8765/api/history?limit=20`
- `http://127.0.0.1:8765/api/alerts?limit=20`
- `http://127.0.0.1:8765/api/scenario`
- `http://127.0.0.1:8765/api/forecast`
- `http://127.0.0.1:8765/api/forecast/validation`

The dashboard's virtual sensor lab can switch between normal operation, rough
sea, low battery, overheating, and sensor-failure scenarios. Generated warnings
are evaluated by the real rules engine and persisted in SQLite.

The overview also includes a presentation-only trend forecaster for wave
height, wind speed, water level, water temperature, and battery reserve at
5-, 15-, and 30-minute horizons. It is intentionally marked experimental and
must be retrained and validated with real sensor data before field use.

The validation endpoint performs a rolling one-step backtest over recent
telemetry and reports mean absolute error, direction accuracy, an overall demo
model score, and predicted-versus-actual wave comparisons.

The database is created at `edge/data/falcon.db`. This runtime data is ignored
by Git.

## Read from the ESP32

Connect the computer to the `FALCON-01` Wi-Fi network, then run:

```powershell
python -m falcon_edge.service --source esp32 --esp32-url http://192.168.4.1
```

The collector intentionally records connection errors instead of silently
substituting fake readings when ESP32 mode is selected.

## Run tests

```powershell
cd edge
python -m unittest discover -s tests -v
```

## Current rules

- Valid physical ranges for battery, water temperature, tilt, and wave level
- Low/critical battery reserve
- High water temperature
- High/critical station tilt
- High wave activity

Thresholds are prototype defaults and must be reviewed against the selected
sensors and deployment safety requirements before field use.
