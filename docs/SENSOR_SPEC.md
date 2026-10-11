# Sensor Specification v9.1

<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

| Group | Channel | Output | Required truth label | Notes |
| --- | --- | --- | --- | --- |
| Core | Low-range submersible water pressure transmitter, 4–20 mA preferred | raw loop current, raw/filtered kPa, baseline, optional depth, estimated wave height | CANDIDATE; EXACT CONFIGURATION, SEAWATER SUITABILITY, AND CALIBRATION REQUIRED | Primary research signal. Use 0–1 mH2O or 0–2 mH2O unless depth review requires otherwise. |
| Core | Wind speed | speed, unit, quality state | LIVE after calibration or SIMULATED during bench demo | Required after DOST revision. Compare against a reference anemometer. |
| Core | Wind direction | heading/degrees/cardinal direction, quality state | LIVE after calibration or SIMULATED during bench demo | Align north and record mounting offset. |
| Core support | GPS position/time/security | latitude, longitude, fix, satellites, geofence distance/state, timestamp | LIVE or SIMULATED | Required for exact position, drift/security validation, and time support. |
| Core support | Battery/solar monitor | voltage, current, power, charging state, low-battery event | LIVE or SIMULATED | Used to validate small battery and solar sizing. |
| Core communication | Wi-Fi/LTE cloud link | signal/registration state, reconnect state, packet status | LIVE or SIMULATED | Wi-Fi for lab/near-shore; LTE for remote field. LoRa is fallback only. |
| Core support | Local buffer | queued record count, oldest/newest timestamp, replay status | LIVE or SIMULATED | Required for field trial when internet is intermittent. |
| Optional event/security | MPU6050, SW-420, reed/enclosure switch | tilt, vibration, lid-open, tamper state | LIVE, SIMULATED, or OPTIONAL | Adds event detection; not a substitute for pressure. |
| Optional context | DS18B20 water temperature | temperature, unit, quality state | LIVE, SIMULATED, or OPTIONAL | Context only; not a primary research result. |

BNO085, salinity/conductivity, pH, dissolved oxygen, turbidity, camera, Raspberry Pi buoy computer, and load-cell mooring tension are excluded from the low-cost minimum build. Pressure alternatives include 0–5 V/0–10 V, RS485/Modbus, and marine digital sensors, subject to the same range, sealing, seawater, and calibration gates. Every active channel requires units, range, sampling target, wiring, calibration, invalid/stale behavior, timestamp, and physical test evidence.
