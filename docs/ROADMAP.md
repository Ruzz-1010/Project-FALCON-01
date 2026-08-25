# Project FALCON Adviser-Revised Roadmap v6.0

## Gate 1 — Scope and component freeze

- approve exact models/datasheets for all TBD sensors and security inputs;
- remove BNO085 and load-cell requirements from purchasing/fabrication;
- approve pressure-based estimated-wave wording, passive mooring, optional AI, and four-page dashboard.

## Gate 2 — Electrical and bench integration

- revise schematic/PCB/wiring against purchased modules;
- verify rails, protection, addresses, logic levels, connectors, and test points;
- integrate Bar02, GPS, wind, DS18B20, conductivity, power/health, tamper, enclosure switch, and buzzer one at a time.

## Gate 3 — Calibration and software integration

- record pressure baseline/depth/reference method and coefficients;
- calibrate water temperature, conductivity indicator, wind, and power channels;
- validate serial ingestion, grouped API, storage, stale state, security persistence, and automatic restart.

## Gate 4 — Controlled validation

- compare estimated wave height against a documented reference;
- measure MAE/RMSE/bias/repeatability;
- test geofence and tamper false positives/negatives under wave-like motion;
- validate power budget, waterproofing, corrosion controls, dashboard usability, and recovery.

## Gate 5 — Controlled coastal trial and thesis results

- obtain permissions and follow deployment/retrieval safety limits;
- collect traceable live data and document failures;
- update results, conclusions, BOM, drawings, and limitations from evidence;
- evaluate optional AI only if calibrated data and schedule permit.
