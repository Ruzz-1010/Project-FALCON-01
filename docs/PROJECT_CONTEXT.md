# PROJECT_CONTEXT.md v5.0

## Document Control

| Field | Value |
| --- | --- |
| Project | Project FALCON |
| Expanded name | Fullbright College's AI-powered Live Coastal Observation Network |
| Document | Master Engineering Context |
| Version | 5.0 |
| Status | Phase 1 Prototype |
| Authority | Official repository source of truth |
| Research focus | Real-time coastal monitoring and AI-assisted short-term wave-height prediction |
| Prediction window | 5–15 minutes |
| Primary deployment context | Philippine coastal waters |
| Primary controller | ESP32 |
| Selected edge computer | Orange Pi Zero 3 (4GB) |
| Last architecture update | 2026-08-13 |
## Authority and Use

This document defines the approved Phase 1 engineering baseline for Project FALCON. It governs:
- research scope;
- system architecture;
- firmware boundaries;
- sensor selection;
- AI responsibilities;
- dashboard content;
- API design;
- mechanical constraints;
- power architecture;
- validation activities;
- repository organization;
- documentation terminology;
- and future-development decisions.
Every future firmware change shall be checked against this document. Every future dashboard change shall be checked against this document. Every future CAD change shall be checked against this document. Every
future AI model shall be checked against this document. Every future API change shall be checked against this document. Every future research claim shall be checked against this document. When a lower-level
document conflicts with this document, this document has priority unless an approved newer master context explicitly supersedes it. Working source code remains the authority for what is currently implemented.
This document remains the authority for what the approved system is intended to become. The difference between implementation and intent shall always be stated honestly.
## Version 4 Refactor Intent

Version 4 narrows Project FALCON to one defensible research contribution. The project is not a general-purpose marine AI platform. The project is not a weather-forecasting platform. The project is not an
autonomous marine vehicle. The project is not a cloud-first buoy network. The project is a focused coastal observation prototype. Its two core functions are:
1. real-time coastal monitoring; and
2. AI-assisted short-term wave-height prediction.
Useful v3 engineering material is retained where it supports these functions. Duplicated material is consolidated. Unapproved capabilities are moved to Future Expansion. Conflicting claims are removed.
Unimplemented features are not presented as completed work.
## Project Identity

Project FALCON is Fullbright College's AI-powered Live Coastal Observation Network. FALCON is an affordable, modular, solar-powered coastal monitoring buoy prototype. It is intended to collect near-real-time
coastal measurements. It is intended to estimate short-term wave height at the edge. It is intended to classify current or predicted sea conditions. It is intended to operate through a local dashboard without
requiring cloud connectivity. It is intended for research, education, prototyping, and controlled coastal trials. It is designed around commercially available components. It prioritizes field serviceability
over unnecessary complexity. It prioritizes transparent predictions over unsupported AI claims. It prioritizes a focused research scope over a long feature list.
## Executive Summary

Affordable coastal monitoring systems commonly collect and display environmental readings. Many low-cost systems stop at data acquisition and visualization. Commercial wave-monitoring platforms can be too
costly or inaccessible for small institutions. Project FALCON explores whether a low-cost, modular, solar-powered buoy can provide useful real-time coastal monitoring and AI-assisted wave-height predictions
over a short 5–15 minute window. The Phase 1 buoy uses an ESP32 for deterministic sensor acquisition and control. An Orange Pi Zero 3 (4GB) is the selected edge-computing platform. The ESP32 and Orange Pi communicate primarily through UART, with validated local Wi-Fi available as an alternate transport. The Orange Pi exposes a local REST API and hosts the dashboard. The system remains locally usable without Internet access. Cloud synchronization is not part of the Phase 1 implementation
baseline. The approved AI scope is intentionally limited. The AI estimates short-term wave height. The AI classifies sea condition as Calm, Moderate, or Rough. The AI does not autonomously control the buoy. The
AI does not issue navigation commands. The AI does not predict typhoons, storms, weather, fish activity, maintenance, or water quality.
## Research Focus

### Primary Focus
Project FALCON focuses only on:
- real-time coastal monitoring; and
- AI-assisted short-term wave-height prediction.
### Monitoring Focus
Real-time monitoring includes:
- wave-related pressure changes;
- wave motion from the IMU;
- pitch;
- roll;
- yaw;
- wind speed;
- wind direction;
- GPS position;
- battery state;
- solar charging state;
- internal enclosure temperature;
- system health;
- communication state;
- and operational alerts.
### AI Focus
The AI has exactly two Phase 1 responsibilities.
#### Responsibility 1: Wave-Height Prediction
The AI estimates wave height 5–15 minutes into the future. The output shall include:
- current measured wave height;
- predicted wave height;
- prediction horizon;
- prediction timestamp;
- confidence value;
- model identifier;
- sample count or input-window context;
- and model status.
#### Responsibility 2: Sea-Condition Classification
The AI classifies the sea condition as:
- Calm;
- Moderate; or
- Rough.
No fourth operational class is approved for Phase 1. Invalid or unavailable inputs shall produce an unavailable status rather than a fabricated class.
## Research Gap

Existing affordable marine monitoring systems primarily monitor and display environmental data. Many educational and low-cost IoT buoy projects provide sensor readings but do not provide transparent short-term
wave prediction. Advanced commercial monitoring systems may provide wave analytics, but their acquisition cost, proprietary interfaces, service requirements, and deployment complexity can limit adoption by
smaller Philippine schools, local research groups, and local coastal stakeholders. Few accessible prototypes combine all of the following in one focused platform:
- low-cost components;
- modular construction;
- solar-powered operation;
- local-first monitoring;
- real-time wave-related measurements;
- edge-based short-term wave-height prediction;
- transparent current-versus-predicted values;
- and suitability for controlled Philippine coastal deployment.
Project FALCON addresses this gap by designing and evaluating a focused coastal monitoring buoy that combines deterministic sensing with AI-assisted 5–15 minute wave-height prediction. The research contribution
is not the invention of wave forecasting. The contribution is the integration and evaluation of a low-cost, modular, locally operated prototype for this specific use case.
## Research Questions

The Phase 1 study shall be guided by focused questions.
1. Can a low-cost buoy collect stable real-time wave, motion, wind, position, and power data in controlled coastal conditions?
2. Can pressure and IMU measurements be processed into a repeatable wave-height estimate?
3. Can an edge model provide a measurable 5–15 minute wave-height prediction from the available sensor history?
4. How accurate are predicted wave heights compared with subsequent measured wave heights?
5. Can the system classify sea conditions as Calm, Moderate, or Rough with documented thresholds or validated model logic?
6. Can the local dashboard clearly communicate current measurements, predictions, confidence, alerts, and system state without cloud dependence?
## General Objective

To design, develop, and evaluate a low-cost, modular, solar-powered coastal monitoring buoy that provides real-time coastal measurements and AI-assisted short-term wave-height prediction through a local
dashboard.
## Specific Objectives

1. Design and integrate a stable Phase 1 buoy using a traditional Ø650 mm HDPE single body, a 240 mm rounded tapered underwater keel, central ballast, and a single-anchor mooring system.
2. Acquire and process real-time data from the approved Phase 1 sensor set, including IMU, water pressure, wind, GPS, battery, solar, and internal-temperature measurements.
3. Develop a transparent wave-height estimation pipeline using synchronized water-pressure and IMU data.
4. Develop and evaluate an edge AI method that predicts wave height 5–15 minutes ahead and classifies sea condition as Calm, Moderate, or Rough.
5. Develop a responsive local dashboard that displays current readings, predicted wave height, confidence, alerts, motion, history, logs, and system status.
6. Validate the prototype through mechanical, electrical, sensor, AI, dashboard, and communication testing under controlled conditions.
## Scope

Phase 1 includes only the following scope.
### Real-Time Monitoring
- acquisition of approved sensor readings;
- timestamping;
- range validation;
- basic filtering;
- local display;
- local logging;
- system-health reporting;
- and threshold-based alerts.
### Wave Monitoring
- water-pressure changes;
- IMU motion;
- pitch and roll;
- wave-motion features;
- current wave-height estimation;
- wave history;
- and sea-condition context.
### AI Prediction
- one focused short-term wave-height prediction pipeline;
- 5-minute prediction support;
- 15-minute prediction support;
- confidence reporting;
- current-versus-predicted comparison;
- prediction history;
- validation against subsequent measurements;
- and Calm, Moderate, or Rough classification.
### Dashboard
- local responsive web dashboard;
- desktop and mobile layouts;
- light and dark themes;
- real-time status;
- wave and prediction cards;
- motion display;
- GPS display;
- power display;
- alerts;
- settings;
- histories;
- and logs.
### Solar Operation
- solar energy harvesting;
- MPPT charging;
- 12 V LiFePO4 energy storage;
- power distribution;
- battery monitoring;
- solar monitoring;
- and energy-budget validation.
## Delimitations

Phase 1 does not include tsunami prediction. Phase 1 does not include typhoon prediction. Phase 1 does not include storm prediction. Phase 1 does not include weather forecasting. Phase 1 does not include
ocean-current prediction. Phase 1 does not include fish prediction. Phase 1 does not include maintenance prediction. Phase 1 does not include self-learning AI. Phase 1 does not include multiple operational AI
models. Phase 1 does not include cloud AI. Phase 1 does not include autonomous decision making. Phase 1 does not include autonomous navigation. Phase 1 does not include satellite communication. Phase 1 does not
include multi-buoy networking. Phase 1 does not include camera AI. Phase 1 does not include computer vision. Phase 1 does not include water-quality AI. Phase 1 does not include a mobile application. Phase 1
does not include a cloud-first implementation. Phase 1 does not include a multi-buoy field deployment. Phase 1 does not claim operational disaster-warning capability. Phase 1 predictions shall not be
represented as official safety advisories.
## Terminology

### Real Time
Real time means data is updated frequently enough for local monitoring. It does not imply hard real-time deterministic guarantees for the web dashboard.
### Wave Height
Wave height means the project-defined estimate derived from calibrated pressure and motion measurements. The exact estimator shall be documented and validated.
### Prediction
Prediction means a model-generated estimate for a specified future horizon. It is not a direct measurement.
### Confidence
Confidence is a documented model-quality or uncertainty indicator. It shall not be presented as a probability unless it is calibrated as one.
### Sea Condition
Sea condition is the approved three-class output:
- Calm;
- Moderate;
- Rough.
### Edge
Edge refers to processing on the local Orange Pi Zero 3 (4GB) near or within the buoy system.
### Local Dashboard
Local dashboard means a browser interface reachable over the local network without requiring Internet service.
### Implemented
Implemented means working source code exists and has been exercised in the repository environment.
### Planned
Planned means approved for Phase 1 but not yet completely integrated or validated.
### Future Expansion
Future Expansion means explicitly outside the Phase 1 baseline.
## Current Implementation Status

Project FALCON is in Phase 1 Prototype status. The repository contains an ESP32 captive-portal prototype. The ESP32 prototype provides:
- Wi-Fi access-point mode;
- captive-portal DNS behavior;
- LittleFS setup and diagnostics portal hosting;
- status output;
- monitoring control;
- and restart control.
The repository also contains a laptop-hosted edge-service prototype. The edge-service prototype provides:
- simulated telemetry;
- local REST endpoints;
- SQLite telemetry storage;
- deterministic safety alerts;
- presentation forecast generation;
- forecast backtesting;
- and local dashboard asset hosting.
The repository contains the canonical edge-hosted Dashboard Next application. It includes:
- responsive layouts;
- light and dark modes;
- live telemetry views;
- local notifications;
- alert history;
- current-versus-predicted values;
- and an interactive 3D mechanical model.
The current forecast implementation is a presentation model. It is not yet a field-validated AI model. The current telemetry source is primarily simulated when physical sensors are unavailable. Physical sensor
integration remains Planned until hardware is installed and validated. The selected Orange Pi Zero 3 has not yet been integrated into the physical prototype. The laptop may temporarily represent the edge-computing role during
demonstrations. The full dashboard is bundled with and served by the edge service; it is not approved for direct deployment on the current ESP32 flash because its 3D assets exceed the configured LittleFS capacity.
## System Requirements

### Functional Requirements
The system shall acquire approved sensor readings. The system shall timestamp sensor readings. The system shall validate readings before use. The system shall retain raw or minimally processed data required for
traceability. The system shall estimate current wave height. The system shall predict wave height over a selected 5–15 minute horizon. The system shall classify sea condition as Calm, Moderate, or Rough. The
system shall expose the approved REST API. The system shall display current readings locally. The system shall display predicted wave height separately from current wave height. The system shall display
prediction confidence. The system shall record prediction history. The system shall record alerts and system logs. The system shall allow authorized restart and calibration commands.
### Non-Functional Requirements
The system shall be modular. The system shall be serviceable. The system shall be locally operable. The system shall degrade safely when optional components fail. The system shall avoid fabricated sensor values
in field mode. The system shall distinguish simulated data from live sensor data. The system shall use consistent SI or documented engineering units. The system shall provide readable mobile and desktop
interfaces. The system shall preserve diagnostic logs after recoverable faults where storage permits. The system shall use non-blocking firmware patterns where practical. The system shall be testable at
subsystem boundaries.
## Final Phase 1 Architecture

```text
Sensors
   |
   v
ESP32
   |
   | UART
   v
Orange Pi Zero 3 (4GB)
   |
   | REST API
   v
Local Dashboard
```
Future connectivity is represented only as:
```text
Local System
   |
   v
Cloud (Future Expansion)
```
No cloud component is required for Phase 1 operation. No cloud component is required for Phase 1 demonstration. No cloud component is required for local AI inference.
## Architecture Responsibilities

### Sensors
Sensors convert physical conditions into electrical or digital measurements. Sensors do not make safety decisions. Sensors shall expose calibration and health information where available.
### ESP32
The ESP32 is the deterministic embedded controller. It is responsible for:
- sensor initialization;
- sensor polling;
- basic filtering;
- range checking;
- calibration application;
- timestamp coordination;
- power telemetry;
- GPS parsing;
- UART framing;
- local watchdog handling;
- basic fault reporting;
- and safe restart behavior.
The ESP32 shall continue basic acquisition if the Orange Pi is unavailable.
### UART
UART is the primary Phase 1 link between ESP32 and Orange Pi. Validated local Wi-Fi is an alternate development or fallback transport. Both shall include framing, validation, reconnect behavior, and stale-data detection.
### Orange Pi Zero 3 (4GB)
The Orange Pi Zero 3 (4GB) is the selected edge-processing host. It is responsible for:
- ingesting ESP32 telemetry;
- validating message structure;
- local storage;
- wave-feature processing;
- AI inference;
- sea-condition classification;
- prediction history;
- API hosting;
- dashboard hosting;
- alert aggregation;
- and system logging.
The Orange Pi shall not replace the ESP32's time-critical acquisition role.
### REST API
The REST API is the approved interface between local services and the dashboard. It shall return explicit status codes. It shall distinguish unavailable values from zero values. It shall use documented JSON
schemas.
### Local Dashboard
The dashboard presents measurements and predictions. It does not directly control physical actuators except through approved API commands. It shall clearly label simulated, measured, estimated, and predicted
values.
## End-to-End Data Flow

1. A sensor produces a measurement.
2. The ESP32 reads the sensor.
3. The ESP32 applies calibration metadata.
4. The ESP32 checks validity and range.
5. The ESP32 assigns a timestamp or sequence number.
6. The ESP32 packages the reading into a UART message.
7. The Orange Pi validates the UART or Wi-Fi message.
8. The Orange Pi stores the accepted reading.
9. The wave-processing pipeline updates wave features.
10. The AI pipeline produces a prediction when sufficient valid history exists.
11. The classifier produces Calm, Moderate, or Rough.
12. The API exposes current data and AI results.
13. The dashboard displays current and predicted values separately.
14. Alerts and logs are generated when defined conditions are met.
15. Later measurements are compared with earlier predictions for validation.
## Approved Phase 1 Sensor Set

Only the following sensors are part of the Phase 1 baseline.
### 1. BNO085 IMU
Purpose:
- pitch measurement;
- roll measurement;
- yaw measurement;
- acceleration measurement;
- angular-motion measurement;
- wave-motion feature extraction;
- and orientation context for pressure-derived estimates.
Required outputs:
- pitch in degrees;
- roll in degrees;
- yaw in degrees;
- timestamp;
- calibration state;
- and sensor-health state.
Installation guidance:
- mount near the buoy's rigid central structure;
- align axes with documented buoy axes;
- isolate from loose mechanical vibration;
- record mounting orientation;
- and prevent movement relative to the main frame.
Validation:
- stationary offset test;
- known-angle test;
- repeatability test;
- axis-orientation test;
- and motion-response test.
### 2. Water Pressure Sensor
Purpose:
- detect pressure changes related to water movement;
- support current wave-height estimation;
- provide wave-period features;
- and support AI prediction inputs.
Required outputs:
- raw pressure;
- calibrated pressure;
- pressure change;
- timestamp;
- temperature compensation status when applicable;
- and sensor-health state.
Installation guidance:
- mount at a documented depth;
- prevent trapped air at the sensing face;
- protect wiring through waterproof glands;
- avoid flow obstruction;
- document vertical position relative to the float;
- and provide service access.
Validation:
- static-water baseline;
- known-depth comparison;
- drift test;
- noise test;
- temperature-sensitivity review;
- and dynamic wave-tank or controlled-motion test.
### 3. Wind Speed Sensor
Purpose:
- measure local wind speed;
- provide environmental context for wave development;
- and provide an optional input feature for wave prediction.
Required outputs:
- wind speed;
- engineering unit;
- timestamp;
- validity;
- and health state.
Installation guidance:
- mount above major flow obstructions;
- separate from rotating hazards;
- document mast height;
- and inspect for salt accumulation.
### 4. Wind Direction Sensor
Purpose:
- measure local wind direction;
- provide directional context for wave conditions;
- and support interpretation of buoy motion.
Required outputs:
- direction in degrees;
- cardinal representation for display;
- timestamp;
- validity;
- and health state.
Installation guidance:
- align the reference direction during deployment;
- document magnetic or true-north convention;
- and verify free mechanical movement.
### 5. GPS Module
Purpose:
- record deployment position;
- report current position;
- support mooring-distance checks;
- provide time reference when available;
- and assist recovery.
Required outputs:
- latitude;
- longitude;
- fix type;
- satellite count;
- horizontal accuracy when available;
- speed when valid;
- UTC time when valid;
- and health state.
GPS is not an autonomous-navigation component. GPS drift alerts shall account for expected swing around the anchor.
### 6. Battery Monitor
Purpose:
- battery-voltage measurement;
- battery-current measurement;
- battery-percentage estimation;
- low-power warning;
- and energy-budget validation.
Required outputs:
- voltage;
- current;
- estimated percentage;
- charging or discharging direction;
- timestamp;
- and health state.
Battery percentage is an estimate. Its method shall be documented.
### 7. Solar Monitor
Purpose:
- solar-voltage measurement;
- solar-current measurement;
- charging-status reporting;
- and solar-performance validation.
Required outputs:
- solar voltage;
- solar current;
- calculated solar power when appropriate;
- charging state;
- timestamp;
- and health state.
### 8. Internal Temperature Sensor
Purpose:
- monitor electronics-enclosure temperature;
- detect thermal stress;
- support cooling decisions;
- and protect electronics.
Required outputs:
- internal temperature;
- timestamp;
- threshold state;
- and health state.
The sensor shall be placed where it represents enclosure thermal conditions. It shall not be mounted directly against a localized heat source unless the measurement is explicitly labeled as component
temperature.
### Optional Water Temperature Sensor
Water temperature is optional in Phase 1. If installed, it may provide:
- environmental context;
- pressure-sensor compensation context;
- and an additional monitored value.
Water temperature is not an AI output. Water temperature prediction is not included.
## Sensors Reserved for Future Expansion

The following are not part of the Phase 1 sensor baseline:
- pH;
- salinity;
- turbidity;
- dissolved oxygen;
- rain sensor;
- UV sensor;
- camera;
- hydrophone;
- current meter;
- and Water Quality Index inputs.
These sensors shall not appear as active Phase 1 hardware in official claims. Dashboard placeholders for these sensors shall be removed or explicitly labeled Future Expansion.

The controlled post-approval path for these sensors, an on-demand non-recording
camera, communications improvements, and a conditional Raspberry Pi 5 4GB edge
upgrade is defined in [`FUTURE_UPGRADES.md`](FUTURE_UPGRADES.md). Orange Pi Zero
3 (4GB) remains the approved Phase 1 host, and no future item may be described as
implemented before its procurement, calibration, integration, and validation
evidence exists.

## Sensor Data Quality

Every sensor value shall carry enough context to determine whether it is usable. Recommended metadata includes:
- timestamp;
- sequence number;
- sensor identifier;
- value;
- unit;
- validity;
- calibration version;
- and fault code.
Invalid values shall not be silently converted to zero. Missing values shall be represented as unavailable. Out-of-range values shall be flagged. Stale values shall be flagged. Repeated identical values may
require a stuck-sensor check. Sudden discontinuities shall be logged for review. Filtering shall not destroy the raw evidence needed for validation.
## Sampling and Synchronization

Sampling rates shall be selected through testing. The IMU may require a higher internal sampling rate than dashboard updates. The pressure sensor shall be sampled fast enough to preserve relevant wave dynamics.
Wind data may use a lower output rate than IMU data. GPS may use a lower rate than pressure and IMU data. Power and internal-temperature data may use still lower rates. All data used together for wave
estimation shall be time-aligned. Clock drift between ESP32 and Orange Pi shall be measured. UART sequence numbers shall help detect missing messages. The dashboard refresh rate shall not be treated as the sensor
sample rate.
## Wave-Height Estimation Pipeline

The measured wave-height value is an engineering estimate. It shall be derived through a documented pipeline. The pipeline shall include:
1. pressure-sensor calibration;
2. pressure baseline determination;
3. removal of invalid samples;
4. compensation for sensor depth where required;
5. separation of slow baseline changes from wave-related changes;
6. IMU-based motion context;
7. synchronized analysis window selection;
8. feature extraction;
9. wave-height calculation;
10. quality scoring;
11. comparison with a reference method;
12. and storage of the resulting estimate.
The estimator shall not claim significant wave height unless it implements and validates the appropriate definition. Terminology shall match the implemented method. If the system reports peak-to-trough wave
height, it shall use that label. If the system reports an average over a window, it shall state the window. If the system reports significant wave height, the computation shall be documented.
## Wave Features

Candidate Phase 1 features may include:
- recent wave-height estimates;
- pressure variance;
- pressure range;
- pressure rate of change;
- dominant motion period;
- vertical acceleration statistics;
- pitch statistics;
- roll statistics;
- motion-energy measures;
- recent wind speed;
- recent wind direction encoding;
- and data-quality indicators.
Only validated features shall be included in the final model. Feature selection shall be documented. Feature units shall be documented. Feature scaling shall be documented. Missing-feature handling shall be
documented.
## AI Subsystem

### Approved AI Boundary
The Phase 1 AI subsystem has one prediction task and one classification task. Prediction task:
- estimate wave height 5–15 minutes ahead.
Classification task:
- classify sea condition as Calm, Moderate, or Rough.
The classifier may use the measured or predicted wave state according to the approved design. The chosen basis shall be visible in the API schema.
### Model Strategy
Phase 1 shall prefer a model that is explainable, lightweight, and testable. Candidate approaches may include:
- persistence baseline;
- moving-average baseline;
- damped linear trend;
- linear regression;
- tree-based regression;
- or a compact time-series model.
Only one operational prediction model shall be selected for the final Phase 1 evaluation. Baselines may be retained for comparison. Baselines shall not be misrepresented as separate production AI systems.
### Training Data
The final model shall be trained or calibrated using time-ordered data. Data collection conditions shall be documented. Sensor calibration state shall be documented. Invalid samples shall be excluded according
to written rules. Training and test periods shall be separated chronologically. Random row-level splitting shall be avoided when it leaks future time-series information.
### Prediction Horizons
The approved horizon range is 5–15 minutes. The dashboard may offer 5-minute and 15-minute views. Any intermediate horizon shall be documented. Thirty-minute prediction is outside the approved Phase 1 research
claim. Legacy 30-minute presentation controls shall be removed or moved to Future Expansion.
### Model Inputs
The minimum input is recent validated wave-height history. Pressure and IMU features are primary inputs. Wind data may be used when validated. GPS, battery, solar, and internal temperature are operational
measurements, not default wave-prediction targets.
### Model Outputs
Each AI response shall include:
- model status;
- current wave height;
- predicted wave height;
- horizon in minutes;
- generated timestamp;
- target timestamp;
- confidence or quality indicator;
- sea-condition class;
- input sample count;
- model version;
- and unavailable reason when applicable.
### Transparency
The dashboard shall show current and predicted wave height together. The dashboard shall not display prediction without its horizon. The dashboard shall not display confidence without a documented meaning. The
dashboard shall identify simulated predictions. The dashboard shall identify presentation models. The dashboard shall identify insufficient-history states. The dashboard shall not hide failed predictions behind
nominal values.
### Sea-Condition Classification
The approved outputs are Calm, Moderate, and Rough. Thresholds shall be established from literature, adviser approval, or validation data. Thresholds shall be recorded in configuration. Classification
hysteresis should be considered to prevent rapid class switching. Unavailable wave input shall produce Unavailable status outside the three valid classes. Unavailable is an error state, not a fourth
sea-condition class.
### AI Safety Boundary
AI output is advisory. AI output shall not actuate propulsion. AI output shall not release or move the anchor. AI output shall not autonomously navigate. AI output shall not be represented as an official
weather warning. AI output shall not replace government advisories.
## AI Validation

The AI shall be evaluated with time-ordered measurements. Required evaluation dimensions include:
- mean absolute error;
- root mean squared error when appropriate;
- bias;
- direction accuracy when used;
- coverage of valid predictions;
- inference time;
- and missing-data behavior.
The model shall be compared with at least one simple baseline. A persistence baseline is recommended. Evaluation shall report the horizon. Five-minute and fifteen-minute results shall not be combined without
explanation. Results shall include sample count. Results shall identify simulated versus physical data. Presentation-model scores shall not be reported as field accuracy.
## Dashboard Baseline

The dashboard shall be simplified around the approved research focus. It shall avoid unrelated sensor cards. It shall avoid unsupported AI predictions. It shall emphasize wave state, prediction, confidence, and
system readiness.
## Dashboard Information Architecture

### Home
Home shall show the most important operational information. Required cards:
- System Status;
- Wave Height;
- Predicted Wave Height;
- Sea Condition;
- Prediction Confidence;
- Wind Speed;
- Wind Direction;
- GPS;
- Battery;
- Solar;
- Internal Temperature;
- and active Alerts.
The Home page shall distinguish measured and predicted values visually.
### System Status
System Status shall show:
- ESP32 state;
- Orange Pi edge-host state;
- UART state;
- API state;
- sensor availability;
- monitoring state;
- last update;
- data source;
- and system uptime.
### Motion
Motion shall show:
- pitch;
- roll;
- yaw when available;
- wave motion;
- IMU calibration state;
- and recent motion history.
### GPS
GPS shall show:
- coordinates;
- fix state;
- satellite count;
- reference deployment position;
- anchor-distance estimate;
- and drift status.
### Power
Power shall show:
- battery voltage;
- battery current;
- battery percentage;
- solar voltage;
- solar current;
- charging status;
- and power warnings.
### Thermal
Thermal information shall focus on internal temperature. It may show fan state when cooling hardware exists. It shall not imply installed cooling hardware when hardware is absent.
### Alerts
Alerts shall show:
- severity;
- timestamp;
- code;
- affected subsystem;
- message;
- acknowledgement state when implemented;
- and current or historical state.
### Settings
Settings shall provide approved controls for:
- sampling configuration;
- alert thresholds;
- calibration;
- display preferences;
- and authorized restart.
Settings that are not implemented shall be disabled or labeled Planned.
### Logs
Logs shall contain:
- Wave History;
- Prediction History;
- and System Logs.
### Wave History
Wave History shall show measured or estimated wave height over time. It shall include units and timestamps.
### Prediction History
Prediction History shall preserve:
- prediction creation time;
- prediction horizon;
- predicted value;
- later actual value when available;
- error;
- confidence;
- and model version.
### System Logs
System Logs shall include:
- startup;
- shutdown;
- restart;
- sensor connection changes;
- UART errors;
- storage errors;
- API errors;
- calibration events;
- and critical configuration changes.
## Dashboard Design Requirements

The dashboard shall be responsive. The dashboard shall support desktop and mobile browsers. The dashboard shall support light and dark modes. The dashboard shall use readable typography suitable for projection.
The dashboard shall use consistent icons. The dashboard shall use consistent status colors. Green shall indicate healthy or normal state. Amber shall indicate warning or attention state. Red shall indicate
critical or failed state. Color shall not be the only indicator. Labels and icons shall accompany color states. The dashboard shall avoid excessive decorative animation. Motion shall support comprehension
rather than distraction. The dashboard shall remain usable when animation is reduced. The dashboard shall expose data-source labels. The dashboard shall label simulated data. The dashboard shall label
presentation predictions.
## Digital Twin Boundary

The interactive 3D buoy model is a dashboard visualization aid. It is not an AI responsibility. It may show:
- current pitch;
- current roll;
- approximate wave motion;
- sensor locations;
- component temperature state;
- component fault state;
- and navigation-light state.
It shall not claim exact physical motion unless driven by calibrated measurements. It shall preserve the approved mechanical baseline. It shall not introduce autonomous-navigation concepts.
## Approved REST API

Only the following Phase 1 endpoint set is approved.
```text
GET  /status
GET  /wave
GET  /gps
GET  /battery
GET  /solar
GET  /ai
POST /restart
POST /calibrate
```
Legacy `/api/...` paths may remain temporarily during migration. The final documented interface shall use the approved paths above.
### GET /status
Purpose:
- return overall system and communication status.
Minimum response fields:
- system;
- monitoring;
- uptimeSeconds;
- esp32;
- miniPc;
- uart;
- api;
- sensorsOnline;
- sensorsExpected;
- lastUpdate;
- dataSource;
- and activeAlertCount.
### GET /wave
Purpose:
- return current wave and motion measurements.
Minimum response fields:
- recordedAt;
- waveHeight;
- waveHeightUnit;
- estimationMethod;
- pressure;
- pressureUnit;
- pitch;
- roll;
- yaw;
- waveMotion;
- quality;
- and valid.
### GET /gps
Purpose:
- return GPS and deployment-reference information.
Minimum response fields:
- recordedAt;
- latitude;
- longitude;
- fix;
- satellites;
- horizontalAccuracy;
- referenceLatitude;
- referenceLongitude;
- anchorDistance;
- driftStatus;
- and valid.
### GET /battery
Purpose:
- return battery state.
Minimum response fields:
- recordedAt;
- voltage;
- current;
- percentage;
- direction;
- status;
- and valid.
### GET /solar
Purpose:
- return solar generation and charging state.
Minimum response fields:
- recordedAt;
- voltage;
- current;
- power;
- charging;
- status;
- and valid.
### GET /ai
Purpose:
- return the focused wave prediction and sea-condition classification.
Minimum response fields:
- generatedAt;
- targetAt;
- horizonMinutes;
- currentWaveHeight;
- predictedWaveHeight;
- unit;
- change;
- direction;
- confidence;
- seaCondition;
- model;
- modelVersion;
- sampleCount;
- status;
- and unavailableReason.
### POST /restart
Purpose:
- request an authorized system restart.
The target component shall be explicit when more than one component can restart. The response shall acknowledge that restart was accepted.
### POST /calibrate
Purpose:
- request an authorized sensor calibration operation.
The request shall identify the sensor. The request shall identify calibration type when applicable. The response shall return accepted, completed, or failed state.
## API Conventions

JSON is the default representation. Timestamps shall use ISO 8601 with timezone information. Units shall be explicit. HTTP status codes shall be meaningful. Unavailable data shall not return false zero values.
Bad requests shall return structured error codes. Restart and calibration shall require POST. Read endpoints shall not mutate state. Schemas shall be versioned when breaking changes occur.
## UART Interface

UART is the primary ESP32-to-Orange-Pi transport. The interface shall define:
- baud rate;
- voltage-level compatibility;
- connector pinout;
- frame delimiter;
- message type;
- payload length;
- sequence number;
- timestamp;
- checksum or CRC;
- timeout;
- and retry behavior.
Recommended message categories include:
- STATUS;
- WAVE;
- MOTION;
- GPS;
- BATTERY;
- SOLAR;
- TEMPERATURE;
- ALERT;
- CALIBRATION;
- and HEARTBEAT.
Malformed frames shall be rejected. Rejected frames shall be counted. Sequence gaps shall be logged. The Orange Pi shall not block ESP32 acquisition while processing a frame.
## Firmware Architecture

The firmware shall remain modular. Approved top-level firmware modules are:
```text
firmware/
├── sensors/
├── power/
├── gps/
├── dashboard/
├── storage/
├── wifi/
├── api/
├── ai_bridge/
├── config/
├── diagnostics/
├── communication/
└── main.cpp
```
The required named modules from the research baseline are:
- sensors;
- power;
- gps;
- dashboard;
- storage;
- wifi;
- api;
- and ai_bridge.
Diagnostics, configuration, and communication helpers may support them.
## Firmware Module Responsibilities

### sensors
- initialize approved sensors;
- read sensors without unnecessary blocking;
- apply calibration;
- validate values;
- expose health state;
- and publish timestamped measurements.
### power
- read battery voltage;
- read battery current;
- estimate battery percentage;
- read solar voltage;
- read solar current;
- determine charging state;
- and report power warnings.
### gps
- parse GPS messages;
- validate fix state;
- publish coordinates;
- manage reference position;
- calculate anchor distance;
- and report drift state.
### dashboard
- provide only the embedded fallback interface when required;
- avoid hosting assets larger than available flash;
- and expose clear local status.
The full Phase 1 dashboard is expected to run from the Orange Pi Zero 3.
### storage
- store configuration;
- store calibration metadata;
- retain essential logs;
- enforce storage limits;
- and recover safely from incomplete writes.
### wifi
- configure local connectivity;
- manage access-point mode when required;
- report link state;
- and avoid exposing undocumented services.
### api
- implement approved local endpoints where hosted;
- validate requests;
- return structured errors;
- and avoid blocking acquisition.
### ai_bridge
- transport validated sensor data to the Orange Pi;
- receive AI status when needed;
- report link failures;
- and never fabricate AI results.
The ESP32 is not required to execute the Phase 1 AI model.
## Firmware Runtime Principles

The firmware shall avoid long blocking delays. The firmware shall use periodic tasks or a scheduler. Sensor acquisition shall have priority over dashboard requests. UART transmission shall not starve sensor
polling. Watchdog servicing shall be explicit. Recoverable sensor failures shall not restart the entire system immediately. Repeated unrecoverable faults may trigger a controlled restart. Restart reason shall
be logged. Configuration shall be validated before use. Defaults shall be safe and documented.
## Mini-PC Software Architecture

The Orange Pi edge software shall contain focused services. Recommended structure:
```text
orange_pi/
├── ingestion/
├── validation/
├── wave_processing/
├── ai/
├── storage/
├── alerts/
├── api/
├── dashboard_host/
├── config/
└── service.py
```
The ingestion service reads UART data. The validation service checks structure and ranges. The wave-processing service derives wave estimates and features. The AI service produces the approved outputs only. The
storage service retains measurements, predictions, and logs. The alert service applies deterministic operational rules. The API service exposes approved endpoints. The dashboard host serves local static assets.
## Storage Model

The local data store shall prioritize traceability. Recommended records include:
- sensor sample;
- wave estimate;
- AI prediction;
- prediction evaluation;
- GPS fix;
- battery sample;
- solar sample;
- internal-temperature sample;
- alert;
- calibration event;
- and system log.
### Sensor Sample
Minimum fields:
- id;
- recordedAt;
- source;
- sensorId;
- value;
- unit;
- valid;
- quality;
- and calibrationVersion.
### AI Prediction Record
Minimum fields:
- id;
- generatedAt;
- targetAt;
- horizonMinutes;
- currentWaveHeight;
- predictedWaveHeight;
- confidence;
- seaCondition;
- modelVersion;
- sampleCount;
- status;
- actualWaveHeight when later available;
- and absoluteError when later available.
### Retention
Retention periods shall be configurable. Storage exhaustion shall be prevented. Critical logs shall be retained longer than routine dashboard samples where practical. Database backup is a local maintenance
function. Cloud backup is Future Expansion.
## Alert System

Alerts are deterministic operational outputs unless explicitly labeled AI-derived context. Approved severity levels are:
- Info;
- Warning;
- Critical.
Phase 1 shall avoid excessive severity categories.
### Candidate Alerts
- pressure sensor unavailable;
- IMU unavailable;
- wind sensor unavailable;
- GPS fix lost;
- battery low;
- battery critical;
- solar charging unavailable during expected daylight;
- internal temperature high;
- internal temperature critical;
- UART disconnected;
- API unavailable;
- storage nearing capacity;
- prediction unavailable;
- prediction input stale;
- and sustained anchor-distance warning.
### Alert Requirements
Every alert shall have a code. Every alert shall have a timestamp. Every alert shall identify its subsystem. Every alert shall have a human-readable message. Every alert shall avoid ambiguous wording. Repeated
alerts shall be rate-limited or grouped. Resolved alerts shall be distinguishable from active alerts when resolution tracking is implemented.
## Mechanical Baseline

Mechanical Revision 5 replaces the former four-outrigger production direction with a compact traditional single-body buoy. Legacy Revision 4 stabilizer components remain archived for traceability.
### Traditional HDPE Main Float V2
`MAIN_FLOAT_TRADITIONAL_V2` provides primary buoyancy through a Ø650 mm cylindrical upper body and a 240 mm rounded tapered underwater keel. It supports the central frame, electronics enclosure, solar assembly,
upper sensor structure, and central mooring load path. Its nominal overall height is 620 mm with a 6 mm marine-grade HDPE wall. It shall be inspected for cuts, deformation, water ingress, and interference.
### Legacy Outrigger System
The four stabilizer buoys, marine aluminum arms, cradles, and radial tension cables are excluded from the Revision 5 production build. They shall remain in source control and the master CAD archive but shall be
suppressed or hidden in the Revision 5 representation. Removal of their stability contribution requires renewed flotation, heel, roll-recovery, pitch-recovery, and freeboard validation.
### Central Ballast
The ballast lowers the center of gravity. It improves righting moment. It assists upright recovery after disturbance. Its attachment shall include a secondary retention strategy where practical.
### Single Anchor
Phase 1 uses a single-anchor mooring system. The anchor connects beneath the central structure through the approved mooring arrangement. The system shall allow expected swing around the reference position.
Anchor-distance thresholds shall account for line length and GPS uncertainty.
### Electronics Enclosure
The enclosure protects electronics from water, salt, humidity, and mechanical exposure. It should meet IP67 or better design intent. It shall use suitable cable glands. It shall provide strain relief. It shall
support inspection and service. Condensation risk shall be addressed.
### Solar Assembly
The solar assembly shall remain mechanically secure. Tilted solar-panel geometry may be used when supported by the approved CAD model. Panel tilt shall not compromise stability, wind loading, access, or sensor
clearance. Mechanical validation remains required.
## Mechanical Design Rules

Reliability has priority over cosmetic appearance. Stability has priority over compactness. Service access shall be preserved. Sharp exposed edges shall be avoided. Fasteners shall resist loosening.
Galvanic-corrosion risks shall be reviewed where dissimilar metals meet. Cable paths shall avoid abrasion. Water-facing components shall tolerate marine exposure or be protected. The CAD model shall use
meaningful component names. CAD revisions shall be archived.
## Power Architecture

The approved Phase 1 power chain is:
```text
Solar Panel
    |
    v
MPPT Charge Controller
    |
    v
12 V LiFePO4 Battery
    |
    v
Power Distribution
    |
    +--> ESP32
    |
    +--> Orange Pi Zero 3 (4GB)
    |
    +--> Sensors
```
## Power-System Responsibilities

### Solar Panel
- harvest solar energy;
- tolerate outdoor exposure;
- remain securely mounted;
- and provide adequate output for the validated energy budget.
### MPPT Charge Controller
- regulate solar charging;
- respect LiFePO4 requirements;
- expose charging state where possible;
- and protect the battery from invalid charging conditions.
### 12 V LiFePO4 Battery
- store energy;
- supply overnight operation;
- tolerate the planned current draw;
- and include suitable protection.
LiFePO4 is preferred for cycle life, voltage stability, and safety characteristics.
### Power Distribution
- provide fused branches;
- provide correct regulated voltages;
- isolate faults where practical;
- prevent reverse polarity;
- and document connector ratings.
### Energy Budget
The energy budget shall include:
- ESP32 average current;
- Orange Pi average, peak, and startup power;
- sensor consumption;
- GPS consumption;
- cooling consumption when installed;
- regulator loss;
- nighttime duration;
- cloudy-day margin;
- and battery reserve.
Power autonomy shall be demonstrated by measurement. It shall not be claimed from nominal battery capacity alone.
## Operating States

### Normal Monitoring
- approved sensors active;
- ESP32 acquisition active;
- UART active;
- Orange Pi active when power permits;
- API active;
- dashboard available;
- and local storage active.
### Reduced-Power Monitoring
- essential sensing continues;
- nonessential display activity may reduce;
- AI inference frequency may reduce;
- and GPS update frequency may reduce when justified.
### Critical Battery State
- preserve essential ESP32 operation;
- preserve critical logging;
- reduce Orange Pi load when required;
- avoid unsafe battery discharge;
- and report the state locally.
Power states shall not be labeled autonomous decision making. They are deterministic power-management policies.
## Communication Architecture

Phase 1 communication consists of:
- sensor buses to ESP32;
- UART from ESP32 to Orange Pi;
- local network access to REST API;
- and local browser access to the dashboard.
Internet connectivity is optional and not required. LTE is Future Expansion. LoRa is Future Expansion. Satellite communication is Future Expansion. Multi-buoy networking is Future Expansion.
## Local Networking

The local network shall have a documented IP plan. Service ports shall be documented. Default credentials shall be changed before field deployment. The dashboard shall show connection state. The API shall not
depend on public DNS. The system shall recover from temporary client disconnects.
## Cybersecurity Baseline

Phase 1 security shall be proportional to a local prototype while avoiding unsafe defaults. Requirements include:
- non-default strong Wi-Fi credentials for field use;
- input validation;
- bounded request sizes;
- no undocumented control endpoints;
- POST for mutating operations;
- configuration protection;
- logging of restart and calibration requests;
- dependency tracking;
- and no secrets committed to public source control.
HTTPS may be constrained on the embedded local system. The limitation shall be documented. Cloud identity and certificates are Future Expansion.
## Configuration Management

Configuration shall be separate from measurement data. Configuration items may include:
- device identifier;
- sensor identifiers;
- sensor calibration coefficients;
- sampling intervals;
- UART parameters;
- GPS reference position;
- expected anchor radius;
- alert thresholds;
- sea-condition thresholds;
- model path;
- model version;
- retention limits;
- and display defaults.
Configuration changes shall be validated. Invalid configuration shall fall back to documented safe defaults. Configuration version shall be recorded.
## Calibration

Calibration is required before research measurements are treated as valid.
### IMU Calibration
- verify axis mapping;
- verify stationary offsets;
- perform vendor-required calibration;
- record calibration status;
- and verify mounting alignment.
### Pressure Calibration
- establish zero or atmospheric reference as appropriate;
- compare with known pressure or depth;
- document sensor depth;
- evaluate drift;
- and record coefficients.
### Wind-Speed Calibration
- compare with a reference instrument or controlled airflow;
- document conversion factor;
- and verify zero-wind response.
### Wind-Direction Calibration
- align to documented north reference;
- verify full rotation;
- and record angular offset.
### Battery Calibration
- compare voltage with a calibrated meter;
- compare current with a calibrated meter;
- and document percentage-estimation method.
### Solar Calibration
- compare voltage and current with reference measurements;
- and verify charging-state logic.
### Temperature Calibration
- compare with a reference thermometer;
- document sensor location;
- and evaluate local heat-source bias.
## Testing Strategy

Testing is divided into six required categories.
1. Mechanical testing.
2. Electrical testing.
3. Sensor testing.
4. AI testing.
5. Dashboard testing.
6. Communication testing.
## Mechanical Testing

Required mechanical tests include:
- visual inspection;
- flotation test;
- static stability test;
- added-load test;
- roll recovery test;
- pitch recovery test;
- tapered-keel inspection;
- loaded-freeboard and static-heel measurement;
- single-body roll/pitch recovery observation;
- ballast-retention test;
- anchor attachment test;
- enclosure splash test;
- cable-strain test;
- and controlled wave-response test.
Mechanical acceptance evidence shall include photographs, test conditions, observations, and pass/fail results.
## Electrical Testing

Required electrical tests include:
- polarity verification;
- continuity test;
- fuse verification;
- regulator output test;
- idle-current measurement;
- normal-load measurement;
- peak-load measurement;
- solar charging test;
- battery discharge test;
- low-voltage behavior;
- brownout recovery;
- ESP32 restart recovery;
- Orange Pi startup behavior;
- grounding review;
- and thermal observation.
## Sensor Testing

Every installed sensor shall be tested for:
- detection;
- initialization;
- accuracy;
- repeatability;
- stability;
- noise;
- range behavior;
- missing-data behavior;
- disconnect behavior;
- reconnect behavior;
- timestamp quality;
- calibration persistence;
- and dashboard representation.
Sensor test data shall identify the reference instrument.
## AI Testing

Required AI tests include:
- insufficient-history handling;
- invalid-input handling;
- stale-input handling;
- 5-minute prediction evaluation;
- 15-minute prediction evaluation;
- baseline comparison;
- mean absolute error;
- bias assessment;
- inference-time measurement;
- confidence behavior;
- Calm classification;
- Moderate classification;
- Rough classification;
- boundary stability;
- and prediction-history integrity.
Physical-data results shall be separated from simulator results.
## Dashboard Testing

Required dashboard tests include:
- desktop layout;
- tablet layout;
- mobile layout;
- light mode;
- dark mode;
- readable typography;
- navigation drawer;
- current wave display;
- predicted wave display;
- confidence display;
- alert visibility;
- missing-data state;
- offline state;
- API-error state;
- chart resizing;
- history rendering;
- restart control;
- calibration control;
- keyboard focus;
- reduced-motion preference;
- and local-network loading.
## Communication Testing

Required communication tests include:
- UART startup;
- valid frame transfer;
- checksum failure;
- partial frame;
- sequence gap;
- high message rate;
- ESP32 disconnect;
- Orange Pi restart;
- automatic reconnect;
- API availability;
- malformed API request;
- browser refresh;
- multiple local clients;
- and local-network interruption.
## Test Evidence

Each formal test shall record:
- test identifier;
- objective;
- setup;
- equipment;
- software version;
- hardware version;
- environmental condition;
- procedure;
- expected result;
- actual result;
- pass or fail;
- observations;
- and corrective action.
## Acceptance Criteria

Phase 1 acceptance criteria shall be finalized with the adviser before field claims. Minimum categories shall include:
- stable controlled flotation;
- no observed water ingress during the approved test;
- continuous sensor acquisition for the test duration;
- valid UART transfer;
- local API availability;
- responsive dashboard access;
- explicit current and predicted wave values;
- recorded AI validation results;
- correct three-class sea-condition output;
- power operation for the defined test duration;
- and recoverable behavior after planned faults.
Passing a demonstration is not equivalent to passing field validation.
## Deployment Workflow

### 1. Documentation Check
- confirm approved design revision;
- confirm firmware version;
- confirm model version;
- confirm calibration records;
- and confirm test status.
### 2. Mechanical Inspection
- inspect main float;
- inspect the rounded tapered keel;
- verify the legacy outrigger system is absent from the Revision 5 build;
- verify loaded freeboard and ballast clearance;
- inspect ballast;
- inspect anchor connection;
- inspect solar mounts;
- and inspect enclosure mounting.
### 3. Electrical Inspection
- verify battery voltage;
- verify charging state;
- verify fuses;
- verify regulators;
- verify connectors;
- and verify enclosure seals.
### 4. Sensor Inspection
- verify IMU calibration;
- verify pressure baseline;
- verify wind sensors;
- verify GPS fix;
- verify battery monitor;
- verify solar monitor;
- and verify internal temperature.
### 5. Communication Inspection
- verify ESP32 startup;
- verify UART;
- verify Orange Pi;
- verify REST API;
- and verify dashboard access.
### 6. AI Readiness
- verify model file;
- verify model version;
- verify sufficient input history;
- verify current wave value;
- verify prediction horizon;
- verify confidence state;
- and verify sea-condition output.
### 7. Deployment
- record site conditions;
- record coordinates;
- establish GPS reference;
- deploy anchor;
- verify expected swing radius;
- verify live telemetry;
- and begin the approved observation period.
### 8. Recovery
- stop data collection safely;
- record final status;
- retrieve buoy;
- inspect for damage;
- export data;
- and document anomalies.
## Maintenance

Maintenance shall be preventive and evidence-based.
### Before Every Deployment
- inspect seals;
- inspect cable glands;
- inspect fasteners;
- inspect the tapered keel and HDPE shell;
- inspect ballast clearance below the keel;
- verify the single-body stability-test record;
- inspect ballast;
- inspect anchor line;
- clean solar panels;
- verify battery;
- verify sensors;
- and verify calibration status.
### After Every Deployment
- rinse salt residue;
- inspect corrosion;
- inspect biofouling;
- inspect water ingress;
- inspect connectors;
- inspect mechanical deformation;
- export logs;
- back up research data;
- and record maintenance actions.
### Periodic Maintenance
- recalibrate sensors according to the approved schedule;
- review battery capacity;
- review solar performance;
- inspect enclosure venting;
- update approved software;
- and verify stored configuration.
## Failure Behavior

### Pressure Sensor Failure
- mark current wave height unavailable if no validated fallback exists;
- suspend AI prediction when required inputs are missing;
- log the failure;
- and notify the dashboard.
### IMU Failure
- mark motion data unavailable;
- reduce wave-estimate quality when appropriate;
- log the failure;
- and notify the dashboard.
### Wind Sensor Failure
- continue core wave monitoring when possible;
- mark wind input unavailable;
- avoid fabricated wind values;
- and log the failure.
### GPS Failure
- continue local wave monitoring;
- mark position unavailable;
- suspend drift evaluation;
- and retry acquisition.
### UART Failure
- ESP32 continues acquisition;
- Orange Pi marks telemetry stale;
- API reports degraded state;
- dashboard reports communication failure;
- and reconnection is attempted.
### Mini-PC Failure
- ESP32 continues basic acquisition and health reporting;
- AI becomes unavailable;
- full dashboard becomes unavailable unless an embedded fallback exists;
- and recovery is attempted without falsifying predictions.
### Low Battery
- issue warning;
- apply approved deterministic power policy;
- preserve essential monitoring;
- and record the event.
### Internal Overtemperature
- issue warning or critical alert according to thresholds;
- activate cooling only when hardware is installed and approved;
- reduce nonessential load when approved;
- and record peak temperature.
## Risk Register

| Risk | Impact | Primary Mitigation |
| --- | --- | --- |
| Water ingress | Electronics loss | Sealed enclosure, glands, inspection, controlled waterproof testing |
| Battery depletion | Monitoring interruption | Solar sizing, energy budget, low-power policy, battery alert |
| Pressure-sensor drift | Incorrect wave estimate | Calibration, baseline tracking, reference comparison |
| IMU misalignment | Incorrect motion features | Fixed mounting, axis documentation, known-angle calibration |
| UART data loss | Missing edge data | Framing, sequence numbers, CRC, reconnect logic |
| Mini-PC failure | AI and full dashboard unavailable | ESP32 independent acquisition and clear degraded state |
| GPS uncertainty | False drift alert | Accuracy checks, sustained thresholds, mooring-radius allowance |
| Corrosion | Mechanical or electrical failure | Marine materials, isolation, rinsing, periodic inspection |
| Biofouling | Sensor bias | Protective placement and cleaning schedule |
| Excessive wave loading | Structural damage or excessive heel | Rounded keel, low ballast, controlled stability/wave validation |
| Model overfitting | Misleading predictions | Time-ordered validation, baseline comparison, honest reporting |
| Simulated-data confusion | Invalid research claim | Prominent data-source labels and separated results |
| Dashboard overload | Poor operator awareness | Focused cards, readable hierarchy, alert prioritization |
## Engineering Principles

### Focus
One validated contribution is preferred over many unsupported features.
### Reliability
Monitoring reliability has priority over decorative features.
### Modularity
Sensors, controller, edge computer, power system, and mechanical components shall be independently serviceable where practical.
### Transparency
Measured, estimated, predicted, simulated, and unavailable states shall be distinguishable.
### Local-First Operation
Core Phase 1 functions shall not depend on cloud availability.
### Safety
Prototype predictions shall not be presented as official warnings.
### Maintainability
Clear naming, documentation, tests, and version control are required.
### Evidence
Claims shall be supported by tests and recorded results.
## Repository Structure

The target repository structure is:
```text
Project-FALCON/
├── firmware/
│   ├── sensors/
│   ├── power/
│   ├── gps/
│   ├── dashboard/
│   ├── storage/
│   ├── wifi/
│   ├── api/
│   └── ai_bridge/
├── dashboard/
│   ├── assets/
│   ├── models/
│   ├── scripts/
│   ├── styles/
│   └── index.html
├── orange_pi/
│   ├── ingestion/
│   ├── wave_processing/
│   ├── storage/
│   ├── alerts/
│   ├── api/
│   └── service/
├── hardware/
│   ├── schematics/
│   ├── pinout/
│   ├── wiring/
│   └── bom/
├── mechanical/
│   ├── cad/
│   ├── exports/
│   ├── drawings/
│   └── assembly/
├── documentation/
│   ├── architecture/
│   ├── calibration/
│   ├── deployment/
│   ├── maintenance/
│   └── research/
├── api/
│   ├── schema/
│   └── examples/
├── ai/
│   ├── data/
│   ├── features/
│   ├── training/
│   ├── inference/
│   ├── evaluation/
│   └── models/
├── test/
│   ├── mechanical/
│   ├── electrical/
│   ├── sensors/
│   ├── ai/
│   ├── dashboard/
│   └── communication/
└── PROJECT_CONTEXT.md
```
The current repository may migrate incrementally. Migration shall preserve working code and history. Folders shall not be renamed solely for appearance when doing so breaks active workflows.
## Documentation Set

Supporting documents should include:
- system architecture;
- API specification;
- UART protocol;
- firmware specification;
- sensor specification;
- calibration guide;
- power-system specification;
- hardware schematic;
- pinout;
- mechanical assembly guide;
- deployment guide;
- test plan;
- user manual;
- maintenance guide;
- security notes;
- troubleshooting guide;
- changelog;
- and version history.
Supporting documents shall link back to this master context.
## Documentation Style

Use professional engineering language. Use consistent component names. Use consistent units. Use explicit status labels. Avoid marketing claims that exceed evidence. Avoid describing Future Expansion as
implemented. Avoid using AI as a vague label for deterministic rules. Avoid duplicate requirements across multiple documents where a reference is sufficient. Use diagrams where they improve clarity. Record
assumptions. Record unresolved decisions. Record validation evidence.
## Change Control

Changes to the research focus require adviser approval. Changes to the AI responsibilities require adviser approval. Changes to the core sensor set require engineering review. Changes to the mechanical baseline
require mechanical review. Changes to the power architecture require electrical review. Breaking API changes require a versioned migration plan. Model changes require a new model version and evaluation record.
Calibration changes require updated metadata. Every approved change shall update relevant documentation.
## Phase 1 Roadmap

### Gate 1: Documentation Baseline
- approve PROJECT_CONTEXT.md v4;
- align supporting documents;
- remove conflicting Phase 1 claims;
- and approve terminology.
### Gate 2: Hardware Readiness
- acquire approved sensors;
- finalize wiring;
- verify power components;
- inspect mechanical assembly;
- and record hardware revisions.
### Gate 3: Sensor Integration
- integrate BNO085;
- integrate water-pressure sensor;
- integrate wind speed;
- integrate wind direction;
- integrate GPS;
- integrate battery monitor;
- integrate solar monitor;
- integrate internal-temperature sensor;
- and complete calibration.
### Gate 4: Communication Integration
- define UART protocol;
- implement framing;
- implement validation;
- test reconnect behavior;
- and integrate Orange Pi ingestion.
### Gate 5: Wave Estimation
- collect controlled data;
- implement pressure preprocessing;
- synchronize IMU;
- define wave-height method;
- compare with reference;
- and document quality limits.
### Gate 6: AI Model
- define input window;
- create baseline;
- select one operational model;
- train with time-ordered data;
- validate 5-minute horizon;
- validate 15-minute horizon;
- implement three-class output;
- and document limitations.
### Gate 7: Dashboard and API
- migrate to approved endpoints;
- simplify dashboard cards;
- remove unrelated predictions;
- implement current-versus-predicted view;
- implement histories;
- implement settings;
- and complete responsive testing.
### Gate 8: Integrated Testing
- complete mechanical tests;
- complete electrical tests;
- complete sensor tests;
- complete AI tests;
- complete dashboard tests;
- complete communication tests;
- and resolve critical defects.
### Gate 9: Controlled Deployment
- complete readiness review;
- perform controlled deployment;
- record data;
- recover system;
- analyze results;
- and document conclusions.
## Success Metrics

Project success shall be evaluated against focused metrics.
### Monitoring Metrics
- percentage of expected samples acquired;
- percentage of valid pressure samples;
- percentage of valid IMU samples;
- GPS availability;
- UART delivery rate;
- dashboard availability;
- and local storage continuity.
### Wave Metrics
- wave-estimate agreement with reference;
- estimator bias;
- estimator repeatability;
- and valid-estimate coverage.
### AI Metrics
- 5-minute prediction MAE;
- 15-minute prediction MAE;
- baseline comparison;
- valid-prediction coverage;
- inference latency;
- and sea-condition classification performance.
### Power Metrics
- average consumption;
- peak consumption;
- solar energy collected;
- overnight reserve;
- and operation during the test duration.
### Usability Metrics
- dashboard task completion;
- alert visibility;
- mobile readability;
- desktop readability;
- and correct interpretation of current versus predicted values.
## Future Expansion

Everything in this section is outside the Phase 1 baseline. Future work shall not be mixed into Phase 1 claims.
### Environmental Sensors
- pH;
- salinity;
- turbidity;
- dissolved oxygen;
- rain;
- UV;
- hydrophone;
- current meter;
- and Water Quality Index.
### Expanded AI
- weather prediction;
- ocean-current prediction;
- typhoon prediction;
- storm prediction;
- fish prediction;
- maintenance prediction;
- self-learning AI;
- multiple operational AI models;
- cloud AI;
- camera AI;
- computer vision;
- and water-quality AI.
### Communications
- LTE;
- LoRa;
- satellite communication;
- multi-buoy networking;
- mesh networking;
- and remote fleet telemetry.
### Platforms
- cloud dashboard;
- mobile application;
- fleet-management portal;
- remote configuration;
- and cloud archival.
### Mechanical and Operational Expansion
- multi-buoy deployment;
- alternate mooring arrangements;
- larger deployment endurance;
- harsher-environment qualification;
- and additional service tooling.
### Autonomous Functions
- autonomous decision making;
- autonomous navigation;
- and autonomous repositioning.
These functions require a separate safety case and are not inherited automatically from Phase 1.
## Explicitly Removed v3 Claims

The following concepts are no longer part of the Phase 1 description:
- general-purpose marine AI;
- national autonomous buoy network as a current objective;
- cloud platform as a required subsystem;
- mobile application as a required subsystem;
- remote telemetry as a required Phase 1 outcome;
- multi-model AI operation;
- autonomous maintenance prediction;
- harmful algal bloom prediction;
- marine debris detection;
- camera processing;
- satellite communication;
- mesh networking;
- and broad disaster-monitoring capability.
They remain only as possible Future Expansion items.
## Research Reporting Rules

Reports shall identify the data source. Reports shall separate simulator data from physical sensor data. Reports shall identify the prediction horizon. Reports shall state the number of samples. Reports shall
state the reference method. Reports shall state calibration status. Reports shall state environmental conditions. Reports shall state model version. Reports shall state known limitations. Reports shall not
generalize beyond the tested conditions without justification. Reports shall not claim tsunami, typhoon, storm, or weather prediction. Reports shall not claim operational public-safety readiness.
## Demonstration Rules

Demonstration mode may use simulated sensor data. Simulated data shall be labeled clearly. Presentation predictions shall be labeled clearly. Fault scenarios may be injected for demonstration. Injected faults
shall not be confused with hardware failures. The digital twin may visualize simulated motion. The demonstration shall explain that physical sensors and Orange Pi hardware may still be pending. The demonstration
shall focus on architecture, data flow, usability, and planned validation.
## Traceability Matrix

| Research need | System element | Verification |
| --- | --- | --- |
| Real-time wave monitoring | Pressure sensor, IMU, ESP32 | Sensor and communication tests |
| Short-term prediction | Mini-PC AI service | Time-ordered AI evaluation |
| Sea-condition class | AI classifier | Classification test set |
| Local operation | REST API and dashboard | Offline local-network test |
| Solar operation | Solar, MPPT, battery | Electrical endurance test |
| Stable platform | Single-body float, rounded keel, central ballast | Mechanical testing |
| Position awareness | GPS | Reference-position test |
| Transparent prediction | Current/predicted dashboard cards | Dashboard usability test |
| Fault awareness | Alerts and logs | Injected-fault test |
| Maintainability | Modular hardware and software | Inspection and replacement exercise |
## Open Engineering Decisions

The Orange Pi Zero 3 (4GB) is selected; procurement and integration remain pending. The exact water-pressure sensor remains to be finalized. The exact wind-speed sensor remains to be finalized. The exact wind-direction sensor remains to be
finalized. The exact GPS module remains to be finalized. The exact battery-monitor device remains to be finalized. The exact solar-monitor device remains to be finalized. The exact internal-temperature sensor
remains to be finalized. The final sampling rates remain to be validated. The final UART baud rate remains to be approved. The final wave-height estimator remains to be validated. The final AI model remains to
be selected after data collection. The final Calm, Moderate, and Rough thresholds remain to be validated. The final power budget remains to be measured. The final field-test site and permits remain to be
confirmed.
## Definition of Done for Phase 1

Phase 1 is complete only when:
- the approved mechanical baseline is assembled;
- the approved core sensors are installed;
- calibration records exist;
- ESP32 acquisition is operational;
- UART communication is operational;
- Orange Pi edge services are operational;
- the approved REST API is operational;
- current wave height is validated against a reference;
- 5–15 minute prediction is evaluated on physical data;
- Calm, Moderate, and Rough classification is evaluated;
- the simplified dashboard is operational;
- histories and logs are retained;
- solar-power behavior is tested;
- all six required testing categories are documented;
- critical defects are resolved or explicitly accepted;
- and research limitations are documented.
## Version History

### v1
- initial concept;
- basic IoT buoy direction;
- and early local monitoring ideas.
### v2
- HDPE mechanical direction;
- ESP32 dashboard concept;
- edge-computing concept;
- and expanded power architecture.
### v3
- four-stabilizer mechanical baseline;
- tension-cable reinforcement;
- modular firmware direction;
- broad AI and cloud concepts;
- and comprehensive but overly broad master context.
### v4.0
- narrowed research to real-time coastal monitoring;
- narrowed AI to 5–15 minute wave-height prediction and three-class sea-condition classification;
- defined approved Phase 1 sensors;
- moved unrelated sensors and AI capabilities to Future Expansion;
- simplified final architecture;
- simplified API endpoint set;
- simplified dashboard information architecture;
- retained approved mechanical and power baselines;
- clarified current implementation versus planned integration;
- rewrote the research gap and objectives;
- strengthened validation and transparency requirements;
- and established this document as the official v4 source of truth.
### v5.0
- adopted `MAIN_FLOAT_TRADITIONAL_V2` as the current mechanical direction;
- replaced the production outrigger arrangement with a Ø650 mm single body and 240 mm rounded tapered keel;
- retained Revision 4 stabilizer components only as archived legacy geometry;
- required ballast relocation below the deeper keel;
- required renewed flotation, freeboard, heel, and roll/pitch recovery validation;
- identified pre-August-13 3D exports as legacy assets pending replacement.
## Final Authority Statement

PROJECT_CONTEXT.md v5.0 is the authoritative Phase 1 engineering context for Project FALCON. All firmware shall align with its focused sensor and architecture boundaries. All dashboard work shall align with its
simplified information architecture. All AI work shall remain limited to short-term wave-height prediction and Calm, Moderate, or Rough classification. All API work shall migrate toward the approved eight
endpoints. All mechanical work shall preserve the approved Phase 1 baseline unless formally reviewed. All research reporting shall distinguish implemented, planned, simulated, and future capabilities. Any
proposal outside this baseline belongs in Future Expansion until approved through change control. This document supersedes PROJECT_CONTEXT.md v4.0.
