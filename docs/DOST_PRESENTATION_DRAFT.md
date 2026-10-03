# Project FALCON-01 — DOST Presentation Draft

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
4. Transmit via LoRa to shore Bay Station for storage, processing and dashboard
5. Evaluate accuracy, reliability, latency, power use and usability
6. Develop and evaluate short-term AI wave prediction vs baseline

## Slide 4 — System Architecture
Buoy ESP32 → LoRa → Bay Station mini PC
Bay Station: SQLite, REST API, Dashboard, AI prediction
Internet backhaul via SIM/4G/5G from Bay Station only
No mini PC or cellular on buoy
Buffering and retransmission on LoRa outage

## Slide 5 — Hardware Baseline
Buoy:
* ESP32 controller
* Underwater pressure sensor
* Wind speed / direction sensors
* GPS for position/time/geofence
* Battery / solar power
* LoRa transceiver
Shore:
* Bay Station mini PC
* LoRa receiver
* Local storage and processing

## Slide 6 — Software Baseline
* ESP32 PlatformIO firmware with telemetry framing
* Python Bay Station service: simulator, SQLite, REST API, prediction baseline
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
LoRa packet loss, latency, range, buffering
Power budget validation
Dashboard usability on desktop/tablet/phone
AI evaluation vs baseline

## Slide 11 — Current Status
Implemented:
* ESP32 firmware shell, captive portal, telemetry framing
* Bay Station service prototype with simulator, SQLite, API, dashboard
* Grouped telemetry endpoint
* Pressure-based wave estimate simulation
* GPS geofence simulation
Not yet validated:
* Final sensor models and calibration coefficients
* Real GPS/tamper performance
* LoRa hardware selection and range
* Field-trained AI

## Slide 12 — Scope Limits and Safe Claims
No tsunami/typhoon prediction, no official warnings, no navigation control
No laboratory-grade water quality analysis
Phase 1 is integration and evaluation, not sensor invention
All claims are prototype status until validation is complete

## Slide 13 — Risks and Mitigations
Power autonomy, waterproofing, corrosion
LoRa range and interference
Calibration drift
False security alerts
Mitigations via bench testing, staged deployment, documented validation

## Slide 14 — Timeline and Next Steps
Define replacement prototype per PROTOTYPE_REDESIGN_BASELINE.md
Select exact parts and freeze BOM
Implement physical pressure acquisition and calibration routine
Integrate LoRa buoy radio and Bay Station gateway
Collect controlled reference data before performance claims

## Slide 15 — Acknowledgement
Adviser revision 2026-08-29
Project FALCON-01 Master Context v8.1
Thank you
