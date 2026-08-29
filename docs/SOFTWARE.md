# Software Architecture v6.1

```text
ESP32 drivers/acquisition -> versioned USB/UART telemetry -> Orange Pi ingestion
-> validation/filtering -> SQLite -> REST API -> five-page local dashboard
```

The ESP32 performs deterministic acquisition, calibration application, range checks, security input debounce, watchdog handling, and serial framing. It must continue sensing when the Orange Pi is unavailable.

The Orange Pi performs ingestion, stale-data detection, pressure filtering/wave estimation, GPS geofence persistence, event aggregation, SQLite storage, API/dashboard hosting, and optional isolated model inference.

Primary software sections follow the grouped schema: `system`, `wave`, `environment`, `gps`, `power`, `security`, `health`, `assistant`, and `alerts`. Missing values stay null. Every value carries or inherits timestamp, source, state, and units.

The FALCON Assistant is deterministic and rule-based. AI wave prediction is a required Overview feature, while its execution remains isolated so it cannot block monitoring. Legacy IMU/motion modules may remain for historical traceability but are not loaded by the primary dashboard or required by firmware/API tests.

Security rules use debounce/persistence. Normal wave movement alone never triggers theft. All configuration and calibration actions must be logged.

Run tests with `PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v`; build the dashboard with Node.js 20.19+ using `npm run build` in `dashboard-next/`.
