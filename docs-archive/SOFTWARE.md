# Software Architecture v6.1


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

```text
Sensors -> ESP32 acquisition/validation/event detection -> Wi-Fi/LTE
-> cloud service -> pressure processing -> storage + dashboard + optional AI
```

The ESP32 performs deterministic acquisition, engineering-unit/range checks, event detection, security debounce, watchdog handling, versioned telemetry framing, and short-outage buffering. It sends summaries and immediate event packets through Wi-Fi or LTE and continues sensing/local security while the Internet path is unavailable. USB serial remains a bench transport.

The cloud/edge service performs authenticated ingestion, stale-data detection, pressure filtering/wave estimation, event logging, storage, API/dashboard hosting, alerts, and optional isolated prediction. The final LTE module, SIM/provider, cloud endpoint, transport protocol, authentication, and deployment network remain selection gates.

Primary software sections follow the grouped schema: `system`, `wave`, `environment`, `gps`, `power`, `security`, `health`, `assistant`, and `alerts`. Missing values stay null. Every value carries or inherits timestamp, source, state, and units.

The FALCON Assistant is deterministic and rule-based. AI wave prediction is a required Overview feature, while its execution remains isolated so it cannot block monitoring. Legacy IMU/motion modules may remain for historical traceability but are not loaded by the primary dashboard or required by firmware/API tests.

Security rules use debounce/persistence. Normal wave movement alone never triggers theft. All configuration and calibration actions must be logged.

Run tests with `PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v`; build the dashboard with Node.js 20.19+ using `npm run build` in `dashboard-next/`.
