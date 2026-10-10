# Project FALCON Master Context v9.0 — Event Driven Cloud Buoy Baseline


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

## Document control

| Field | Current approved value |
| --- | --- |
| Project | Project FALCON-01 |
| Project type | Solar-powered smart coastal observation buoy |
| Status | Undergraduate Phase 1 prototype; hardware integration pending |
| Authority | Master repository source of truth |
| Bay Station | Cloud dashboard/API; local laptop may be used for development and offline review |
| Controller | ESP32 |
| Primary wave method | Pressure-based estimated wave height |
| AI | Required Bay Station short-term wave-height prediction; validation pending |
| Telemetry | Event-driven Wi-Fi/LTE upload from buoy to cloud; exact modem, protocol, provider, and endpoint TBD |
| Adviser revision | 2026-10-09 |
| Physical prototype | UNDER REDESIGN; geometry and placement TBD |

This file supersedes older Orange Pi-on-buoy, LoRa-primary, USB-only deployment, BNO085, anchor-chain load-cell, and multi-environmental-sensor descriptions. The cloud data path and event-driven reporting are the revised architecture. Working code remains the authority for implemented behavior. Planned hardware must not be described as installed or field-validated.

The system-function baseline remains approved, but the physical and visual prototype is being replaced. `PROTOTYPE_REDESIGN_BASELINE.md` governs that work. Existing CAD, renderings, dashboard models, dimensions, enclosure layouts, solar arrangements, and component positions are reference material only until the replacement passes its acceptance checklist.

## Project definition

Project FALCON is a low-cost, modular, solar-powered coastal observation buoy intended to measure pressure-derived wave conditions and, if retained in the approved scope, wind. An ESP32 buoy node acquires and validates measurements locally, calculates short-window summaries, and sends event-driven packets through Wi-Fi during laboratory tests or a 4G/LTE modem during a remote coastal trial. The buoy buffers records during outages and uploads them after reconnection. The cloud service stores records, serves the dashboard, and may run heavier processing. No mini PC or LoRa gateway is required for the revised minimum build.

The core undergraduate contribution is the integration and evaluation of an accessible local coastal-monitoring prototype. The system estimates wave height from calibrated underwater-pressure variations. It does not claim direct laboratory-grade wave measurement, official forecasting, navigation control, or disaster-warning capability.

## Objectives

1. Design a serviceable solar-powered coastal buoy with passive single-anchor mooring.
2. Acquire timestamped pressure and wind measurements with supporting position, power, security, and health telemetry.
3. Filter and calibrate underwater pressure to produce an explicitly labeled estimated wave height.
4. Detect persistent GPS geofence, vibration/tamper, and enclosure-access events without treating normal wave motion as theft.
5. Transmit event-driven telemetry to a cloud API for storage, processing, alerts, and a simple dashboard.
6. Evaluate accuracy, reliability, latency, power use, usability, and false-alert behavior through documented tests.
7. Develop and evaluate required short-term AI wave prediction against a documented non-AI baseline using chronological held-out data.

## Research gap and novelty

Many low-cost educational systems demonstrate individual marine sensors or generic IoT dashboards. Commercial observation buoys may be inaccessible to small schools because of acquisition cost, proprietary interfaces, and maintenance requirements. FALCON investigates an affordable local-first combination of pressure-based wave estimation and wind monitoring, supported by solar power, local logging, security telemetry, and a transparent dashboard for controlled Philippine coastal trials. Novelty must be claimed as integration and evaluation, not invention of the sensors or official ocean forecasting.

## Approved Phase 1 architecture

```text
Pressure / optional wind sensors
                              |
                            ESP32
                              |
              local sampling, summaries, event detection
                              |
                   Wi-Fi (lab) or 4G/LTE (field)
                              |
                    cloud API / database / dashboard
                              |
                       laptop / tablet / phone
```

The buoy samples continuously but transmits one-minute summaries every 1–5 minutes during normal operation. It sends an immediate event packet for a significant pressure or movement change, displacement, tamper, low battery, sensor fault, or Internet recovery. If the Wi-Fi/LTE path is unavailable, the ESP32 buffers records locally and preserves original timestamps. The cloud performs ingestion, storage, pressure processing, dashboard presentation, alerts, and optional heavier prediction. Wi-Fi remains a bench transport; LTE coverage, modem power peaks, cloud endpoint, authentication, and data plan require site-specific testing and approval.

## Sensor baseline

### Primary project sensors

- Approved low-range submersible pressure transmitter: raw pressure and pressure-based wave estimation; 4–20 mA is the preferred field interface, with 0–5 V, 0–10 V, and RS485/Modbus as documented alternatives.
- Wind-speed sensor: local wind-speed context.
- Wind-direction sensor: local wind-direction context.

### Supporting system telemetry

- GPS receiver: position, time, and geofence state required for deployment and security; it is not a primary environmental measurement.
- Battery and solar voltage/current/state: power-health telemetry required to evaluate autonomy; these are not additional environmental sensors.
- Enclosure temperature, tamper input, and enclosure switch: optional system-health/security inputs, not project measurement objectives.
- Water temperature, conductivity, salinity, and other environmental channels are excluded from the required Phase 1 scope. Legacy API fields may remain temporarily for software compatibility but are not displayed, procured, or evaluated.

### System-health sensors

- Battery voltage/current/state estimate.
- Solar voltage/current/charging state.
- Electronics-enclosure temperature.

### Security inputs

- GPS geofence with configured reference point, radius, and persistence.
- Generic vibration/tamper input; exact part is TBD.
- Enclosure reed or limit switch; exact part is TBD.
- Buzzer output for local alert indication.

### Deprecated or excluded from the required baseline

- BNO085 IMU: deprecated as a required Phase 1 sensor. Old code/visualization may remain only as a clearly labeled optional historical prototype and must not be required by the API, dashboard, BOM, objectives, or validation plan.
- Load cell/HX711/anchor-chain tension measurement: removed. FALCON uses passive mooring. Mooring line scope must allow tides, waves, and ordinary movement.
- On-buoy AI or mini PC: excluded. Optional prediction runs in the cloud or development computer and must never block acquisition.

## Pressure-based estimated wave height

The pressure sensor measures underwater pressure variation. The pipeline retains raw pressure, rejects invalid samples, applies filtering, establishes a calibration baseline at a documented installation depth, optionally estimates depth, and converts the dynamic pressure component into an estimated wave-height signal. The implementation and thesis must expose:

- raw pressure and units;
- filtered pressure;
- pressure baseline;
- optional estimated depth;
- estimated wave height and units;
- validity/quality state;
- timestamp and source;
- calibration state and calibration record.

Pressure is a direct sensor reading. Wave height is an estimate derived from pressure and calibration. Simulator values are not physical measurements. The method requires comparison with a documented reference during controlled tests before accuracy claims are made.

## Security behavior

Security state is one of `SECURE`, `WARNING`, `ALERT`, or `DISARMED`.

- `SECURE`: inside geofence, enclosure closed, no persistent tamper input.
- `WARNING`: transient or uncertain event requiring persistence/debounce.
- `ALERT`: persistent geofence violation, vibration/tamper event, or enclosure opening while armed.
- `DISARMED`: authorized maintenance mode.

Normal wave-driven motion must not generate an alert by itself. Geofence and tamper thresholds, debounce intervals, persistence duration, maintenance controls, and false-positive tests must be documented before deployment.

## Dashboard information architecture

Four primary navigation pages are approved:

1. **Overview** — one large estimated-wave chart, one Station Status card containing wind, pressure, GPS security, battery, solar, and enclosure-health telemetry, and one always-visible FALCON AI short-term wave-prediction card.
2. **Buoy Motion** — optional 3D visual model whose water-surface amplitude, heave, and tilt are generated from pressure-based estimated wave height; GPS may provide heading context. It has no required IMU, roll, or pitch measurement channel. It includes Current Data plus clearly labeled Calm, Moderate, Rough, and Pressure Offline presentation scenarios. The scenarios are local visual presets and do not modify stored or live telemetry.
3. **Sensors** — three readable operator groups: Wave & Pressure, Wind, and Supporting Telemetry. Exact device models, sampling, quality, freshness, and calibration diagnostics remain available through expandable details.
4. **Logs & Alerts** — active alerts, persisted telemetry, security events, calibration events, operator actions, search, and export. It remains the final sidebar item.

Settings are available through a compact icon and are not a primary navigation item. The former separate Wave, GPS, Power, System, History, and Alerts pages remain consolidated. Motion is retained strictly as an optional visual model and does not restore BNO085 as a required sensor.

## FALCON Assistant

The assistant is a saved optional animated, rule-based visual status aid and is currently hidden from the dashboard while its final design is being reviewed. It is not a chatbot, language model, voice assistant, or autonomous controller. States are `IDLE/NORMAL`, `WARNING`, `ALERT`, and `OFFLINE`. Messages must be short, factual, and derived from deterministic station rules. It must never issue an official safety advisory or replace PAGASA or authorized coastal agencies.

## Required FALCON AI wave prediction

Short-term wave-height prediction is a required, always-visible FALCON cloud/edge-service feature. The service estimates the wave height 5, 10, or 15 minutes ahead from recent pressure-based estimated-wave records and reports its condition, model version, sample count, and live/simulated source. The Overview uses a clearly labeled red AI comparison line and a separate numeric future-prediction card; it does not imply that predictions are measured data. The current implementation is a transparent short-term trend baseline, not yet a trained or field-validated model. Calibrated field data, chronological train/validation/test partitions, baseline comparison, MAE/RMSE/bias reporting, and versioned evaluation records are required before claiming AI accuracy.

## Canonical grouped telemetry contract

`GET /api/telemetry/current` and compatibility alias `GET /api/dashboard` return:

```json
{
  "system": {},
  "wave": {},
  "environment": {},
  "gps": {},
  "power": {"battery": {}, "solar": {}},
  "security": {},
  "health": {},
  "assistant": {},
  "alerts": []
}
```

Legacy endpoints `/status`, `/wave`, `/gps`, `/battery`, `/solar`, `/ai`, `/logs`, and selected `/api/...` routes remain temporarily available for backward compatibility. Current values use ISO 8601 timestamps and explicit states such as `LIVE`, `SIMULATED`, `ESTIMATED`, `CALIBRATION REQUIRED`, `OFFLINE`, `STALE`, and `OPTIONAL`.

## Implementation status

Implemented in the repository:

- ESP32 PlatformIO firmware shell, captive setup/diagnostic portal, and telemetry framing prototype;
- Python edge/cloud service prototype with simulator, bench serial ingestion, SQLite logging, deterministic alerts, REST API, prediction baseline, and static dashboard hosting;
- grouped adviser-approved telemetry endpoint;
- pressure-data fields and simulated pressure-based wave estimate;
- GPS geofence and tamper/enclosure simulation states;
- four-page responsive Bay Station dashboard with settings icon;
- optional rule-based assistant assets and required always-visible prediction display;
- local logs, alerts, search, and export.

Not yet physically validated:

- final sensor models and procurement beyond explicitly selected parts;
- pressure-to-wave calibration coefficients and reference accuracy;
- real GPS geofence false-positive performance;
- tamper component selection and debounce thresholds;
- confirmation that excluded environmental channels are absent from the Phase 1 release;
- full waterproofing, corrosion protection, power autonomy, and coastal endurance;
- selected field pressure/wind parts, 4G/LTE modem and antenna, cloud endpoint/data plan, and coastal installation;
- field-trained or field-validated AI.

## Validation plan

1. Bench-test each sensor independently and record raw values, units, range, and failures.
2. Calibrate pressure zero/baseline and compare estimated wave height with a documented physical reference.
3. Compare wind speed and direction with suitable reference instruments across the intended operating range.
4. Survey the GPS deployment reference and test inside/outside geofence persistence.
5. Test vibration and enclosure inputs under ordinary wave-like motion and deliberate tampering; record false positives/negatives.
6. Measure Wi-Fi/LTE registration, event upload latency, data usage, reconnect, cloud synchronization, duplicate prevention, stale-data behavior, storage retention, and restart recovery.
7. Validate battery/solar readings against a calibrated meter and complete an energy budget.
8. Test dashboard readability and responsiveness on desktop, tablet, and phone.
9. Validate and improve the required AI wave-prediction feature using traceable calibrated data, while keeping monitoring independent of prediction availability.

## Scope limits and safe claims

FALCON does not provide tsunami, typhoon, storm, or weather prediction; autonomous navigation; official coastal warnings; laboratory-grade water-quality analysis; camera AI; satellite communication; or multi-buoy networking in Phase 1. Camera viewing, Raspberry Pi 5 migration, more sensors, cloud synchronization, and advanced AI remain future upgrades subject to power, privacy, cost, and validation reviews.

## Immediate priorities

1. Define and review the proposed replacement prototype using `PROTOTYPE_REDESIGN_BASELINE.md`.
2. Select exact pressure and wind parts, then select only the supporting GPS, power, tamper, enclosure-switch, and telemetry interfaces required for operation.
3. Freeze component placement, pinout, wiring, and PCB only after electrical and physical-fit review.
4. Implement physical pressure acquisition and a documented calibration routine.
5. Implement security persistence/debounce on real hardware.
6. Select and integrate Wi-Fi for bench work or a 4G/LTE modem for the field buoy, then verify authentication, event-driven reporting, buffering, cloud synchronization, automatic startup, and recovery.
7. Collect controlled reference data before performance or accuracy claims.

## Change control

Any document that conflicts with this v9.0 event-driven cloud context is outdated unless explicitly labeled historical. New sensor, AI, cloud, cellular, LoRa, or mechanical scope requires adviser approval and corresponding updates to requirements, BOM, firmware, API, tests, dashboard, thesis, and risk documentation.
