# Project FALCON Master Context v7.0 — Bay Station Baseline

## Document control

| Field | Current approved value |
| --- | --- |
| Project | Project FALCON-01 |
| Project type | Solar-powered smart coastal observation buoy |
| Status | Undergraduate Phase 1 prototype; hardware integration pending |
| Authority | Master repository source of truth |
| Bay Station | Shore-based mini PC; exact model TBD, development laptop substitute |
| Controller | ESP32 |
| Primary wave method | Pressure-based estimated wave height |
| AI | Required Bay Station short-term wave-height prediction; validation pending |
| Telemetry | LTE/cellular; exact modem, protocol, antenna, and provider TBD |
| Adviser revision | 2026-08-29 |
| Physical prototype | UNDER REDESIGN; geometry and placement TBD |

This file supersedes older Orange Pi-on-buoy, USB-only deployment, BNO085, and anchor-chain load-cell descriptions. The Bay Station AI predictor is required, but its trained model and accuracy remain unvalidated. Working code remains the authority for implemented behavior. Planned hardware must not be described as installed or field-validated.

The system-function baseline remains approved, but the physical and visual prototype is being replaced. `PROTOTYPE_REDESIGN_BASELINE.md` governs that work. Existing CAD, renderings, dashboard models, dimensions, enclosure layouts, solar arrangements, and component positions are reference material only until the replacement passes its acceptance checklist.

## Project definition

Project FALCON is a low-cost, modular, solar-powered coastal observation buoy intended to collect near-real-time coastal, position, power, security, and system-health data. An ESP32 buoy node acquires and validates sensor readings, maintains local security logic, buffers short communication outages, and sends versioned telemetry through an approved LTE/cellular link. A shore-based Bay Station mini PC stores records, performs pressure-based wave processing and AI prediction, serves the REST API/dashboard, and manages alerts. No mini PC is installed on the buoy.

The core undergraduate contribution is the integration and evaluation of an accessible local coastal-monitoring prototype. The system estimates wave height from calibrated underwater-pressure variations. It does not claim direct laboratory-grade wave measurement, official forecasting, navigation control, or disaster-warning capability.

## Objectives

1. Design a serviceable solar-powered coastal buoy with passive single-anchor mooring.
2. Acquire timestamped pressure, GPS, wind, environmental, power, security, and health readings.
3. Filter and calibrate underwater pressure to produce an explicitly labeled estimated wave height.
4. Detect persistent GPS geofence, vibration/tamper, and enclosure-access events without treating normal wave motion as theft.
5. Transmit telemetry to a shore Bay Station for SQLite storage, processing, alerts, and a simple four-page dashboard.
6. Evaluate accuracy, reliability, latency, power use, usability, and false-alert behavior through documented tests.
7. Develop and evaluate required short-term AI wave prediction against a documented non-AI baseline using chronological held-out data.

## Research gap and novelty

Many low-cost educational systems demonstrate individual marine sensors or generic IoT dashboards. Commercial observation buoys may be inaccessible to small schools because of acquisition cost, proprietary interfaces, and maintenance requirements. FALCON investigates an affordable local-first combination of pressure-based wave estimation, environmental sensing, solar power, local logging, geofence/tamper monitoring, and a transparent dashboard for controlled Philippine coastal trials. Novelty must be claimed as integration and evaluation, not invention of the sensors or official ocean forecasting.

## Approved Phase 1 architecture

```text
Pressure / GPS / wind / environment / power / security sensors
                              |
                            ESP32
                              |
                    LTE/cellular telemetry
                              |
                  shore-based Bay Station mini PC
                 +------------+-------------+
                 |            |             |
              SQLite       REST API    Web dashboard + AI
                                              |
                                   laptop / tablet / phone
```

The deployed path requires available cellular coverage between the buoy and Bay Station. The ESP32 continues acquisition and local security during outages and buffers a defined amount of telemetry for later retransmission. The Bay Station performs ingestion, pressure processing, logging, API/dashboard hosting, alerts, and required AI inference. USB serial remains a bench-development transport only.

## Sensor baseline

### Core sensors

- Blue Robotics Bar02 or compatible waterproof pressure sensor: raw pressure and pressure-based wave estimation.
- GPS receiver: coordinates, fix quality, time, and geofence displacement.
- Wind-speed sensor: local wind-speed context.
- Wind-direction sensor: local wind-direction context.

### Supporting environmental sensor

- Sealed DS18B20: water temperature with timestamp, validity, freshness, and reference-comparison status.
- Conductivity/salinity sensing is excluded from the required Phase 1 scope. Legacy API fields may remain temporarily for backward compatibility but are not displayed or evaluated.

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
- On-buoy AI or mini PC: excluded. Required short-term AI prediction runs only at the shore Bay Station.

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

1. **Overview** — one large estimated-wave chart, one Station Status card containing wind, pressure, GPS security, battery, solar, and water/enclosure temperature, and one always-visible FALCON AI short-term wave-prediction card.
2. **Buoy Motion** — optional 3D visual model whose water-surface amplitude, heave, and tilt are generated from pressure-based estimated wave height; GPS may provide heading context. It has no required IMU, roll, or pitch measurement channel. It includes Current Data plus clearly labeled Calm, Moderate, Rough, and Pressure Offline presentation scenarios. The scenarios are local visual presets and do not modify stored or live telemetry.
3. **Sensors** — six readable operator groups: Wave & Pressure, GPS & Security, Wind, Water, Power, and System. Exact device models, sampling, quality, freshness, and calibration diagnostics remain available through expandable details.
4. **Logs & Alerts** — active alerts, persisted telemetry, security events, calibration events, operator actions, search, and export. It remains the final sidebar item.

Settings are available through a compact icon and are not a primary navigation item. The former separate Wave, GPS, Power, System, History, and Alerts pages remain consolidated. Motion is retained strictly as an optional visual model and does not restore BNO085 as a required sensor.

## FALCON Assistant

The assistant is a saved optional animated, rule-based visual status aid and is currently hidden from the dashboard while its final design is being reviewed. It is not a chatbot, language model, voice assistant, or autonomous controller. States are `IDLE/NORMAL`, `WARNING`, `ALERT`, and `OFFLINE`. Messages must be short, factual, and derived from deterministic station rules. It must never issue an official safety advisory or replace PAGASA or authorized coastal agencies.

## Required FALCON AI wave prediction

Short-term wave-height prediction is a required, always-visible FALCON Bay Station feature. The service estimates the wave height 5, 10, or 15 minutes ahead from recent pressure-based estimated-wave records and reports its condition, model version, sample count, and live/simulated source. The Overview uses a clearly labeled red AI comparison line and a separate numeric future-prediction card; it does not imply that predictions are measured data. The current implementation is a transparent short-term trend baseline, not yet a trained or field-validated model. Calibrated field data, chronological train/validation/test partitions, baseline comparison, MAE/RMSE/bias reporting, and versioned evaluation records are required before claiming AI accuracy.

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
- Python Bay Station service prototype with simulator, bench serial ingestion, SQLite logging, deterministic alerts, REST API, prediction baseline, and static dashboard hosting;
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
- water-temperature reference comparison;
- full waterproofing, corrosion protection, power autonomy, and coastal endurance;
- selected LTE/cellular modem integration and shore Bay Station installation;
- field-trained or field-validated AI.

## Validation plan

1. Bench-test each sensor independently and record raw values, units, range, and failures.
2. Calibrate pressure zero/baseline and compare estimated wave height with a documented physical reference.
3. Compare the sealed DS18B20 with a traceable reference thermometer across the intended operating range.
4. Survey the GPS deployment reference and test inside/outside geofence persistence.
5. Test vibration and enclosure inputs under ordinary wave-like motion and deliberate tampering; record false positives/negatives.
6. Measure cellular packet loss, latency, coverage, reconnect/buffered retransmission, duplicate prevention, stale-data behavior, storage retention, and restart recovery.
7. Validate battery/solar readings against a calibrated meter and complete an energy budget.
8. Test dashboard readability and responsiveness on desktop, tablet, and phone.
9. Validate and improve the required AI wave-prediction feature using traceable calibrated data, while keeping monitoring independent of prediction availability.

## Scope limits and safe claims

FALCON does not provide tsunami, typhoon, storm, or weather prediction; autonomous navigation; official coastal warnings; laboratory-grade water-quality analysis; camera AI; satellite communication; or multi-buoy networking in Phase 1. Camera viewing, Raspberry Pi 5 migration, more sensors, cloud synchronization, and advanced AI remain future upgrades subject to power, privacy, cost, and validation reviews.

## Immediate priorities

1. Define and review the proposed replacement prototype using `PROTOTYPE_REDESIGN_BASELINE.md`.
2. Select exact pressure, GPS, wind, water-temperature, tamper, enclosure-switch, and power-interface parts.
3. Freeze component placement, pinout, wiring, and PCB only after electrical and physical-fit review.
4. Implement physical pressure acquisition and a documented calibration routine.
5. Implement security persistence/debounce on real hardware.
6. Select and integrate the LTE modem and shore Bay Station, then verify authentication, buffering, automatic startup, and recovery.
7. Collect controlled reference data before performance or accuracy claims.

## Change control

Any document that conflicts with this v7.0 Bay Station context is outdated unless explicitly labeled historical. New sensor, AI, cloud, cellular, or mechanical scope requires adviser approval and corresponding updates to requirements, BOM, firmware, API, tests, dashboard, thesis, and risk documentation.
