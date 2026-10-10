# Current Project Documentation v9.0


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Project FALCON is now a pressure-based smart coastal observation buoy. The authoritative scope, architecture, sensor groups, truthful claims, validation requirements, and implementation status are in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

## Current implemented software

- ESP32 PlatformIO firmware shell and local diagnostic portal.
- Versioned telemetry framing and USB serial bench prototype; event-driven Wi-Fi/LTE cloud telemetry remains pending modem, endpoint, and protocol selection.
- Python edge/cloud service prototype with simulator and bench serial source.
- SQLite telemetry, alerts, prediction compatibility records, and operator events.
- Grouped `/api/telemetry/current` contract plus legacy endpoints.
- Pressure fields, simulated wave estimate, geofence/tamper scenarios, deterministic alerts, and rule-based assistant.
- Wave and wind monitoring data paths, with GPS/power/security retained only as supporting system telemetry.
- Responsive four-page dashboard: Overview, Buoy Motion, Sensors, Logs & Alerts; settings is an icon. Supporting telemetry is grouped separately from the primary wave and wind channels.

## Current physical status

Most final sensors, LTE modem, cloud endpoint, revised PCB, waterproof enclosure, solar system, and complete buoy have not been physically integrated or field-validated. The current simulator is for software demonstration. The pressure-to-wave method, event thresholds, wind channels, geofence/tamper thresholds, LTE recovery, cloud synchronization, and AI accuracy require controlled testing.

The physical and visual prototype is now **under redesign**. All existing mechanical CAD, dimensions, enclosure layouts, component placements, renders, dashboard models, and video reference images are retained only as references until replaced and approved under [PROTOTYPE_REDESIGN_BASELINE.md](PROTOTYPE_REDESIGN_BASELINE.md). The reduced wave-and-wind sensor scope is the only current proposal baseline.

## Adviser changes applied

- BNO085 removed from the required Phase 1 baseline; old motion files remain only as deprecated optional prototypes.
- Load cell/HX711 and anchor-chain tension sensing removed.
- Pressure sensor is the primary wave input; output is **estimated wave height**.
- Water-temperature, conductivity, and salinity channels removed from the required Phase 1 scope.
- GPS geofence, tamper input, enclosure switch, and buzzer security concept added.
- AI wave prediction remains optional to the low-cost minimum build and must remain isolated from live monitoring failures.
- Dashboard consolidated to four primary pages; GPS/security moved into Sensors while retaining motion as an optional visualization.

## Run and verify

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01"
PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v
cd dashboard-next && npm run build
cd ../edge && python3 -m falcon_edge.service
```

Open `http://127.0.0.1:8765/`. Use Node.js 20.19+ only when running the Vite development server.

## Next engineering gates

1. Define and approve the replacement compact can-buoy prototype geometry and component placement.
2. Finalize exact TBD part models and datasheets.
3. Freeze new wiring/pinout/PCB revision after physical-fit review.
4. Connect and bench-test the selected pressure transmitter and protected ADC loop.
5. Define and execute pressure baseline and wave-reference calibration.
6. Implement and test real geofence/tamper persistence.
7. Select/integrate the LTE modem and cloud endpoint, then verify event-driven upload, authentication, buffering, and recovery.
8. Complete waterproofing, power-budget, endurance, and controlled coastal tests.
9. Validate the implemented AI wave-prediction baseline using traceable calibrated data before reporting prediction accuracy.
