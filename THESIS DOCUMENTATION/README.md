# Project FALCON Thesis Documentation Register

## Current authority

- `BayStation.docx` — canonical adviser-aligned V3.7 thesis documentation.
- `../docs/PROJECT_CONTEXT.md` — canonical repository context v7.0.
- `../docs/BAY_STATION_ARCHITECTURE.md` — approved functional split.
- `../docs/BAY_STATION_SELECTION_REGISTER.md` — unresolved decisions and release gates.

## Superseded records

Other V2/V3 DOCX files in this directory are retained for historical traceability and must not override the Bay Station architecture. They may contain obsolete Orange Pi-on-buoy, USB-only deployment, five-page dashboard, BNO085, load-cell, optional-AI, power, or prototype assumptions.

## Current non-negotiable boundaries

- No mini PC is installed on or powered by the buoy.
- The buoy contains ESP32, approved sensors, LTE/cellular telemetry, power, and security electronics.
- The shore Bay Station performs storage, pressure-wave processing, required AI prediction, API/dashboard hosting, and alerts.
- The dashboard has four primary pages: Overview, Buoy Motion, Sensors, and Logs & Alerts.
- Simulator/build/test results are not physical accuracy, cellular reliability, AI accuracy, or deployment-readiness evidence.
