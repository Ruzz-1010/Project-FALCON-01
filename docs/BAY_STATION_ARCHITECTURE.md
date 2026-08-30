# Shore-Based Bay Station Architecture v1.0

Authority: `PROJECT_CONTEXT.md` and `THESIS DOCUMENTATION/BayStation.docx`.

## Approved split

```text
Buoy sensors -> ESP32 acquisition/validation/security/buffer
             -> approved LTE/cellular modem -> mobile network/Internet
             -> shore Bay Station mini PC
             -> ingestion + pressure processing + SQLite + alerts + AI
             -> REST API + four-page dashboard -> authorized user
```

No Orange Pi, Raspberry Pi, mini PC, database, or AI runtime is installed or powered on the buoy. The development laptop currently substitutes for the final shore mini PC.

## Buoy responsibilities

- Acquire timestamped pressure, GPS, wind, water-temperature, power, health, and security signals.
- Validate units/ranges and report invalid, stale, or disconnected channels explicitly.
- Run local geofence/tamper/enclosure debounce and buzzer rules.
- Frame versioned telemetry with a unique packet identifier.
- Buffer a defined number/duration of packets during link outages.
- Reconnect and retransmit buffered packets without changing original timestamps.

## Bay Station responsibilities

- Authenticate and validate received telemetry and prevent duplicate insertion.
- Retain original and derived records in SQLite.
- Filter pressure, apply the approved baseline/calibration, and estimate wave height.
- Run required short-term AI prediction and its non-AI comparison baseline.
- Serve the REST API, four-page dashboard, logs, alerts, and exports.
- Mark stale/offline/model-unavailable states instead of fabricating values.
- Restart services automatically and preserve received data where possible.

## Selection gates

The exact mini PC, LTE modem, antenna, SIM/provider, transport protocol (for example HTTPS or MQTT over TLS), device authentication, retry policy, packet identifier, buffer capacity, cellular data budget, Bay Station network exposure, and UPS requirement remain `TBD`. USB serial is the current bench transport only and is not the approved deployed communications path.

## Failure and power boundaries

- Cellular or Bay Station loss: ESP32 sensing and local security continue; telemetry is buffered.
- Stale or uncalibrated inputs: wave estimate/AI output is withheld or explicitly qualified.
- AI failure: acquisition, security, ingestion, storage, live display, and alerts continue.
- Buoy solar/battery power covers only ESP32, sensors, LTE modem, security, and conversion losses.
- The shore Bay Station uses facility power or a separately engineered UPS and is excluded from buoy autonomy calculations.
