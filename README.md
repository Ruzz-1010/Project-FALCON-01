# Project FALCON-01

**Fullbright College's AI-powered Live Coastal Observation Network**

Project FALCON is a Phase 1 coastal monitoring buoy prototype focused on two outcomes:

1. real-time coastal monitoring; and
2. AI-assisted wave-height prediction 5–15 minutes ahead.

The AI scope is limited to short-term wave-height prediction and sea-condition classification as **Calm**, **Moderate**, or **Rough**.

## Source of Truth

[PROJECT_CONTEXT.md v5.0](docs/PROJECT_CONTEXT.md) is the official engineering source of truth.

Working source code remains authoritative for what is currently implemented. Documentation describes both the verified prototype and the approved Phase 1 target; it does not turn planned hardware into implemented hardware.

## Current Status

Status: **Phase 1 Prototype**

Implemented in the repository:

- PlatformIO ESP32 Arduino firmware;
- `FALCON-01` Wi-Fi access point and captive portal;
- LittleFS fallback dashboard and basic ESP32 controls;
- laptop-hosted Python edge-service prototype, ready to migrate to the selected Orange Pi Zero 3 (4GB);
- simulated telemetry and deterministic alert scenarios;
- local SQLite telemetry history;
- presentation forecast and backtest pipeline;
- responsive local dashboard with light/dark mode;
- current-versus-predicted forecast presentation;
- browser notifications and alert history;
- and interactive Fusion-derived 3D buoy visualization.

Current mechanical direction: a compact traditional single-body Ø650 mm HDPE buoy with a rounded 240 mm tapered underwater keel, central ballast, and single-anchor mooring. The former four-outrigger configuration is retained only as Legacy Revision 4.

### Safe frontend migration

The production dashboard in `data/` remains the verified fallback. The page-by-page React + TypeScript migration in `dashboard-next/` now includes the responsive shell plus Overview, Wave AI, Motion, GPS, Power, System Health, Alerts, Logs, and Settings. Wave AI includes current-versus-predicted results, forecast horizons, model evidence, and presentation scenarios. Motion preserves the Fusion GLB digital twin with telemetry-driven sea motion, camera controls, navigation lights, and component alert highlighting. GPS provides a live Puerto Princesa coastal map, deployment reference, geofence, and drift telemetry. Power presents battery, solar, thermal, fan, and recent-history telemetry. System Health presents local service connectivity, sensor availability, edge resource use, and diagnostics. Alerts provides live notification badges and toasts, active warnings, persisted history, severity filters, and non-destructive acknowledgement. Logs provides searchable telemetry, AI prediction, alert, and system-event archives with filtered CSV/JSON export. Settings provides local presentation preferences, notification permission, scenarios, and auditable maintenance controls.

Run the migration preview with the edge service on port `8765`:

```powershell
cd dashboard-next
npm install
npm run dev
```

Then open `http://127.0.0.1:5173`.

Important limitations:

- physical Phase 1 sensors are not yet fully integrated;
- the selected Orange Pi Zero 3 (4GB) has not yet been installed;
- the laptop currently represents the edge-computing role during demonstrations;
- simulator results are not field-validation results;
- the current presentation forecast is not the final trained AI model;
- and the 3D dashboard assets exceed the configured ESP32 LittleFS capacity.

## Approved Phase 1 Architecture

```text
Marine Sensors -> ESP32 -> UART / Wi-Fi -> Orange Pi Zero 3 (4GB)
                                             |
                                             +-> AI prediction + XAI
                                             +-> SQLite + historical data
                                             +-> REST API + web server
                                             +-> Local dashboard -> laptop / tablet / phone
```

Cloud connectivity is Future Expansion and is not required for Phase 1 operation.

## Approved Sensor Set

- BNO085 IMU;
- water-pressure sensor;
- wind-speed sensor;
- wind-direction sensor;
- GPS module;
- battery monitor;
- solar monitor;
- internal-temperature sensor;
- and optional water-temperature sensor.

pH, salinity, turbidity, dissolved oxygen, rain, UV, cameras, hydrophones, current meters, and Water Quality Index inputs are Future Expansion.

## Approved AI Outputs

- current wave height;
- predicted wave height for a 5–15 minute horizon;
- prediction confidence or quality indicator;
- prediction status and model version;
- and sea condition: Calm, Moderate, or Rough.

Weather, typhoon, storm, ocean-current, fish, maintenance, camera, and water-quality predictions are not part of Phase 1.

## Approved API Direction

```text
GET  /status
GET  /wave
GET  /gps
GET  /battery
GET  /solar
GET  /ai
POST /restart
POST /calibrate
```

Current `/api/...` endpoints are prototype compatibility routes and require a controlled migration to the approved v4 contract.

## Development Setup

### ESP32 Firmware

```powershell
platformio run
platformio run --target buildfs
platformio run --target upload
platformio run --target uploadfs
```

Close the serial monitor before uploading. Hold BOOT if required; after flashing, release BOOT and press EN/RESET.

Prototype access-point settings:

| Setting | Value |
| --- | --- |
| SSID | `FALCON-01` |
| Prototype password | `falcon123` |
| ESP32 dashboard | `http://192.168.4.1` |

The prototype password must be changed before field deployment.

### Laptop Edge-Service Demonstration

```powershell
cd "C:\Users\Admin\Documents\PlatformIO\Projects\Project FALCON-01\edge"
python -m falcon_edge.service
```

Open `http://127.0.0.1:8765/`.

Run tests:

```powershell
cd edge
python -m unittest discover -s tests -v
```

## Repository Today

```text
Project FALCON-01/
├── data/               # current dashboard assets and 3D model
├── docs/               # engineering documentation
├── edge/               # laptop/Orange Pi edge-service prototype
├── exports/            # archived CAD exchange assets
├── fusion360/          # mechanical component documentation
├── include/            # ESP32 configuration headers
├── src/                # ESP32 firmware source
├── test/               # PlatformIO test location
├── platformio.ini
└── README.md
```

The target v4 repository organization is documented in PROJECT_CONTEXT.md and will be adopted incrementally without breaking working code.

## Documentation

Start here:

1. [PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) — master engineering context;
2. [ROADMAP.md](docs/ROADMAP.md) — focused delivery gates;
3. [HARDWARE.md](docs/HARDWARE.md) — electronics and sensor baseline;
4. [SOFTWARE.md](docs/SOFTWARE.md) — firmware and edge-software boundaries;
5. [AI.md](docs/AI.md) — focused prediction and classification specification;
6. [DASHBOARD.md](docs/DASHBOARD.md) — approved information architecture;
7. [API.md](docs/API.md) — approved REST contract and migration status;
8. [MECHANICAL.md](docs/MECHANICAL.md) — approved buoy mechanical baseline;
9. [INDEX.md](docs/INDEX.md) — full documentation index.

## Engineering Principles

- Focus over feature count.
- Reliability over decoration.
- Local-first operation.
- Measured, estimated, predicted, simulated, and unavailable values must remain distinguishable.
- No field claim without calibration and evidence.
- No AI claim outside wave prediction and three-class sea-condition classification.
- Preserve working source and migrate incrementally.

## Future Expansion

Cloud synchronization, LTE, LoRa, satellite communication, multi-buoy networking, mobile applications, water-quality sensing, computer vision, additional AI models, and autonomous capabilities are outside Phase 1.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 3.1 | 2026-08-05 | Added source-verified implementation status. |
| 4.0 | 2026-08-09 | Aligned repository entry point with PROJECT_CONTEXT.md v4.0 and the focused wave-monitoring research scope. |
| 5.0 | 2026-08-13 | Adopted the single-body rounded-keel buoy baseline and retired the four-stabilizer arrangement to legacy status. |
