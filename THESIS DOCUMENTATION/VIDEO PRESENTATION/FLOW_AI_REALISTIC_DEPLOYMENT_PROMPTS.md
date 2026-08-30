# Project FALCON — Flow AI Deployment Prompt Status

> **REDESIGN HOLD — 27 August 2026:** Do not generate a final mechanical or
> deployment video from the old prototype image. The physical and visual
> prototype is under redesign. Exterior geometry, sensor placement, enclosure
> layout, solar arrangement, cooling geometry, dimensions, and waterline are
> TBD until adviser approval. Follow `docs/PROJECT_CONTEXT.md` v6.1 and
> `docs/PROTOTYPE_REDESIGN_BASELINE.md`.

## Approved system story

The presentation may describe this data path without inventing physical
placement:

`Pressure + GPS + wind speed + wind direction + supporting water temperature`
`→ ESP32 acquisition, validation, and buffering → LTE/cellular → shore Bay Station mini PC`
`→ SQLite/local processing → REST API → local dashboard`

Security monitoring includes persistent GPS geofence, a generic
vibration/tamper input, an enclosure reed or limit switch, and a buzzer. Power
and enclosure temperature are health channels. Pressure-derived wave height
must be labelled **ESTIMATED** and **CALIBRATION REQUIRED** until validated.
Simulated values must be labelled **SIMULATED**.

## Claims that must not appear

- No required BNO085/IMU or IMU-derived wave measurement.
- No required load cell, HX711, mooring-tension sensor, salinity sensor, or AI.
- No mandatory cloud dependency or official forecast claim.
- No fixed solar-panel count, cooling arrangement, enclosure layout, sensor
  position, dimensions, waterline, or final CAD until the redesign is approved.
- No reuse of old stabilizer-buoy geometry as the current prototype.

## Temporary non-mechanical Flow prompt

> Create a clean engineering data-flow animation for Project FALCON-01 without
> showing or inventing a final buoy body. Begin with labelled coastal inputs:
> water pressure, GPS, wind speed, wind direction, and supporting sealed water
> temperature. Animate signals entering an ESP32, being validated and
> timestamped, then traveling through a visible USB serial/UART link to an
> shore Bay Station mini PC. Show SQLite storage, pressure-derived
> estimated-wave processing, security and health alerts, a REST API, and a
> four-page local dashboard: Overview, Buoy Motion, Sensors, and Logs & Alerts.
> Label wave height ESTIMATED and CALIBRATION REQUIRED. Label all demonstration
> values SIMULATED. AI is an optional isolated future aid and must not block or
> replace the deterministic core. Documentary engineering style, 16:9, clear
> arrows and readable labels, no fictional hardware placement, no cloud shown
> as required, and no exterior prototype geometry.

After the replacement prototype is approved, create a new scene package using
only verified CAD screenshots and the approved component-placement register.
