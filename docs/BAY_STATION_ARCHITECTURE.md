# Shore-Based Bay Station Architecture v1.2

Authority: `PROJECT_CONTEXT.md` and `THESIS DOCUMENTATION/BayStation.docx`.

## Approved split

```text
Buoy sensors -> ESP32 acquisition/validation/security/buffer
             -> LoRa primary -> barangay-hall Bay Station gateway
             -> Bay Station mini PC
                -> ingestion + pressure processing + SQLite + alerts + AI
                -> REST API + local dashboard -> local authorized user
                -> SIM/4G/5G Internet backhaul
                   -> cloud upload -> authorized remote dashboard / alerts
```

## Buoy to barangay hall setup reference

![Project FALCON concept showing the offshore buoy, LoRa link, barangay-hall receiver, Bay Station computer, cellular backhaul and remote dashboard](../THESIS%20DOCUMENTATION/visuals/bayyy.png)

Figure: User-supplied setup reference, added September 11, 2026. The deployment arrangement is adopted as the project concept, not evidence of an installed or tested system. The original illustration is preserved unchanged. The corrections below take precedence over its embedded labels.

### How data moves through the setup

1. **Buoy sensing node.** Sensors connect to the ESP32 on the solar-and-battery-powered buoy. The controller acquires and checks readings, attaches timestamps and packet identifiers, and prepares compact telemetry. Pressure supplies the input for estimated wave height; wind supplies speed and direction. Supporting GPS, power and enclosure-health data accompany the main observations.
2. **LoRa link to shore.** A buoy radio sends telemetry to one receiving installation at the barangay hall. The receiver passes packets to the Bay Station computer using an interface that remains to be selected. LoRa carries sensor telemetry; it is not the buoy's Internet connection. The drawing's tower represents the receiving antenna installation, not a second offshore computing node.
3. **Local Bay Station processing.** The shore mini PC validates and stores incoming records, processes pressure data, runs the wave-prediction service, and serves the local dashboard and alerts. A development laptop currently substitutes for this computer. Local processing comes before cloud upload and does not depend on an Internet round trip.
4. **Internet and remote viewing.** A separately powered SIM-enabled 4G/5G modem or router at the Bay Station supplies Internet backhaul. The planned cloud service receives uploaded records and makes authorized remote viewing available on phones or computers. Cloud hosting, access control and the remote-access implementation still require selection and testing.

### Corrections and limits of the illustration

- **Pressure sensor:** replace the pictured Bar02 in the deployment specification with the provisional Holykell HPT604 Type A candidate. Exact range/order code, continuous-seawater suitability, 4–20 mA interface and calibration remain pending. The drawing is not an approved wiring diagram.
- **Motion sensing:** the pictured BNO085 is not required in the current Phase 1 scope. Dashboard heave and tilt are modeled from pressure-derived wave estimates, not measured IMU orientation.
- **Temperature:** the pictured optional water-temperature channel is a future extension, not the current required sensor list. Enclosure-temperature monitoring remains a separate supporting function.
- **Link distance:** the pictured approximately 1–5 km is a proposed test envelope, not a guaranteed range or completed radio test. The actual site, antenna placement, obstruction profile and selected radio configuration determine the validation plan.
- **Tower height:** the pictured 8–12 m is a concept reference only, not a construction instruction. Final height, siting, structural design, lightning protection and installation permissions require a qualified site review.
- **Connectivity claims:** “works well” and “less affected by congestion” in the illustration are not measured project results. Packet delivery, delay, interference and recovery must be tested at the chosen site.
- **Power boundary:** the buoy solar system powers the buoy only. The Bay Station computer, receiver and cellular router use shore power with any backup supply sized separately.

### Expected behavior during interruptions

The intended design buffers buoy telemetry during LoRa loss and marks the shore display stale rather than live. During a Bay Station Internet outage, local reception, processing, storage and dashboard operation should continue; remote viewers must see the last-update time. Recovery, replay and duplicate prevention remain implementation and validation requirements, not demonstrated endurance results.

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
