# FALCON Edge Service — Current v6.1 Baseline

Shore-based Python Bay Station service for Project FALCON. It receives ESP32 buoy telemetry, validates approved channels, evaluates deterministic alerts, stores operational records in SQLite, performs pressure-based wave processing and short-term prediction, and serves the dashboard. Prediction is isolated from core ingestion and logging. A development laptop currently performs the Bay Station role; the final mini PC is pending approval.

## Run the Presentation Simulator

From the repository root:

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01/edge"
python3 -m falcon_edge.service
```

Open `http://127.0.0.1:8765/`.

This URL serves the bundled production build of `dashboard-next`. Rebuild it with
`npm run build` inside `dashboard-next/` after frontend changes.

## API compatibility routes

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

Presentation scenarios use gradual state transitions. Rough Sea ramps pressure-based estimated wave height and related wind context over multiple samples and settles gradually when Normal operation is restored. Buoy Motion also provides separate local visual presets that never overwrite telemetry.

The presentation simulator also correlates related channels: wave height with
pressure, coordinates with anchor distance, solar input with battery
voltage/current, and enclosure temperature with fan demand. Low Battery and
Overheating now ramp gradually instead of stepping directly to their alert values.

## Local Database

The default database is `edge/data/falcon.db`. Startup performs a non-destructive additive schema migration.

- `telemetry` — raw timestamped source payloads
- `alerts` — deterministic alerts linked to telemetry
- `wave_predictions` — stored 5- and 15-minute predictions
- `system_events` — audited restart and calibration requests

Runtime database files are ignored by Git.

## Read from the ESP32

Connect the Bay Station development laptop to the configured telemetry endpoint and run:

```powershell
python -m falcon_edge.service --source esp32 --esp32-url http://192.168.4.1
```

ESP32 connection failures are reported explicitly. The service never silently replaces physical-source failures with simulated readings.

For current ESP32 USB serial bench telemetry on Linux (development transport only; deployed LoRa transport and Bay Station Internet backhaul remain pending):

```bash
python3 -m pip install -r edge/requirements-hardware.txt
python3 -m falcon_edge.service --source serial --serial-port /dev/ttyUSB0
```

The serial reader accepts only `falcon.telemetry` version 1 newline-JSON frames.

## Tests

```powershell
cd edge
python -m unittest discover -s tests -v
```

The test suite covers the two approved prediction horizons, wave-only output, sea-condition classification, invalid horizons, wave backtesting, sensor validation, and presentation alert scenarios.
