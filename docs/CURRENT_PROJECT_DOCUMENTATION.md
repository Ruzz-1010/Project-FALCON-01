# Current Project Documentation v6.1

Project FALCON is now a pressure-based smart coastal observation buoy. The authoritative scope, architecture, sensor groups, truthful claims, validation requirements, and implementation status are in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

## Current implemented software

- ESP32 PlatformIO firmware shell and local diagnostic portal.
- Versioned telemetry framing and USB serial bench prototype; deployed LTE transport remains pending modem/protocol selection.
- Python shore Bay Station service prototype with simulator and bench serial source.
- SQLite telemetry, alerts, prediction compatibility records, and operator events.
- Grouped `/api/telemetry/current` contract plus legacy endpoints.
- Pressure fields, simulated wave estimate, geofence/tamper scenarios, deterministic alerts, and rule-based assistant.
- Water-temperature monitoring through a sealed DS18B20; physical reference comparison remains pending.
- Responsive four-page dashboard: Overview, Buoy Motion, Sensors, Logs & Alerts; settings is an icon. GPS/security is grouped under Sensors and summarized on Overview.

## Current physical status

Most final sensors, LTE modem, shore Bay Station mini PC, revised PCB, waterproof enclosure, solar system, and complete buoy have not been physically integrated or field-validated. The current simulator is for software demonstration. The pressure-to-wave method, water-temperature channel, geofence/tamper thresholds, cellular recovery, and AI accuracy require controlled testing.

The physical and visual prototype is now **under redesign**. All existing mechanical CAD, dimensions, enclosure layouts, component placements, renders, dashboard models, and video reference images are retained only as references until replaced and approved under [PROTOTYPE_REDESIGN_BASELINE.md](PROTOTYPE_REDESIGN_BASELINE.md).

## Adviser changes applied

- BNO085 removed from the required Phase 1 baseline; old motion files remain only as deprecated optional prototypes.
- Load cell/HX711 and anchor-chain tension sensing removed.
- Pressure sensor is the primary wave input; output is **estimated wave height**.
- Sealed DS18B20 water-temperature channel retained; conductivity/salinity removed from the required Phase 1 scope.
- GPS geofence, tamper input, enclosure switch, and buzzer security concept added.
- AI wave prediction made a required, always-visible Overview feature while remaining isolated from live monitoring failures.
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

1. Define and approve the replacement prototype geometry and component placement.
2. Finalize exact TBD part models and datasheets.
3. Freeze new wiring/pinout/PCB revision after physical-fit review.
4. Connect and bench-test the physical Bar02 pressure sensor.
5. Define and execute pressure baseline and wave-reference calibration.
6. Implement and test real geofence/tamper persistence.
7. Select/integrate the LTE modem and install/harden the shore Bay Station service.
8. Complete waterproofing, power-budget, endurance, and controlled coastal tests.
9. Validate the implemented AI wave-prediction baseline using traceable calibrated data before reporting prediction accuracy.
