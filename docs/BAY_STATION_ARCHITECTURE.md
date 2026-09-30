# Shore-Based Bay Station Architecture v1.1

Authority: `PROJECT_CONTEXT.md` and `THESIS DOCUMENTATION/BayStation.docx`.

## Approved split

```text
Buoy sensors -> ESP32 acquisition/validation/security/buffer
             -> LoRa primary -> barangay-hall Bay Station gateway
             -> Bay Station mini PC -> SIM/4G/5G Internet backhaul
             -> cloud upload / authorized remote access
             -> ingestion + pressure processing + SQLite + alerts + AI
             -> REST API + four-page dashboard -> local/cloud authorized user
```

No Orange Pi, Raspberry Pi, mini PC, SIM/4G/5G Internet modem, database, or AI runtime is installed or powered on the buoy. The development laptop currently substitutes for the final barangay-hall Bay Station mini PC.

## Buoy responsibilities

- Acquire timestamped pressure, GPS, wind, power, health, and security signals.
- Validate units/ranges and report invalid, stale, or disconnected channels explicitly.
- Run local geofence/tamper/enclosure debounce and buzzer rules.
- Frame versioned telemetry with a unique packet identifier.
- Transmit compact telemetry over LoRa to the verified barangay-hall gateway.
- Buffer a defined number/duration of packets during LoRa outages.
- Reconnect and retransmit buffered packets without changing original timestamps.

## Bay Station responsibilities

- Authenticate and validate received LoRa telemetry and prevent duplicate insertion.
- Retain original and derived records in SQLite.
- Filter pressure, apply the approved baseline/calibration, and estimate wave height.
- Run required short-term AI prediction and its non-AI comparison baseline.
- Serve the local REST API, four-page dashboard, logs, alerts, and exports.
- Use the SIM/4G/5G Internet backhaul for cloud upload and authorized remote access.
- Mark stale/offline/model-unavailable states instead of fabricating values.
- Restart services automatically and preserve received data where possible.

## Selection gates

The exact mini PC, LoRa module/gateway, antenna, regional band, transport protocol, device authentication, retry policy, packet identity, buffer capacity, Bay Station SIM/provider, cloud endpoint, remote-access method, firewall/TLS policy, and UPS requirement remain `TBD`. USB serial is the current bench transport only and is not the approved deployed communications path.

## Failure and power boundaries

- LoRa loss: sensing and local security continue and telemetry is buffered until the verified barangay-hall gateway is reachable again.
- Bay Station Internet loss: local ingestion, storage, dashboard, alerts, and AI continue; cloud upload and remote access resume after SIM/4G/5G connectivity returns.
- Stale or uncalibrated inputs: wave estimate/AI output is withheld or explicitly qualified.
- AI failure: acquisition, security, ingestion, storage, live display, and alerts continue.
- Buoy solar/battery power covers only ESP32, sensors, LoRa radio, security, and conversion losses.
- The shore Bay Station uses facility power or a separately engineered UPS and is excluded from buoy autonomy calculations.
