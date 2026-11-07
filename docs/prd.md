# Project FALCON-01 — Product Requirements

| Field | Value |
| --- | --- |
| Product | FALCON-01 near-shore coastal observation buoy |
| Type | Undergraduate Phase 1 capstone prototype |
| Revision | 2026-11-07 |
| Status | Software demo exists; hardware, calibration, ML, and field validation pending |
| Controller | ESP32 |

## 1. Problem and contribution

Coastal observers, researchers, students, and selected public users need understandable local sea-condition information, while commercial systems can be expensive and difficult to maintain. FALCON integrates a serviceable buoy, truthful pressure-derived wave estimates, contextual sensing, resilient telemetry, and clear interfaces. Its contribution is integration and evaluation; it does not invent the sensors or claim official marine forecasting.

## 2. Target users

| User | Access and benefit |
| --- | --- |
| Operator/maintainer | Detailed live state, quality, power, GPS/security, alerts, logs, and diagnostics |
| Researcher/student | Historical records, calibration evidence, model evaluation, and exports |
| Approved public viewer | Read-only Palawan station map with simplified wave/wind condition and update status |
| Adviser/panel | Traceable requirements, methods, limitations, and evidence |

## 3. Scope

### In scope

- ESP32 acquisition of a 24 V two-wire 4–20 mA pressure transmitter through a shunt and ADS1115.
- Pressure-derived wave height with calibration, sensor-depth correction, filtering/noise control, and reference validation.
- Wind speed/direction, GNSS position/time/drift/geofence, battery/solar, enclosure health, and communication status.
- 12.8 V 8 Ah LiFePO4 system, proposed six-panel 3S2P solar array, charge controller, protection, and 24 V boost stage, subject to electrical validation.
- Local buffering, routine summaries, event packets, outage recovery, edge/cloud storage, and alerts.
- Operator dashboard plus separate read-only public Palawan map.
- Python-based AI-assisted 15-minute wave-height prediction evaluated on chronological held-out data against persistence and damped-trend baselines.
- Bench, controlled-water, and limited supervised near-shore evaluation.

### Out of scope

- Official PAGASA forecast, navigation control, emergency/disaster-warning authority, or safety certification.
- Guaranteed deep-water/open-ocean operation or permanent unattended deployment.
- Water temperature, salinity, conductivity, and unrelated environmental channels as core objectives.
- Continuous cloud upload of every 4 Hz raw pressure sample.
- Production-grade multi-tenant authentication, OTA, or hardened cloud security.
- Claims of accuracy, waterproofing, corrosion resistance, autonomy, or ML skill before testing.

## 4. Functional requirements

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| FR-01 | Acquire timestamped 4–20 mA pressure through shunt/ADS1115 | Calibrated ADC/current/pressure table and fault detection |
| FR-02 | Produce a depth-corrected pressure-derived wave estimate | Method metadata, quality state, and comparison with reference |
| FR-03 | Acquire wind speed/direction | Timestamped observations and reference comparison when available |
| FR-04 | Report GNSS position, time, drift, and geofence | Fix, satellites/quality, anchor distance, state |
| FR-05 | Report battery, solar, and charging state | Measured voltage/current/power and status |
| FR-06 | Buffer data and recover after loss of Internet | Original timestamps retained; no duplicate replay |
| FR-07 | Send routine summaries and debounced events | Logged packet delivery, latency, and event evidence |
| FR-08 | Store telemetry, alerts, predictions, and events | SQLite persistence and additive migration tests |
| FR-09 | Serve an operator dashboard | Detailed state and explicit truth labels |
| FR-10 | Serve a public Palawan map | Read-only station summaries; no maintenance/security data |
| FR-11 | Generate a 15-minute AI-assisted estimate | Model output/status and held-out evaluation versus baselines |
| FR-12 | Continue current sensing when AI/dashboard/Internet fails | Acquisition and buffering remain operational |

## 5. Quality and truth requirements

- Every value carries source, unit, timestamp, and state.
- Measured pressure, estimated wave height, simulated data, and predicted values are never conflated.
- The system reports `UNAVAILABLE` instead of extrapolating beyond validated sensor response or poor signal quality.
- UI works from phone to desktop, supports keyboard use, and preserves readable contrast.
- Hardware remains serviceable, fused, protected, strain-relieved, and recoverable.
- Power sizing uses measured current and solar results.

## 6. Evaluation

| Area | Required evidence |
| --- | --- |
| Pressure/wave | Calibration curve; depth/SNR correction; MAE, RMSE, mean bias versus reference |
| Sampling | Stable 4 Hz timestamps, usable band, noise/spike handling, transmitter response verification |
| Communication | Packet delivery ratio, latency, duplicates, outage recovery |
| Power | Load current, boost efficiency, battery runtime, charging behavior, daily solar energy |
| GPS/security | Position error, drift/geofence behavior, false events |
| AI | Chronological held-out MAE/RMSE/bias and comparison with persistence/damped trend |
| Usability | Defined operator/public tasks completed without assistance |

## 7. Constraints and assumptions

- The pressure sensor is fixed to a seabed/mooring reference, with site-specific depth/tide clearance.
- The reported 5 m transmitter range, 24 V supply, and SS316 construction require datasheet/bench confirmation.
- The 3S2P array is provisional until individual panel and controller ratings are known.
- Wi-Fi is for bench use; LTE is proposed for field use.
- Four public-map stations are simulated/test locations until physical buoys exist.
- The current deterministic forecast is a baseline/demo; the ML model still requires implementation and evaluation.

## 8. Success condition

FALCON succeeds when it produces traceable, calibrated pressure-derived estimates under a limited approved test plan; preserves and communicates data reliably; operates within a measured power budget; presents honest states to operators/public viewers; and evaluates the 15-minute model without claiming official forecast authority.
