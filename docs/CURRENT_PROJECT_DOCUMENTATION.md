# Current Project Documentation v8.2

Project FALCON is now a pressure-based smart coastal observation buoy. The authoritative scope, architecture, sensor groups, truthful claims, validation requirements, and implementation status are in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

## Current implemented software

- ESP32 PlatformIO firmware shell and local diagnostic portal.
- Versioned telemetry framing and USB serial bench prototype; deployed LoRa-primary buoy telemetry to a barangay-hall Bay Station remains pending radio, gateway, and protocol selection. SIM/4G/5G is reserved for Bay Station Internet backhaul.
- Python shore Bay Station service prototype with simulator and bench serial source.
- SQLite telemetry, alerts, prediction compatibility records, and operator events.
- Grouped `/api/telemetry/current` contract plus legacy endpoints.
- Pressure fields, simulated wave estimate, geofence/tamper scenarios, deterministic alerts, and rule-based assistant.
- Wave and wind monitoring data paths, with GPS/power/security retained only as supporting system telemetry.
- Responsive four-page dashboard: Overview, Buoy Motion, Sensors, Logs & Alerts; settings is an icon. Supporting telemetry is grouped separately from the primary wave and wind channels.

## Current physical status

Most final sensors, LoRa radio/gateway, Bay Station SIM/4G/5G backhaul, shore Bay Station mini PC, revised PCB, waterproof enclosure, solar system, and complete buoy have not been physically integrated or field-validated. The current simulator is for software demonstration. The pressure-to-wave method, wind channels, geofence/tamper thresholds, LoRa recovery, Bay Station Internet recovery, and AI accuracy require controlled testing.

The physical and visual prototype is now **under redesign**. All existing mechanical CAD, dimensions, enclosure layouts, component placements, renders, dashboard models, and video reference images are retained only as references until replaced and approved under [PROTOTYPE_REDESIGN_BASELINE.md](PROTOTYPE_REDESIGN_BASELINE.md). The reduced wave-and-wind sensor scope is the only current proposal baseline.

## Adviser changes applied

- BNO085 removed from the required Phase 1 baseline; old motion files remain only as deprecated optional prototypes.
- Load cell/HX711 and anchor-chain tension sensing removed.
- Pressure sensor is the primary wave input; output is **estimated wave height**.
- Holykell HPT604 0–2 mH2O, 4–20 mA is the recommended deployment candidate pending supplier and seawater confirmation; Bar02 is bench-only.
- Water-temperature, conductivity, and salinity channels removed from the required Phase 1 scope.
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
4. Obtain the exact HPT604 quotation/configuration, redesign its 4–20 mA interface, and bench-test the complete loop; use Bar02 only for short comparison trials.
5. Define and execute pressure baseline and wave-reference calibration.
6. Implement and test real geofence/tamper persistence.
7. Select/integrate the LoRa buoy radio and barangay-hall gateway, select the Bay Station SIM/4G/5G backhaul, then install/harden the shore Bay Station service.
8. Complete waterproofing, power-budget, endurance, and controlled coastal tests.
9. Validate the implemented AI wave-prediction baseline using traceable calibrated data before reporting prediction accuracy.
