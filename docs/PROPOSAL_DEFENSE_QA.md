# Project FALCON Proposal Defense Q&A


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

## How to use this guide

These answers are for proposal defense, adviser consultation, and funding presentations. Keep the answers evidence-based. Use `proposed`, `planned`, `simulated`, `estimated`, `pending`, and `to be validated` when discussing work that is not yet physically completed.

## Project and purpose

### 1. What is Project FALCON?

Project FALCON is a proposed affordable, solar-powered coastal observation buoy for localized monitoring of pressure-derived wave conditions and required wind. The buoy will sample locally, then send event-driven summaries and alerts through Wi-Fi during testing or 4G/LTE during a remote trial. A cloud service will store the data, host the dashboard, and provide authorized access.

### 2. What problem does it address?

The project addresses limited access to affordable, site-specific coastal observations for schools, communities, and other local users. It does not claim that official monitoring is absent or that FALCON will replace professional oceanographic systems. The proposal investigates whether a smaller, documented, and locally adaptable platform can provide useful observations after proper calibration and testing.

### 3. Is the project already deployed?

No. It is an undergraduate Phase 1 proposal and software engineering prototype. The dashboard, simulator, edge-service prototype, firmware foundation, API, and documentation are available. Physical sensor integration, final communications hardware, calibration, waterproofing, endurance, and supervised coastal testing remain pending.

### 4. Who is the first intended user?

The first intended user should be one verified coastal stakeholder and one identified pilot site. The team must confirm the user's information needs through consultation before claiming that the system solves an operational community problem.

## Technical operation

### 5. How does the water-pressure sensor measure waves?

The pressure sensor is placed below the water surface and measures underwater pressure. Static pressure depends mainly on the sensor depth. When the water surface moves, the pressure at the sensor changes over time. The system filters the pressure signal, removes the baseline, and uses calibration data to estimate wave height. The sensor directly measures pressure; wave height is a derived estimate.

### 5A. Which exact pressure sensor will you use for long-term deployment?

The recommended candidate is a Holykell HPT604 Type A ordered provisionally as 0–2 mH2O vented gauge with 4–20 mA output. It will use a protected 12 V loop, 150 ohm precision shunt and ADS1115 receiver. This is still a candidate: we will not purchase or deploy it until the supplier confirms the exact order code, continuous-saltwater compatibility, wetted materials, seal, cable, and calibration. Bar02 is limited to short supervised comparison because its daily drying and immersion limits do not fit unattended deployment.

### 6. What is the basic pressure relationship?

The hydrostatic relationship is:

$$P = \rho g h$$

where pressure depends on water density, gravity, and depth. In actual implementation, the team must account for sensor depth, dynamic response, noise, installation conditions, and calibration. A pressure difference must not be converted to an exact wave height without reference testing.

### 7. Why use pressure instead of an IMU?

The Phase 1 scope is intentionally focused. A submerged pressure time series provides a direct input for investigating pressure-derived wave estimation. The BNO085 IMU is not required in the current baseline, and buoy motion visualization must not be presented as an IMU measurement.

### 8. What does the wind sensor contribute?

Wind speed and direction provide environmental context alongside the pressure-derived wave estimate. They are optional/supporting channels in the reduced build and still require comparison with suitable reference instruments before accuracy claims.

### 9. What sensors are excluded?

Water temperature, salinity, conductivity, BNO085 IMU measurement, and load-cell/HX711 mooring tension are excluded from the required Phase 1 measurement scope. GPS, battery, solar, timestamps, enclosure temperature, and security inputs are supporting system telemetry.

## Architecture and communications

### 10. Why is processing outside the buoy?

The cloud or development edge service keeps storage, dashboard hosting, and heavier analysis away from the buoy. This reduces buoy power, heat, waterproofing, and maintenance demands. The exact cloud provider or shore computer remains subject to approval and testing.

### 11. What is the proposed communication path?

The proposed path is:

```text
Sensors -> ESP32 -> Wi-Fi/LTE -> Cloud API/database/dashboard
```

Wi-Fi is the planned laboratory link and 4G/LTE is the planned remote field link. The ESP32 needs an external LTE modem because ordinary ESP32 boards do not have built-in cellular connectivity.

### 12. Is the cloud link already implemented?

Not yet. The current firmware and edge service support diagnostic and bench telemetry, including USB serial framing. The exact LTE module, cloud endpoint, protocol, authentication, buffering, and site coverage remain selection and implementation gates.

### 13. Why not put the SIM/4G/5G modem on the buoy?

The revised proposal places the LTE modem on the buoy for a direct cloud path. This removes the LoRa gateway requirement, but it adds modem power peaks, antenna constraints, SIM management, and coverage testing.

### 14. What happens during an outage?

During an Internet outage, the ESP32 should continue acquisition and local security while buffering records for later retransmission. Cloud upload and authorized dashboard access should resume after connectivity returns. These behaviors are proposed acceptance requirements, not yet field evidence.

## Software and AI

### 15. What has already been developed?

The repository contains an ESP32 firmware shell and diagnostic portal, versioned telemetry framing, a Python edge/cloud prototype, simulator, SQLite storage, REST API, deterministic alerts, pressure-based simulated wave processing, prediction baseline, and a four-page dashboard. These demonstrate software workflow, not physical accuracy or deployment readiness.

### 16. Is the AI already accurate?

No. The current prediction is a transparent short-term trend baseline used to demonstrate the software workflow. A valid AI result requires calibrated local data, chronological train/validation/test separation, comparison with non-AI baselines, error metrics such as MAE and RMSE, uncertainty reporting, and versioned evaluation records.

### 17. Why make AI a required feature if it is not validated yet?

The proposal treats short-term wave prediction as a research objective to be developed and evaluated, not as an already-proven operational service. The monitoring path must continue working even when prediction is collecting data, unavailable, or inaccurate.

### 18. Is the dashboard showing live ocean measurements?

No. Current presentation values may be simulator-generated. Every value must be labeled as `LIVE`, `SIMULATED`, `ESTIMATED`, `CALIBRATION REQUIRED`, `STALE`, `OFFLINE`, or `MODEL OUTPUT` as appropriate.

## Validation and safety

### 19. How will pressure-to-wave accuracy be tested?

The team will record raw pressure, measure sensor installation depth, establish a baseline, use controlled water-column or wave-motion tests, and compare the estimate against a documented independent reference. The calibration and verification data must be separate. Final claims will report error, repeatability, limitations, and quality states.

### 20. How will false security alerts be controlled?

The system will use geofence persistence, GPS quality, vibration/tamper persistence, enclosure-switch state, and authorized maintenance mode. Normal wave-driven movement must not automatically be treated as theft. False positives and false negatives must be tested under representative motion.

### 21. What safety claims are not allowed?

FALCON is not an official weather, tsunami, typhoon, storm, navigation, or emergency-warning service. It does not replace PAGASA, coast guard instructions, professional oceanographic instruments, or authorized emergency agencies.

### 22. What must funding enable?

Funding should enable exact component procurement, compact can-buoy fabrication, LTE/cloud integration, pressure and required wind calibration, power and waterproofing tests, controlled data collection, optional prediction evaluation, and supervised coastal validation.

## Difficult questions

### 23. What is innovative about the project?

The proposal does not claim to invent the pressure sensor, buoy, cloud service, or AI algorithm. Its intended contribution is the transparent integration and local evaluation of pressure-based wave estimation, event-driven telemetry, solar power, security telemetry, and a clearly labeled dashboard for a defined local use case.

### 24. What are the main risks?

The main risks are pressure-to-wave calibration uncertainty, wind-sensor durability, LTE coverage and data cost, cloud availability, power autonomy, water ingress, false security alerts, incomplete local data, and insufficient data for prediction evaluation. Each risk requires a test, acceptance condition, or explicit limitation.

### 25. What is the most honest conclusion today?

The team has a coherent architecture and software demonstration, but not yet a physically validated coastal instrument. The proposal requests support to turn the documented concept into a calibrated, tested, and evidence-based prototype.

## Safe phrases

Use:

- proposed architecture
- planned Wi-Fi/LTE cloud link
- proposed event-driven upload and buffering
- simulator-generated data
- pressure-derived estimated wave height
- calibration required
- pending procurement or integration
- to be validated under controlled tests
- supervised pilot deployment

Avoid:

- deployed system
- production-ready buoy
- accurate AI forecast
- guaranteed LTE coverage or cloud availability
- live ocean data, when using the simulator
- certified warning system
- final mechanical design
- field-proven autonomy
