# Sensor Specification v8.0

| Group | Channel | Output | Required truth label |
| --- | --- | --- | --- |
| Core | HPT604 Type A 0–2 mH2O 4–20 mA candidate | raw loop current, raw/filtered kPa, baseline, optional depth, estimated wave height | CANDIDATE; EXACT CONFIGURATION AND CALIBRATION REQUIRED |
| Core | Wind speed | speed and units | LIVE or SIMULATED |
| Core | Wind direction | direction/heading | LIVE or SIMULATED |
| Supporting telemetry | GPS position/time | latitude, longitude, fix, satellites, geofence distance/state | LIVE or SIMULATED; not a primary measurement |
| Supporting telemetry | Battery/solar monitor | voltage, current, power, charging state | LIVE or SIMULATED; power validation only |
| Optional health/security | Enclosure temperature, tamper, enclosure switch | diagnostic and security state | LIVE, SIMULATED, or OPTIONAL |

BNO085, water temperature, salinity/conductivity, and load-cell/HX711 mooring tension are excluded from the Phase 1 sensor scope. GPS, power, and security remain supporting telemetry only. Exact TBD models cannot be added to BOM, pinout, or PCB as final selections without datasheet review. Every primary channel requires units, range, sampling target, wiring, calibration, invalid/stale behavior, timestamp, and physical test evidence.
