# Dashboard Specification v6.0

The Orange Pi-hosted `dashboard-next/` application has four primary pages: **Overview**, **Buoy Motion**, **Sensors**, and **Logs & Alerts**. Settings is a compact header action.

Overview uses two large cards only: a pressure-based estimated-wave chart and a readable Station Status summary for wind, pressure, GPS security, battery, solar, and water/enclosure temperature. Optional AI controls are removed from the main screen and kept only as advanced settings. The FALCON Assistant assets are preserved for later design work but the assistant is not currently mounted in the operator dashboard. Buoy Motion retains the interactive 3D model and remains clearly labeled as visualization-only rather than an IMU measurement. Sensors groups individual hardware devices into six user-facing monitoring categories—Wave & Pressure, GPS & Security, Wind, Water, Power, and System—to improve readability while preserving detailed technical diagnostics through expandable views. Logs & Alerts combines active alerts with persisted telemetry, security/calibration events, search, acknowledgement, and export.

All values must distinguish `LIVE`, `SIMULATED`, `ESTIMATED`, `CALIBRATION REQUIRED`, `STALE`, `OFFLINE`, and `OPTIONAL`. Optional AI is absent from the default operator view. The former separate Wave, GPS, Power, System, History, and Alerts modules are legacy implementation files and are not primary navigation.

The dashboard must remain responsive at 320 px and above, keyboard usable, readable in light/dark themes, and functional when optional AI is unavailable.
