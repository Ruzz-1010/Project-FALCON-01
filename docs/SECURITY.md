# Anti-Theft and Tamper Security v6.1


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

FALCON uses GPS geofence persistence, a generic vibration/tamper input, an enclosure reed/limit switch, and a buzzer. Exact tamper and switch parts remain TBD.

States are `SECURE`, `WARNING`, `ALERT`, and `DISARMED`. A momentary GPS error or ordinary wave movement enters evaluation/debounce, not an immediate theft alert. `ALERT` requires a persistent geofence violation, persistent tamper input, or enclosure opening while armed. Authorized maintenance uses `DISARMED` and is logged.

Validation must document geofence radius, GPS accuracy, persistence time, input debounce, buzzer behavior, false positives under wave-like motion, deliberate tamper detection, enclosure access, communication loss, and recovery. This is a prototype deterrence/notification feature, not a certified security system.
