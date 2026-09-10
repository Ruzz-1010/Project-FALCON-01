# Project FALCON Adviser-Revised Roadmap v8.0

## Gate 1 — Scope and component freeze

- approve exact models/datasheets for the pressure and wind sensors plus only the supporting telemetry interfaces;
- remove BNO085 and load-cell requirements from purchasing/fabrication;
- approve pressure-based estimated-wave wording, passive mooring, LoRa buoy-to-barangay-hall link, Bay Station SIM/4G/5G backhaul, required wave-prediction scope, and four-page dashboard.

## Gate 2 — Electrical and bench integration

- revise schematic/PCB/wiring against purchased modules;
- verify rails, protection, addresses, logic levels, connectors, and test points;
- obtain and verify the exact HPT604 configuration, redesign and test its 4–20 mA receiver, then integrate wind speed/direction and only the supporting GPS, power, and security telemetry required for operation; retain Bar02 only for short bench comparisons.

## Gate 3 — Calibration and software integration

- record pressure baseline/depth/reference method and coefficients;
- calibrate pressure-derived wave output and wind channels;
- validate serial ingestion, grouped API, storage, stale state, security persistence, and automatic restart.
- validate LoRa gateway ingestion, Bay Station Internet/cloud synchronization, remote-access controls, and outage recovery.

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
