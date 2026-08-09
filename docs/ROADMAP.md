# Project FALCON Development Roadmap v4.0

## Document Control

| Field | Value |
| --- | --- |
| Project | Project FALCON-01 |
| Status | Phase 1 Prototype |
| Authority | PROJECT_CONTEXT.md v4.0 |
| Scope | Real-time coastal monitoring and 5–15 minute wave-height prediction |
| Updated | 2026-08-09 |

## Roadmap Rules

- A phase is complete only when its exit criteria have evidence.
- Source-backed behavior may be labeled Implemented.
- Approved but unfinished work shall be labeled Planned or In Progress.
- Simulator results shall not satisfy physical-sensor or field-validation gates.
- Future Expansion shall not be inserted into Phase 1 deliverables.
- The AI remains limited to short-term wave-height prediction and Calm, Moderate, or Rough classification.

## Current Baseline

Implemented:

- ESP32 PlatformIO firmware foundation;
- Wi-Fi access point and captive portal;
- LittleFS fallback dashboard;
- basic ESP32 status, monitoring, and restart routes;
- laptop-hosted edge-service prototype;
- local SQLite storage;
- simulated telemetry and alert scenarios;
- presentation forecasting and backtesting;
- responsive dashboard with light/dark themes;
- current-versus-predicted UI;
- and an interactive Fusion-derived digital twin.

Not yet complete:

- acquisition and installation of all approved sensors;
- final UART protocol and physical ESP32-to-mini-PC link;
- final mini-PC installation;
- calibrated wave-height estimation;
- physical coastal dataset;
- final trained/selected wave-prediction model;
- field AI validation;
- measured solar endurance;
- and controlled coastal deployment.

## Gate 1 — Documentation Baseline

**Status:** In Progress

### Deliverables

- PROJECT_CONTEXT.md v4.0;
- README.md v4 alignment;
- ROADMAP.md v4 alignment;
- HARDWARE.md v4 alignment;
- SOFTWARE.md v4 alignment;
- AI.md v4 alignment;
- DASHBOARD.md v4 alignment;
- API.md v4 alignment;
- MECHANICAL.md v4 alignment;
- and updated documentation index.

### Exit Criteria

- all documents use the focused research scope;
- all documents use the approved sensor set;
- all documents use the final Phase 1 architecture;
- all documents limit AI to two responsibilities;
- removed features appear only under delimitations or Future Expansion;
- and no document presents planned hardware as installed.

## Gate 2 — Mechanical Readiness

**Status:** In Progress / Planned Validation

### Approved Baseline

- HDPE main float;
- four HDPE stabilizer buoys;
- marine aluminum arms;
- stainless steel tension cables;
- central ballast;
- single anchor;
- waterproof electronics enclosure;
- and tilted solar-panel assembly where represented by the approved CAD revision.

### Deliverables

- controlled CAD assembly;
- archived source and exchange files;
- component naming convention;
- mechanical bill of materials;
- assembly sequence;
- inspection checklist;
- and test-ready prototype.

### Exit Criteria

- all structural parts are identified;
- ballast and anchor attachments have retention provisions;
- sensor and antenna clearances are verified;
- solar tilt does not create interference;
- cable routes and service access are documented;
- and mechanical test plan is approved.

## Gate 3 — Electrical and Power Readiness

**Status:** Planned

### Deliverables

- final power schematic;
- solar-panel selection;
- MPPT selection;
- 12 V LiFePO4 selection;
- protected power distribution;
- regulator selection;
- fuse schedule;
- connector schedule;
- grounding strategy;
- and measured energy budget.

### Exit Criteria

- polarity and continuity tests pass;
- regulated outputs remain within tolerance;
- peak loads do not trigger brownout;
- charging is compatible with the battery;
- essential monitoring survives the defined low-power state;
- and runtime claims are supported by measurements.

## Gate 4 — Core Sensor Acquisition

**Status:** Planned

### Approved Sensors

- BNO085 IMU;
- water-pressure sensor;
- wind-speed sensor;
- wind-direction sensor;
- GPS module;
- battery monitor;
- solar monitor;
- internal-temperature sensor;
- and optional water-temperature sensor.

### Deliverables

- final part selections;
- wiring and pin assignments;
- modular sensor drivers;
- calibration procedures;
- sensor-health output;
- test fixtures;
- and acquisition logs.

### Exit Criteria

- each sensor initializes reliably;
- each sensor reports units and timestamps;
- disconnect and reconnect behavior is tested;
- invalid values are not converted to zero;
- calibration records exist;
- and reference comparisons meet approved tolerances.

## Gate 5 — UART and Mini-PC Integration

**Status:** Planned

### Deliverables

- UART electrical interface;
- frame format;
- message types;
- sequence numbers;
- checksum or CRC;
- reconnect logic;
- mini-PC ingestion service;
- validation service;
- and end-to-end communication tests.

### Exit Criteria

- valid messages are delivered consistently;
- corrupted messages are rejected;
- sequence gaps are detected;
- ESP32 acquisition continues during mini-PC restart;
- mini-PC reconnects automatically;
- and communication state is visible through `/status`.

## Gate 6 — Wave-Height Estimation

**Status:** Planned

### Deliverables

- pressure calibration;
- sensor-depth documentation;
- synchronized pressure and IMU samples;
- baseline-removal method;
- wave-feature extraction;
- documented wave-height definition;
- reference measurement method;
- and estimator validation report.

### Exit Criteria

- current wave height is traceable to raw measurements;
- the reported wave-height definition is unambiguous;
- quality state is exposed;
- invalid inputs produce unavailable status;
- and controlled-test error is documented.

## Gate 7 — Focused AI Development

**Status:** Presentation Prototype Implemented; Physical Model Planned

### Deliverables

- time-ordered dataset;
- persistence baseline;
- documented feature set;
- one selected operational prediction model;
- 5-minute evaluation;
- 15-minute evaluation;
- confidence/quality definition;
- Calm/Moderate/Rough classification logic;
- model artifact and version;
- and evaluation report.

### Exit Criteria

- physical-data training/test boundaries are documented;
- the selected model is compared with a baseline;
- MAE and bias are reported per horizon;
- missing and stale inputs are tested;
- classification thresholds are approved;
- prediction latency is acceptable;
- and no unrelated AI outputs are present.

## Gate 8 — REST API Migration

**Status:** Planned Migration

### Approved Contract

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

### Deliverables

- schemas;
- error codes;
- endpoint tests;
- legacy route compatibility plan;
- dashboard migration;
- and API documentation examples.

### Exit Criteria

- all eight routes meet the approved schemas;
- unavailable values remain distinct from zero;
- timestamps and units are explicit;
- mutating operations use POST;
- and legacy `/api/...` routes are removed or clearly deprecated.

## Gate 9 — Dashboard Simplification

**Status:** In Progress

### Required Areas

- Home;
- System Status;
- Motion;
- GPS;
- Power and Solar;
- Internal Temperature;
- Alerts;
- Settings;
- Wave History;
- Prediction History;
- and System Logs.

### Required Home Information

- system status;
- current wave height;
- predicted wave height;
- sea condition;
- prediction confidence;
- wind speed;
- wind direction;
- GPS;
- battery;
- solar;
- internal temperature;
- and active alerts.

### Exit Criteria

- unrelated sensor and prediction cards are removed;
- 30-minute prediction is removed from Phase 1 UI;
- current and predicted values are visually distinct;
- simulated and live data are labeled;
- mobile, tablet, and desktop layouts pass;
- light and dark modes pass;
- alerts remain readable in both themes;
- and typography is suitable for projection.

## Gate 10 — Integrated Bench Validation

**Status:** Planned

### Test Categories

- mechanical;
- electrical;
- sensors;
- AI;
- dashboard;
- and communication.

### Exit Criteria

- approved test cases have recorded results;
- critical faults are resolved;
- calibration metadata is archived;
- the system survives planned disconnect tests;
- prediction records retain later actual values;
- and a readiness review approves controlled deployment.

## Gate 11 — Controlled Coastal Deployment

**Status:** Planned

### Deliverables

- deployment approval;
- site record;
- weather and sea context record;
- deployment coordinates;
- monitoring dataset;
- prediction dataset;
- recovery inspection;
- maintenance record;
- and field-test report.

### Exit Criteria

- buoy remains mechanically stable for the approved test duration;
- no unacceptable water ingress occurs;
- sensor availability is documented;
- UART and dashboard availability are documented;
- power performance is measured;
- wave estimates are compared with a reference;
- 5-minute and 15-minute predictions are evaluated;
- and limitations are stated honestly.

## Gate 12 — Research Presentation and Phase 1 Closeout

**Status:** Planned

### Deliverables

- working prototype demonstration;
- focused research manuscript;
- architecture diagram;
- mechanical model and drawings;
- hardware and wiring documentation;
- source code;
- calibration evidence;
- test evidence;
- AI evaluation;
- dashboard demonstration;
- and final limitations/future-work statement.

### Exit Criteria

- claims match evidence;
- simulator and physical results are separated;
- AI scope remains focused;
- source and documentation versions are recorded;
- and adviser review is complete.

## Future Expansion Roadmap

Future Expansion begins only after Phase 1 closeout.

Possible later work includes:

- pH, salinity, turbidity, and dissolved-oxygen sensors;
- rain and UV sensors;
- hydrophone and current meter;
- cloud synchronization;
- LTE or LoRa;
- satellite communication;
- mobile application;
- multi-buoy networking;
- computer vision;
- additional AI models;
- maintenance prediction;
- and autonomous capabilities.

None of these are Phase 1 exit criteria.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 3.1 | 2026-08-05 | Added source-verified phase status. |
| 4.0 | 2026-08-09 | Replaced broad multi-platform roadmap with focused documentation, sensing, wave, AI, dashboard, API, and validation gates. |
