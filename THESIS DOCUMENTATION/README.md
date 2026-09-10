# Project FALCON Thesis Documentation Register

## Current authority

- `BayStation.docx` — canonical expanded V4 thesis documentation with the
  adviser-aligned wave-and-wind Phase 1 scope, formal Chapters 1–4, methodology,
  validation plan, risks, references, appendices, and explanatory figures.
- `PROJECT FALCON-01 - V3 Documentation.docx` — filename-compatible copy of the
  canonical Bay Station V3.7 thesis; it is retained for users who open the
  earlier V3 filename.
- `../docs/PROJECT_CONTEXT.md` — canonical repository context v8.1.
- `../docs/BAY_STATION_ARCHITECTURE.md` — approved functional split.
- `../docs/BAY_STATION_SELECTION_REGISTER.md` — unresolved decisions and release gates.
- `../docs/PRESSURE_SENSOR_BASELINE.md` — authoritative HPT604 candidate decision, interface, procurement, venting, and validation gates.

## Superseded records

Other DOCX files in this directory are supporting or legacy records. Every copy carries a dated document-control notice; any body text that conflicts with `BayStation.docx`, `PROJECT_CONTEXT.md`, or `PRESSURE_SENSOR_BASELINE.md` is superseded. Older V2/V3 files, including `PROJECT FALCON-01 - V3 Documentation - LEGACY.docx`, are retained for historical traceability and must not override the Bay Station architecture.
They may contain obsolete Orange Pi-on-buoy, USB-only deployment, five-page
dashboard, BNO085, load-cell, optional-AI, power, or prototype assumptions.

## Current non-negotiable boundaries

- No mini PC is installed on or powered by the buoy.
- The buoy contains the ESP32, approved sensors, LoRa telemetry, power, and security electronics. It has no mini PC or cellular Internet modem.
- The shore Bay Station performs storage, pressure-wave processing, required AI prediction, API/dashboard hosting, and alerts. Its separate SIM/4G/5G connection provides Internet backhaul.
- The dashboard has four primary pages: Overview, Buoy Motion, Sensors, and Logs & Alerts.
- Simulator/build/test results are not physical accuracy, cellular reliability, AI accuracy, or deployment-readiness evidence.
- The only primary Phase 1 sensors are pressure-derived wave sensing and wind speed/direction. GPS, power, timestamps, and security states are supporting telemetry; water temperature and other environmental sensors are excluded.
- The recommended long-duration pressure candidate is the Holykell HPT604 Type A, provisionally 0–2 mH2O vented gauge with 4–20 mA output. It is not yet purchased or validated; exact seawater compatibility and order details require written supplier confirmation. Bar02 is bench-only.
