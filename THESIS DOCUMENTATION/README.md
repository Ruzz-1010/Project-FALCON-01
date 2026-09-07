# Project FALCON Thesis Documentation Register

## Current authority

- `BayStation.docx` — canonical adviser-aligned thesis documentation with the wave-and-wind-only Phase 1 measurement scope.
- `PROJECT FALCON-01 - V3 Documentation.docx` — filename-compatible copy of the
  canonical Bay Station V3.7 thesis; it is retained for users who open the
  earlier V3 filename.
- `../docs/PROJECT_CONTEXT.md` — canonical repository context v8.0.
- `../docs/BAY_STATION_ARCHITECTURE.md` — approved functional split.
- `../docs/BAY_STATION_SELECTION_REGISTER.md` — unresolved decisions and release gates.

## Superseded records

Other V2/V3 DOCX files in this directory, including
`PROJECT FALCON-01 - V3 Documentation - LEGACY.docx`, are retained for
historical traceability and must not override the Bay Station architecture.
They may contain obsolete Orange Pi-on-buoy, USB-only deployment, five-page
dashboard, BNO085, load-cell, optional-AI, power, or prototype assumptions.

## Current non-negotiable boundaries

- No mini PC is installed on or powered by the buoy.
- The buoy contains ESP32, approved sensors, LTE/cellular telemetry, power, and security electronics.
- The shore Bay Station performs storage, pressure-wave processing, required AI prediction, API/dashboard hosting, and alerts.
- The dashboard has four primary pages: Overview, Buoy Motion, Sensors, and Logs & Alerts.
- Simulator/build/test results are not physical accuracy, cellular reliability, AI accuracy, or deployment-readiness evidence.
- The only primary Phase 1 sensors are pressure-derived wave sensing and wind speed/direction. GPS, power, timestamps, and security states are supporting telemetry; water temperature and other environmental sensors are excluded.
