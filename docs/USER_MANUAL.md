# FALCON Operator User Manual v6.1


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

## Purpose

Use the local FALCON dashboard to inspect current station readings, visualize pressure-based buoy movement, review grouped sensors, and examine logs or alerts.

## Start the local station

```bash
cd "/home/ruzz/Documents/PlatformIO/Projects/Project FALCON-01/edge"
python3 -m falcon_edge.service
```

Open <http://127.0.0.1:8765/> on the development laptop. On deployment, use the approved cloud, institutional, or remote endpoint configured by the team.

## Source labels

- `LIVE`: received from connected hardware.
- `SIMULATED`: software-generated development data.
- `ESTIMATED`: calculated from another reading; wave height is estimated from pressure.
- `CALIBRATION REQUIRED`: do not make accuracy claims yet.
- `STALE` or `OFFLINE`: the reading is not current or unavailable.
- `OPTIONAL`: not required for core monitoring.

Never hide or reinterpret these labels.

## Main pages

1. **Overview:** read estimated wave height and the station summary for wind, pressure, GPS security, battery, solar, and temperature.
2. **Buoy Motion:** view the optional pressure-driven 3D model. `Current Data` follows the received estimate. `Calm`, `Moderate`, `Rough`, and `Pressure Offline` are labeled local demonstrations and do not modify telemetry. The visible buoy is a reference model under redesign.
3. **Sensors:** open a group and use **View Details** when technical quality, freshness, calibration, or source information is needed.
4. **Logs & Alerts:** review active conditions and stored events. Acknowledgement records that an operator saw an alert; it does not erase the evidence.

Settings is opened from the header icon. FALCON AI wave prediction is always visible on Overview; it is a research estimate and not an official marine forecast.

## ESP32 diagnostic portal

The ESP32 may expose a small setup/diagnostic portal at `http://192.168.4.1` while connected to its configured access point. This portal is not the full dashboard and must not substitute simulated diagnostic values for edge-service telemetry.

## Limits

FALCON is a research prototype, not an official weather, navigation, storm, tsunami, or emergency-warning service. Report persistent offline, calibration, geofence, enclosure, battery, or thermal states to the responsible project operator and follow the approved maintenance procedure.
