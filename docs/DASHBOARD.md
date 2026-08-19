# Project FALCON Dashboard Specification v5.0

## Authority and Purpose

Authority: PROJECT_CONTEXT.md v4.0.

The local dashboard presents Phase 1 coastal measurements, wave prediction, system health, alerts, settings, and histories.

It shall remain usable without cloud connectivity.

## Current Status

Implemented prototype capabilities include:

- responsive desktop/mobile navigation;
- light and dark modes;
- presentation-readable typography;
- telemetry cards and charts;
- local browser notifications;
- alert history;
- current-versus-predicted forecast cards;
- simulated scenarios;
- dedicated sensor-status and calibration registers;
- explainable GPS/IMU displacement logic;
- a traceable AI architecture view;
- filtered historical pressure, wave, motion, wind, and prediction charts with CSV/JSON export;
- engineering telemetry for database size, link interval, packet age, sampling output, and packet loss;
- and interactive Fusion-derived 3D visualization.

The v4 dashboard simplification is implemented in the local edge dashboard. Out-of-scope sensor cards, multi-sensor predictions, and the 30-minute prediction selector have been removed.

The dashboard now consumes the approved v4 read endpoints directly. The simulator scenario route remains a clearly labeled presentation-only compatibility control.

Dashboard v5.0 also consumes `GET /prediction` and `GET /logs` as local presentation extensions. `/prediction` exposes the requested 10-minute presentation view, while durable Phase 1 prediction audit rows remain at the approved 5- and 15-minute horizons.

The overview uses consistent engineering line icons and a restrained operational-card hierarchy. Graphs are limited to meaningful trends: current versus predicted wave height plus supporting current-only wind, water-pressure, battery, and internal-temperature sparklines. Supporting graphs explicitly state that those channels are not AI predictions.

All prediction surfaces carry an experimental-research disclaimer and must not be represented as PAGASA or official-agency guidance. Simulator history is labeled `SIMULATED`, live sensor-derived wave height remains `ESTIMATED` until field validation, and model output is labeled `PREDICTED`.

## Information Architecture

### Home

Required cards:

- System Status;
- Wave Height;
- Predicted Wave Height;
- Sea Condition;
- Prediction Confidence;
- Wind Speed;
- Wind Direction;
- GPS;
- Battery;
- Solar;
- Internal Temperature;
- and Alerts.

Home shall prioritize wave state and system readiness.

### System Status

- ESP32;
- Orange Pi Zero 3 edge-host state;
- Orange Pi Zero 3;
- UART;
- API;
- monitoring state;
- sensor count;
- data source;
- last update;
- and uptime.

### Motion

- pitch;
- roll;
- yaw;
- wave motion;
- IMU calibration;
- and recent motion history.

The Motion/Buoy Motion implementation and interactive 3D behavior remain the locked visual baseline and are not modified by the engineering-page expansion.

### Sensor Status

- per-channel availability and health;
- configured or target sampling frequency;
- last-update age;
- signal-quality indicator;
- calibration readiness; and
- explicit simulator/source labeling.

### Calibration

- GPS reference;
- IMU orientation;
- pressure/depth;
- wind speed and direction;
- battery monitor; and
- solar monitor procedures.

Starting a workflow records an accepted calibration action. It does not mark a sensor scientifically calibrated without a reference instrument, operator, evidence, and approved result.

### Security Logic

GPS distance, IMU tilt, time persistence, and battery evidence produce an explainable research assessment: Normal, Anchor Swing, Equipment Displacement, or Possible Theft. The page is not a certified theft detector and requires human confirmation.

### AI Architecture

The page documents the unchanged pipeline: Sensors → ESP32 → Orange Pi → SQLite → Feature Engineering → AI Prediction → Explainable AI → Dashboard. Cloud, LTE, satellite, remote monitoring, and additional sensors are labeled future interfaces and are not implemented.

### Historical Data

The local archive provides date filtering, charts for pressure, wave height, motion, wind, and predictions, plus CSV and JSON export. Source/state labels remain part of exported evidence.

### GPS

- latitude;
- longitude;
- fix;
- satellites;
- reference location;
- anchor distance;
- and drift status.

### Power

- battery voltage;
- battery current;
- battery percentage;
- solar voltage;
- solar current;
- charging state;
- and power alerts.

### Internal Temperature

- current enclosure temperature;
- warning/critical threshold state;
- and cooling state only when hardware is installed.

### Alerts

- active alerts;
- severity;
- code;
- subsystem;
- timestamp;
- message;
- and history.

### Settings

- sampling settings;
- alert thresholds;
- calibration;
- theme preference;
- and authorized restart.

Unimplemented settings shall be disabled or labeled Planned.

### Logs

- Wave History;
- Prediction History;
- and System Logs.

## Wave Presentation

Current wave height shall be labeled measured or estimated according to the implemented method.

Predicted wave height shall display:

- current value;
- predicted value;
- 5-, 10-, or 15-minute displayed horizon;
- signed change;
- direction;
- confidence;
- model status;
- and sample count/context.

The dashboard shall not show a prediction without a horizon.

Thirty-minute prediction shall be removed from the Phase 1 interface.

## Sea Condition

Valid displayed classes:

- Calm;
- Moderate;
- Rough.

Unavailable data shall show Unavailable, not a fabricated class.

## Data Labels

Every view shall distinguish:

- LIVE SENSOR;
- ESTIMATED;
- PREDICTED;
- SIMULATED;
- PRESENTATION MODEL;
- STALE;
- and UNAVAILABLE.

## Status System

Green:

- healthy;
- online;
- within normal bounds.

Amber:

- warning;
- reduced confidence;
- planned attention.

Red:

- critical;
- failed;
- unsafe operating threshold.

Color shall be accompanied by text/iconography.

## Notifications

Notifications shall be visible in light and dark modes.

They shall include severity and a concise message.

Repeated identical alerts shall be rate-limited.

Browser-notification permission shall remain user controlled.

The Activity/Alerts view shall retain the complete local record available from the API.

## Responsive Requirements

### Desktop

- sidebar navigation;
- user-controlled expanded or compact icon-only sidebar with persisted preference;
- multi-column summary;
- readable projector typography;
- persistent but non-obstructive controls;
- and full chart/table layouts.

### Tablet

- drawer navigation where appropriate;
- two-column sensor cards;
- stacked complex panels;
- and touch-friendly controls.

### Mobile

- single-row compact header;
- slide-out navigation drawer;
- one-column summary cards on narrow screens;
- stacked sensor/detail panels;
- horizontally scrollable wide tables;
- 3D viewport sized to the screen;
- and demo controls placed after content rather than covering it.

## Accessibility and Readability

- readable contrast in both themes;
- minimum practical presentation typography;
- keyboard-visible focus;
- touch targets around 40 px or larger;
- semantic buttons and labels;
- reduced-motion support;
- and no information conveyed by color alone.

## 3D Digital Twin

The digital twin may display:

- approved buoy geometry;
- sensor component locations;
- pitch/roll/yaw motion;
- approximate wave response;
- antenna/navigation lights;
- thermal highlighting;
- and sensor-fault highlighting.

It shall not imply exact physics unless driven by calibrated data.

The anchor may be hidden in the dashboard view for visual clarity while remaining part of the mechanical baseline.

## API Dependency

The dashboard target endpoints are:

- `GET /status`;
- `GET /wave`;
- `GET /gps`;
- `GET /battery`;
- `GET /solar`;
- `GET /ai`;
- `POST /restart`;
- and `POST /calibrate`.

Prototype compatibility routes may remain during migration.

The GPS page plots the live `/gps` position, deployment reference, 10 m geofence, and drift line on an interactive OpenStreetMap layer. Map tiles require internet access; telemetry overlays and the explicit offline state remain available when tiles cannot load. The packaged Puerto Princesa City, Palawan coast point is a demo reference, not a surveyed deployment coordinate.

## Performance

- local assets should not require public CDNs;
- telemetry polling shall avoid overlapping requests;
- charts shall cap retained display points;
- 3D rendering shall cap pixel ratio;
- and missing assets shall produce clear states.

## Dashboard Test Matrix

- desktop dark mode;
- desktop light mode;
- tablet dark mode;
- tablet light mode;
- mobile dark mode;
- mobile light mode;
- live data;
- simulated data;
- missing sensor;
- stale API;
- critical alert;
- current/predicted comparison;
- 3D load failure;
- keyboard navigation;
- and reduced motion.

## Future Expansion

Cloud dashboards, mobile applications, fleet views, water-quality pages, camera feeds, additional prediction pages, and remote user management are outside Phase 1.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 4.0 | 2026-08-09 | Created focused local-dashboard specification aligned with v4 monitoring and wave-prediction scope. |
| 4.1 | 2026-08-09 | Implemented the focused responsive interface and migrated it to the approved v4 data endpoints. |
| 4.2 | 2026-08-09 | Refined presentation hierarchy, replaced symbolic icons with SVG engineering icons, and added transparent supporting-sensor trend graphs. |
| 5.0 | 2026-08-09 | Promoted the redesigned marine operations interface and simplified the Wave AI result while preserving the Motion/3D standard. |
| 5.1 | 2026-08-09 | Completed Mission Control, flagship Wave Intelligence, GPS, Power, System, Alerts, Logs, Settings, exports, and responsive operational components; restored Motion as the locked visual standard. |
