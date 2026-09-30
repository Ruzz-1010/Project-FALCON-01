# Software Architecture v6.1

```text
Sensors -> ESP32 acquisition/validation -> LoRa primary
-> barangay-hall gateway/Bay Station -> pressure processing -> SQLite + AI
-> local REST API/dashboard -> SIM/4G/5G Internet -> cloud/remote access
```

The ESP32 performs deterministic acquisition, engineering-unit/range checks, security debounce, watchdog handling, versioned telemetry framing, LoRa transport, and short-outage buffering. It sends compact telemetry to the verified barangay-hall gateway and continues sensing/local security while the LoRa path is unavailable. USB serial remains a bench transport until the deployed LoRa link is selected and implemented.

The shore Bay Station performs authenticated LoRa ingestion, stale-data detection, pressure filtering/wave estimation, event aggregation, SQLite storage, API/dashboard hosting, alerts, required isolated AI prediction, and cloud/remote synchronization over its SIM/4G/5G Internet backhaul. The final mini PC, LoRa module/gateway, SIM/provider, cloud endpoint, transport protocol, authentication, and deployment network remain selection gates.

Primary software sections follow the grouped schema: `system`, `wave`, `environment`, `gps`, `power`, `security`, `health`, `assistant`, and `alerts`. Missing values stay null. Every value carries or inherits timestamp, source, state, and units.

The FALCON Assistant is deterministic and rule-based. AI wave prediction is a required Overview feature, while its execution remains isolated so it cannot block monitoring. Legacy IMU/motion modules may remain for historical traceability but are not loaded by the primary dashboard or required by firmware/API tests.

Security rules use debounce/persistence. Normal wave movement alone never triggers theft. All configuration and calibration actions must be logged.

Run tests with `PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v`; build the dashboard with Node.js 20.19+ using `npm run build` in `dashboard-next/`.
