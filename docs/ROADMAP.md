# Project FALCON Adviser-Revised Roadmap v9.0

## Gate 1 — Scope and component freeze

- approve exact models/datasheets for the pressure and wind sensors plus only the supporting telemetry interfaces;
- remove BNO085 and load-cell requirements from purchasing/fabrication;
- approve pressure-based estimated-wave wording, passive mooring, single-tube geometry, event-driven Wi-Fi/LTE cloud link, reduced battery, optional wave-prediction scope, and dashboard scope.

## Gate 2 — Electrical and bench integration

- revise schematic/PCB/wiring against purchased modules;
- verify rails, protection, addresses, logic levels, connectors, and test points;
- integrate the approved pressure transmitter and movement sensor first, then add only the supporting GPS, power, wind, and security telemetry required for operation.

## Gate 3 — Calibration and software integration

- record pressure baseline/depth/reference method and coefficients;
- calibrate pressure-derived wave output and wind channels;
- validate serial ingestion, grouped API, storage, stale state, security persistence, and automatic restart.
- validate event-driven LTE/cloud ingestion, remote-access controls, data usage, and outage recovery.

## Gate 4 — Controlled validation

- compare estimated wave height against a documented reference;
- measure MAE/RMSE/bias/repeatability;
- test geofence and tamper false positives/negatives under wave-like motion;
- validate power budget, waterproofing, corrosion controls, dashboard usability, and recovery.

## Gate 5 — Controlled coastal trial and thesis results

- obtain permissions and follow deployment/retrieval safety limits;
- collect traceable live data and document failures;
- update results, conclusions, BOM, drawings, and limitations from evidence;
- evaluate the implemented AI wave-prediction baseline against calibrated field data and report MAE/RMSE/bias before making accuracy claims.
