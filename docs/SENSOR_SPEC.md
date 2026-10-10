# Sensor Specification v9.0


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

| Group | Channel | Output | Required truth label |
| --- | --- | --- | --- |
| Core | Low-range submersible pressure transmitter; 4–20 mA preferred | raw loop current, raw/filtered kPa, baseline, optional depth, estimated wave height | CANDIDATE; EXACT CONFIGURATION, SEAWATER SUITABILITY, AND CALIBRATION REQUIRED |
| Optional/supporting | Wind speed | speed and units | LIVE or SIMULATED; retain only if scope requires it |
| Optional/supporting | Wind direction | direction/heading | LIVE or SIMULATED; retain only if scope requires it |
| Supporting telemetry | GPS position/time | latitude, longitude, fix, satellites, geofence distance/state | LIVE or SIMULATED; not a primary measurement |
| Supporting telemetry | Battery/solar monitor | voltage, current, power, charging state | LIVE or SIMULATED; power validation only |
| Optional health/security | Enclosure temperature, tamper, enclosure switch | diagnostic and security state | LIVE, SIMULATED, or OPTIONAL |

BNO085, salinity/conductivity, and load-cell/HX711 mooring tension are excluded from the low-cost minimum build. Water temperature is optional supporting context only. Pressure alternatives include 0–5 V/0–10 V, RS485/Modbus, and marine digital sensors, subject to the same range, sealing, seawater, and calibration gates. Every channel requires units, range, sampling target, wiring, calibration, invalid/stale behavior, timestamp, and physical test evidence.
