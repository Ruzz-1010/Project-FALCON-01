# Project FALCON-01 — Current Tasks

Status date: 2026-11-07. Software demonstrations exist; physical integration, calibration, ML evaluation, and field validation remain pending.

## Immediate priorities before defense

- [ ] Confirm the single authoritative thesis DOCX before editing.
- [ ] Remove claims that ML is only a future enhancement; define the AI-assisted 15-minute model as current scope.
- [ ] Correct Sections 2.1.1 and 2.6 for fixed sensor placement, depth attenuation, sampling noise, and reference validation.
- [ ] Make hardware tables consistent: 12.8 V 8 Ah battery; 24 V two-wire 4–20 mA 5 m-range transmitter; boost converter; shunt; ADS1115; fuse; controller; truthful status labels.
- [ ] Recheck every figure and caption against current architecture.
- [ ] Prepare defense answers for pressure placement, ADS1115, 4 Hz sampling, correction, AI, validation, power, users, and limitations.

## Hardware freeze and procurement

- [ ] Obtain the pressure-transmitter datasheet: supply range, span, accuracy, response time, overload, vent/reference type, and seawater compatibility.
- [ ] Select the precision shunt after checking ADS1115 supply/input limits; document endpoints and protection/filtering.
- [ ] Select and test a fused 12.8 V-to-24 V boost converter at continuous load and worst-case battery voltage.
- [ ] Verify the 12.8 V 8 Ah LiFePO4 BMS and usable capacity.
- [ ] Verify every panel's Vmp, Voc, Imp, Isc, and wattage; confirm 3S2P compatibility with the charge controller.
- [ ] Freeze wind, direction, GNSS, LTE, INA260/equivalent, controller, fuses, connectors, glands, and enclosure.
- [ ] Update schematic, BOM, wiring, and thesis only after exact models are confirmed.

## Pressure channel and wave validation

- [ ] Calibrate 4 mA and 20 mA endpoints plus intermediate points using a known water column/reference.
- [ ] Mount the transmitter to an independent seabed/mooring reference, not at constant distance below the buoy.
- [ ] Survey sensor elevation, depth, tidal range, and low-tide seabed clearance.
- [ ] Record 4 Hz bursts and verify the transmitter response bandwidth.
- [ ] Implement despiking, saturation checks, trend removal, windowing, band limits, pressure-response correction, and SNR rejection.
- [ ] Compare with an independent wave reference; report MAE, RMSE, and mean bias.
- [ ] Return `UNAVAILABLE` where correction is unreliable.

## Firmware and communication

- [ ] Implement ADS1115 acquisition and engineering-unit conversion.
- [ ] Integrate wind, GPS, battery/solar, enclosure, and communication health.
- [ ] Buffer UTC timestamps and quality flags locally.
- [ ] Upload summaries at the approved interval; do not upload every 4 Hz sample.
- [ ] Implement event debounce, outage replay, LTE reconnect, watchdog, and brownout recovery.

## AI-assisted 15-minute prediction

- [ ] Freeze features using validated wave history, trend/variability, and wind context.
- [ ] Freeze chronological train/validation/held-out test periods.
- [ ] Implement a justified Python ML regression model.
- [ ] Compare with persistence and damped linear-trend baselines.
- [ ] Report MAE, RMSE, mean bias, sample count, and failure cases.
- [ ] Show `COLLECTING`/`UNAVAILABLE` when input is inadequate.
- [ ] Align UI/API around a primary 15-minute horizon; current code supports 5/10/15-minute demos.

## Dashboards and service

- [x] Operator dashboard exists in `dashboard-next/`.
- [x] Edge service, SQLite, simulator, alerts, API, and hosting exist.
- [x] Public Palawan map exists with four test stations.
- [ ] Connect both dashboards to physical endpoints.
- [ ] Keep public data simplified/read-only; detailed controls remain operator-only.
- [ ] Harden stale/offline states, exports, clock changes, and long outages.
- [ ] Review at 1600, 1280, 780, 638, and 390 px after changes.

## Field validation

- [ ] Obtain permission, maximum sea state, supervision, and retrieval plan.
- [ ] Measure site depth and tidal range before final geometry.
- [ ] Run bench, controlled-water, then limited near-shore tests.
- [ ] Test drift/geofence, tamper, packet recovery, solar, runtime, ingress, and corrosion exposure.
- [ ] Preserve raw evidence and label every render/simulation.

## Definition of done

Implementation must exist, the narrow test must pass, output must be inspected, and documentation must match evidence. Planned or simulated behavior is never a test result.

## Repository warning

The working tree contains extensive user work and is detached or in an interrupted rebase. Do not reset, clean, rebase, commit, or push until this is deliberately resolved without losing work.
