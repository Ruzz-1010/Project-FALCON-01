# Project FALCON-01 — DOST Presentation Draft


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

## Slide 1 — Title
Project FALCON-01
Solar-Powered Coastal Observation Buoy Prototype
Phase 1 — Undergraduate Prototype
Date: 5 October 2026
Fullbright College

## Slide 2 — Problem Statement
* Limited access to affordable coastal wave and wind data in barangay-level settings
* Commercial buoys are costly, proprietary and maintenance heavy
* Need for local-first, transparent, evaluable prototype for education and research

## Slide 3 — Objectives
1. Design serviceable solar-powered buoy with passive mooring
2. Acquire pressure and wind measurements with supporting telemetry
3. Estimate wave height from underwater pressure with explicit calibration
4. Upload event-driven summaries and alerts directly to the cloud through Wi-Fi or 4G/LTE
5. Evaluate accuracy, reliability, latency, power use and usability
6. Develop and evaluate short-term AI wave prediction vs baseline

## Slide 4 — System Architecture
Buoy ESP32 → Wi-Fi/LTE modem → Cloud API/database/dashboard
ESP32: local sampling, event detection, buffering, and upload
No mini PC or LoRa gateway in the low-cost minimum build
Buffering and retransmission on Internet outage

## Slide 5 — Hardware Baseline
Buoy:
* ESP32 controller
* Underwater pressure sensor
* Wind speed / direction sensors
* GPS for position/time/geofence
* Battery / solar power
* 4G/LTE modem for remote field tests or Wi-Fi for laboratory tests
* Local flash or microSD buffer
Cloud:
* API and database
* Dashboard, alerts, and optional heavier processing

## Slide 6 — Software Baseline
* ESP32 PlatformIO firmware with telemetry framing
* Python edge/cloud service: simulator, SQLite, REST API, prediction baseline
* Four-page dashboard: Overview, Buoy Motion, Sensors, Logs & Alerts
* Grouped telemetry endpoint with explicit states LIVE/SIMULATED/ESTIMATED

## Slide 7 — Wave Estimation Method
Pressure measurement → quality check → filter → baseline removal → depth response → calibration → estimated Hs
Wave height is an estimate derived from pressure and calibration
Calibration and reference comparison required before accuracy claims

## Slide 8 — AI Prediction Requirement
Short-term wave-height prediction 5/10/15 min ahead
Currently transparent trend baseline
Evaluation requires calibrated data, chronological train/validation/test, MAE/RMSE/bias reporting
Not a trained model result yet

## Slide 9 — Security and Health
Security states: SECURE, WARNING, ALERT, DISARMED
GPS geofence persistence, vibration/tamper, enclosure switch
Normal wave motion must not generate alerts
False-positive testing required

## Slide 10 — Validation Plan
Bench sensor tests, pressure-to-wave calibration vs reference
Wind sensor comparison
GPS geofence testing
Vibration/tamper testing
Wi-Fi/LTE upload latency, packet loss, coverage, buffering, and retry testing
Power budget validation
Dashboard usability on desktop/tablet/phone
AI evaluation vs baseline

## Slide 11 — Current Status
Implemented:
* ESP32 firmware shell, captive portal, telemetry framing
* Edge/cloud service prototype with simulator, SQLite, API, dashboard
* Grouped telemetry endpoint
* Pressure-based wave estimate simulation
* GPS geofence simulation
Not yet validated:
* Final sensor models and calibration coefficients
* Real GPS/tamper performance
* LTE modem selection, coverage, data cost, and upload reliability
* Field-trained AI

## Slide 12 — Scope Limits and Safe Claims
No tsunami/typhoon prediction, no official warnings, no navigation control
No laboratory-grade water quality analysis
Phase 1 is integration and evaluation, not sensor invention
All claims are prototype status until validation is complete

## Slide 13 — Risks and Mitigations
Power autonomy, waterproofing, corrosion
LTE/Wi-Fi coverage, antenna placement, data cost, and upload retries
Calibration drift
False security alerts
Mitigations via bench testing, staged deployment, documented validation

## Slide 14 — Timeline and Next Steps
Define replacement prototype per PROTOTYPE_REDESIGN_BASELINE.md
Select exact parts and freeze BOM
Implement physical pressure acquisition and calibration routine
Integrate Wi-Fi/LTE cloud upload, buffering, and authentication
Collect controlled reference data before performance claims

## Slide 15 — Acknowledgement
DOST revision direction 2026-10-09
Project FALCON-01 Master Context v9.0
Thank you
