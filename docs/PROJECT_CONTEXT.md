# Project FALCON Master Context v6.0

## Document control

| Field | Current approved value |
| --- | --- |
| Project | Project FALCON-01 |
| Project type | Solar-powered smart coastal observation buoy |
| Status | Undergraduate Phase 1 prototype; hardware integration pending |
| Authority | Master repository source of truth |
| Edge host | Orange Pi Zero 3 (4 GB), with laptop substitute during development |
| Controller | ESP32 |
| Primary wave method | Pressure-based estimated wave height |
| AI | Optional supporting research feature |
| Adviser revision | 2026-08-25 |

This file supersedes older descriptions that made the BNO085 IMU, anchor-chain tension sensing, or AI forecasting mandatory. Working code remains the authority for what is implemented. Planned hardware must not be described as installed or field-validated.

## Project definition

Project FALCON is a low-cost, modular, solar-powered coastal observation buoy intended to collect near-real-time coastal, position, power, security, and system-health data. An ESP32 acquires sensor readings and sends them to an Orange Pi Zero 3 through USB/UART. The Orange Pi logs data locally, serves a REST API, and hosts a responsive web dashboard without requiring Internet connectivity.

The core undergraduate contribution is the integration and evaluation of an accessible local coastal-monitoring prototype. The system estimates wave height from calibrated underwater-pressure variations. It does not claim direct laboratory-grade wave measurement, official forecasting, navigation control, or disaster-warning capability.

## Objectives

1. Design a serviceable solar-powered coastal buoy with passive single-anchor mooring.
2. Acquire timestamped pressure, GPS, wind, environmental, power, security, and health readings.
3. Filter and calibrate underwater pressure to produce an explicitly labeled estimated wave height.
4. Detect persistent GPS geofence, vibration/tamper, and enclosure-access events without treating normal wave motion as theft.
5. Store telemetry and events locally on the Orange Pi and present them through a simple four-page dashboard.
6. Evaluate accuracy, reliability, latency, power use, usability, and false-alert behavior through documented tests.
7. Explore short-term AI wave prediction only as an optional extension after the monitoring baseline is validated.

## Research gap and novelty

Many low-cost educational systems demonstrate individual marine sensors or generic IoT dashboards. Commercial observation buoys may be inaccessible to small schools because of acquisition cost, proprietary interfaces, and maintenance requirements. FALCON investigates an affordable local-first combination of pressure-based wave estimation, environmental sensing, solar power, local logging, geofence/tamper monitoring, and a transparent dashboard for controlled Philippine coastal trials. Novelty must be claimed as integration and evaluation, not invention of the sensors or official ocean forecasting.

## Approved Phase 1 architecture

```text
Pressure / GPS / wind / environment / power / security sensors
                              |
                            ESP32
                              |
                         USB serial/UART
                              |
                    Orange Pi Zero 3 (4 GB)
                 +------------+-------------+
                 |            |             |
              SQLite       REST API    Local dashboard
                                              |
                                   laptop / tablet / phone
```

Internet and cloud synchronization are not required. The ESP32 continues basic acquisition when the edge computer is temporarily unavailable. The Orange Pi performs logging, aggregation, API hosting, dashboard hosting, and optional future model inference.

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
- Mandatory AI prediction: removed. AI is optional and supporting.

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

1. **Overview** — one large estimated-wave chart and one Station Status card containing wind, pressure, GPS security, battery, solar, and water/enclosure temperature. Optional AI is not shown in the default operator view.
2. **Buoy Motion** — optional 3D visual model driven by estimated sea context; it is not a required BNO085 measurement channel.
3. **Sensors** — six readable operator groups: Wave & Pressure, GPS & Security, Wind, Water, Power, and System. Exact device models, sampling, quality, freshness, and calibration diagnostics remain available through expandable details.
4. **Logs & Alerts** — active alerts, persisted telemetry, security events, calibration events, operator actions, search, and export.

Settings are available through a compact icon and are not a primary navigation item. The former separate Wave, GPS, Power, System, History, and Alerts pages remain consolidated. Motion is retained strictly as an optional visual model and does not restore BNO085 as a required sensor.

## FALCON Assistant

The assistant is a saved optional animated, rule-based visual status aid and is currently hidden from the dashboard while its final design is being reviewed. It is not a chatbot, language model, voice assistant, or autonomous controller. States are `IDLE/NORMAL`, `WARNING`, `ALERT`, and `OFFLINE`. Messages must be short, factual, and derived from deterministic station rules. It must never issue an official safety advisory or replace PAGASA or authorized coastal agencies.

## Optional AI

Short-term wave prediction may remain as an opt-in research demonstration after the pressure-monitoring baseline is functional. It must be hidden by default, labeled `OPTIONAL`, identify simulated versus live inputs, expose model/version/sample context, and never be described as an official forecast. Failure of the optional model must not interrupt data acquisition, logging, security, or the dashboard.

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
- Python edge service with simulator, serial ingestion, SQLite logging, deterministic alerts, REST API, and static dashboard hosting;
- grouped adviser-approved telemetry endpoint;
- pressure-data fields and simulated pressure-based wave estimate;
- GPS geofence and tamper/enclosure simulation states;
- four-page responsive dashboard with settings icon;
- optional rule-based assistant and opt-in prediction display;
- local logs, alerts, search, and export.

Not yet physically validated:

- final sensor models and procurement beyond explicitly selected parts;
- pressure-to-wave calibration coefficients and reference accuracy;
- real GPS geofence false-positive performance;
- tamper component selection and debounce thresholds;
- water-temperature reference comparison;
- full waterproofing, corrosion protection, power autonomy, and coastal endurance;
- Orange Pi installation on the buoy;
- field-trained or field-validated AI.

## Validation plan

1. Bench-test each sensor independently and record raw values, units, range, and failures.
2. Calibrate pressure zero/baseline and compare estimated wave height with a documented physical reference.
3. Compare the sealed DS18B20 with a traceable reference thermometer across the intended operating range.
4. Survey the GPS deployment reference and test inside/outside geofence persistence.
5. Test vibration and enclosure inputs under ordinary wave-like motion and deliberate tampering; record false positives/negatives.
6. Measure serial packet loss, latency, stale-data behavior, storage retention, and restart recovery.
7. Validate battery/solar readings against a calibrated meter and complete an energy budget.
8. Test dashboard readability and responsiveness on desktop, tablet, and phone.
9. Evaluate optional AI separately and only with traceable live/calibrated data.

## Scope limits and safe claims

FALCON does not provide tsunami, typhoon, storm, or weather prediction; autonomous navigation; official coastal warnings; laboratory-grade water-quality analysis; camera AI; satellite communication; or multi-buoy networking in Phase 1. Camera viewing, Raspberry Pi 5 migration, more sensors, cloud synchronization, and advanced AI remain future upgrades subject to power, privacy, cost, and validation reviews.

## Immediate priorities

1. Select exact pressure, GPS, wind, water-temperature, tamper, enclosure-switch, and power-interface parts.
2. Freeze the adviser-approved pinout and wiring after electrical review.
3. Implement physical pressure acquisition and a documented calibration routine.
4. Implement security persistence/debounce on real hardware.
5. Integrate the Orange Pi service and verify automatic startup.
6. Collect controlled reference data before performance or accuracy claims.

## Change control

Any document that conflicts with this v6.0 context is outdated unless it is explicitly labeled historical. New sensor, AI, cloud, or mechanical scope requires adviser approval and corresponding updates to requirements, BOM, firmware, API, tests, dashboard, thesis, and risk documentation.
