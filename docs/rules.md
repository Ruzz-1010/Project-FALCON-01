# Project FALCON-01 — Rules

These rules are non-negotiable for code, documentation, hardware work, and thesis claims. Updated 2026-11-07.

## 1. Truthfulness

- Never describe simulated, planned, or bench-tested hardware as field-deployed,
  installed, calibrated, or production-ready.
- Pressure is measured. Wave height is **estimated** and must show
  `CALIBRATION REQUIRED` until a reference calibration exists.
- AI output is a **15-minute research estimate**. It is not an official marine
  forecast, warning, or measured value.
- Never fabricate sensor values, test results, accuracy figures, or deployment
  dates.
- Every displayed value must carry its state: `LIVE`, `SIMULATED`, `ESTIMATED`,
  `CALIBRATION REQUIRED`, `STALE`, `OFFLINE`, `COLLECTING`, `MODEL OUTPUT`.
- Distinguish measured, estimated, predicted, and scenario data in both UI and
  prose.

## 2. Approved scope

Required core: water pressure, wind speed/direction, GPS position/security,
battery + solar, internet communication, ESP32 controller.

Current pressure baseline: 24 V two-wire 4–20 mA transmitter, precision shunt,
ADS1115, and ESP32. Current power baseline: 12.8 V 8 Ah LiFePO4. The six-panel
3S2P solar array remains proposed until actual panel/controller ratings match.

Excluded from the Phase 1 scope: water temperature, salinity, conductivity, and
other environmental channels. Legacy API fields may remain for compatibility but
must not be presented as required measurements.

Do not reintroduce BNO085, load cells, tall towers, large outriggers, a buoy-side
mini PC, or LoRa as the primary link unless the baseline is formally revised.

## 3. Event-driven telemetry

- Sample locally; do not upload per wave.
- Send a summary every 1–5 minutes during normal operation.
- Send an immediate packet only on a validated threshold event: pressure/wind
  excursion, GPS displacement, tamper, low battery, sensor fault, or recovery.
- Debounce and persist events before transmitting.
- Buffer records during outages and preserve original timestamps.
- Every threshold must be documented and testable.

## 4. Hardware and safety

- Keep the center of gravity low; ballast and battery placement must be
  documented.
- Fix the pressure sensor relative to the seabed or an independent mooring
  reference. Do not hang it at constant distance below the heaving buoy.
- Keep it clear of the seabed at low tide and provide strain relief, impact/debris protection, and retrieval.
- Treat 5 m as measurement span, not required suspension depth or proof of maximum site depth.
- Never connect 24 V to ADS1115/ESP32. Verify shunt voltage, ADC range,
  protection, grounding, and tolerances.
- Fuse and bench-test the battery/boost/loop continuously before 24/7 claims.
- Verify rail voltages, logic levels, polarity, fusing, and waterproofing before
  power-on.
- Use only approved sensor interfaces and document any substitution.
- Field deployment requires permissions, a retrieval plan, and a documented
  maximum sea state.
- Do not claim waterproofing or corrosion resistance without a test record.

## 5. Pressure and wave processing

- `ΔP/(ρg)` is an initial hydrostatic conversion, not the complete irregular-wave method.
- Correct frequency-dependent pressure attenuation using measured sensor/water depth and stated assumptions.
- Reject bins below validated pressure-response/SNR limits instead of amplifying noise.
- A proposed 4 Hz rate has a 2 Hz Nyquist limit; usable bandwidth must also pass transmitter tests.
- Validate against an independent reference and report MAE, RMSE, mean bias, sample count, conditions, and limitations.

## 6. Software conventions

### Edge service (Python)

- Python 3.11+; standard library unless a dependency is justified.
- Keep acquisition, validation, storage, rules, and prediction separated by
  module.
- SQLite migrations must be additive and non-destructive.
- Reject invalid or out-of-range channels before storage.
- Preserve session breaks; never connect samples across a long outage.
- `/status`, `/wave`, `/gps`, `/battery`, `/solar`, `/ai`, and `/logs` contracts
  are consumed by the dashboard; change them deliberately.

### Dashboard (TypeScript / React)

- `dashboard-next/` is the only full dashboard; the ESP32 serves setup and
  diagnostics only.
- Keep data acquisition, estimation, and prediction logic out of components.
- Preserve explicit loading, empty, stale, offline, and unavailable states.
- Charts must distinguish measured and estimated/predicted series by both color
  and label. Do not rely on color alone.
- No decorative animation that hides data; respect reduced motion.
- Keyboard access and readable contrast are required.
- The measured series must remain visually dominant over any forecast tail.

### Prediction and public access

- The thesis target is a current AI-assisted 15-minute model, not a future-only feature.
- Use chronological train/validation/held-out test periods and compare with persistence and damped-trend baselines.
- Current deterministic prediction code is a baseline/demo until ML training and held-out results exist.
- Prediction failure must not block acquisition, storage, alerts, or current readings.
- `public-dashboard/` stays read-only, Palawan-limited, simplified, and explicitly simulated until physical endpoints exist.
- Do not expose maintenance controls, raw logs, protected coordinates, or security details publicly.

## 7. Validation gates

Run the narrowest relevant check after every change.

```bash
# Backend
PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v

# Dashboard
cd dashboard-next && npm run build

# Public dashboard
cd public-dashboard && npm run build

# Patch hygiene
git diff --check
```

- Dashboard changes require a production build; the service serves the build,
  not the source.
- Thesis/DOCX changes require compiling the updater and inspecting the generated
  text.
- A change is not "done" until the relevant check passes and the UI was looked
  at, not just compiled.
- Do not mark hardware validation complete without a dated test record.

## 8. Documentation

- Keep the active docs set to `prd.md`, `architecture.md`, `rules.md`,
  `design.md`, `task.md`, and `memory.md`.
- Historical material lives in `docs-archive/` and is reference only.
- Do not duplicate the same specification across files; link instead.
- Update `task.md` when scope or status changes.
- Record irreversible decisions in `memory.md`.
- Write in plain language; define acronyms on first use.
- Ask which DOCX is authoritative before editing.
- Keep `selected`, `proposed`, `purchased`, `simulated`, and `validated` distinct.

## 9. Git and backups

- Preserve unrelated user work in the working tree.
- Commit only files that belong to the requested change.
- Never commit secrets, API keys, SIM details, private certificates, local
  databases, telemetry dumps, browser profiles, or generated preview images.
- Do not commit `node_modules/`, build caches, or temporary files.
- Run `git diff --check` before committing.
- If the repository is mid-rebase or detached, stop and resolve that state
  before committing new work.
