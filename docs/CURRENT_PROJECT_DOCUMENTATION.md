# Current Project Documentation v6.0

Project FALCON is now a pressure-based smart coastal observation buoy. The authoritative scope, architecture, sensor groups, truthful claims, validation requirements, and implementation status are in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

## Current implemented software

- ESP32 PlatformIO firmware shell and local diagnostic portal.
- Versioned newline-JSON serial telemetry prototype.
- Python Orange Pi-targeted edge service with simulator and serial source.
- SQLite telemetry, alerts, prediction compatibility records, and operator events.
- Grouped `/api/telemetry/current` contract plus legacy endpoints.
- Pressure fields, simulated wave estimate, geofence/tamper scenarios, deterministic alerts, and rule-based assistant.
- Water-temperature monitoring through a sealed DS18B20; physical reference comparison remains pending.
- Responsive four-page dashboard: Overview, Buoy Motion, Sensors, Logs & Alerts; settings is an icon. Sensors are simplified into six operator-facing groups, with research diagnostics hidden behind expandable details.

## Current physical status

Most final sensors, the Orange Pi, PCB, waterproof enclosure, solar system, and complete buoy have not been physically integrated or field-validated. The current simulator is for software demonstration. The pressure-to-wave method, water-temperature channel, geofence thresholds, and tamper thresholds require reference calibration/testing.

## Adviser changes applied

- BNO085 removed from the required Phase 1 baseline; old motion files remain only as deprecated optional prototypes.
- Load cell/HX711 and anchor-chain tension sensing removed.
- Pressure sensor is the primary wave input; output is **estimated wave height**.
- Sealed DS18B20 water-temperature channel retained; conductivity/salinity removed from the required Phase 1 scope.
- GPS geofence, tamper input, enclosure switch, and buzzer security concept added.
- AI made optional and hidden by default.
- Dashboard consolidated to four primary pages while retaining motion as an optional visualization.

## Run and verify

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01"
PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v
cd dashboard-next && npm run build
cd ../edge && python3 -m falcon_edge.service
```

Open `http://127.0.0.1:8765/`. Use Node.js 20.19+ only when running the Vite development server.

## Next engineering gates

1. Finalize exact TBD part models and datasheets.
2. Freeze new adviser-approved wiring/pinout/PCB revision.
3. Connect and bench-test the physical Bar02 pressure sensor.
4. Define and execute pressure baseline and wave-reference calibration.
5. Implement and test real geofence/tamper persistence.
6. Install and harden the Orange Pi service.
7. Complete waterproofing, power-budget, endurance, and controlled coastal tests.
8. Evaluate optional AI only after traceable calibrated data exists.
