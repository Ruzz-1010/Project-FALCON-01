# Dashboard Specification v6.0

The Orange Pi-hosted `dashboard-next/` application has four primary pages: **Overview**, **Buoy Motion**, **Sensors**, and **Logs & Alerts**. Settings is a compact header action.

Overview presents pressure-based estimated wave height and calibration state, filtered pressure, optional AI toggle, water/environment status, GPS geofence, battery/solar, security, system health, active alerts, the optional rule-based FALCON Assistant, and a compact animated buoy preview. Buoy Motion provides the larger interactive 3D model. Both motion scenes are driven by estimated sea context and labeled visualization-only; they are not presented as IMU measurements. Sensors groups core, supporting, health, and security channels. Logs & Alerts combines active alerts with persisted telemetry, security/calibration events, search, acknowledgement, and export.

All values must distinguish `LIVE`, `SIMULATED`, `ESTIMATED`, `CALIBRATION REQUIRED`, `STALE`, `OFFLINE`, and `OPTIONAL`. Optional AI is hidden by default. The former separate Wave, GPS, Power, System, History, and Alerts modules are legacy implementation files and are not primary navigation.

The dashboard must remain responsive at 320 px and above, keyboard usable, readable in light/dark themes, and functional when optional AI is unavailable.
