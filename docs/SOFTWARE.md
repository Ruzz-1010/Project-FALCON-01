# Software Architecture v6.1

```text
Sensors -> ESP32 acquisition/validation -> LTE/cellular telemetry -> Internet
-> shore Bay Station ingestion -> pressure processing -> SQLite + AI -> REST API -> four-page dashboard
```

The ESP32 performs deterministic acquisition, engineering-unit/range checks, security debounce, watchdog handling, versioned telemetry framing, and short-outage buffering. It must continue sensing and local security when cellular connectivity or the Bay Station is unavailable. USB serial remains a bench transport until the LTE path is selected and implemented.

The shore Bay Station performs authenticated ingestion, stale-data detection, pressure filtering/wave estimation, event aggregation, SQLite storage, API/dashboard hosting, alerts, and required isolated AI prediction. The final mini PC, LTE modem, transport protocol, authentication, and deployment network remain selection gates.

Primary software sections follow the grouped schema: `system`, `wave`, `environment`, `gps`, `power`, `security`, `health`, `assistant`, and `alerts`. Missing values stay null. Every value carries or inherits timestamp, source, state, and units.

The FALCON Assistant is deterministic and rule-based. AI wave prediction is a required Overview feature, while its execution remains isolated so it cannot block monitoring. Legacy IMU/motion modules may remain for historical traceability but are not loaded by the primary dashboard or required by firmware/API tests.

Security rules use debounce/persistence. Normal wave movement alone never triggers theft. All configuration and calibration actions must be logged.

Run tests with `PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v`; build the dashboard with Node.js 20.19+ using `npm run build` in `dashboard-next/`.
