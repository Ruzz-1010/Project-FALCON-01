# Event Driven Cloud Buoy Selection Register


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Status: required adviser, supplier, and site-validation gate. `TBD` means not purchased or approved; it must not be presented as installed.

| Item | Required decision/evidence | Current state |
| --- | --- | --- |
| Pressure channel | Exact range, output, wetted materials, cable sealing, saltwater suitability, calibration certificate, supplier, price | Required; 4–20 mA preferred, 0–5 V/0–10 V/RS485 alternatives under review |
| Movement channel | MPU6050 or equivalent, mounting, sample rate, threshold and calibration method | Required for event detection; exact part TBD |
| Optional wind channel | Speed/direction sensor, range, output, reference instrument, price | Retain only if adviser confirms it remains in Phase 1 |
| Optional position channel | GPS module, fix quality, geofence radius, persistence, data-privacy controls | Supporting telemetry; exact part TBD |
| Cellular Internet | 4G/LTE modem, supported bands, antenna, regulator, SIM/data plan, coverage and recurring cost | Required for remote field path; exact module/provider TBD |
| Bench Internet | Wi-Fi access point and credentials | Approved laboratory path |
| Cloud endpoint | Provider, API or MQTT broker, storage, retention, dashboard URL, cost, backup | TBD |
| Transport | HTTPS or MQTT over TLS, payload limit, acknowledgement behavior | TBD |
| Device identity | Per-buoy ID, credential provisioning, rotation/revocation, no secrets in repository | TBD |
| Packet identity | Monotonic sequence/UUID plus original sample timestamp for deduplication | Required design |
| ESP32 buffer | Flash or microSD, record count/time capacity, overwrite rule, integrity and wear behavior | TBD |
| Retry policy | Backoff, reconnect, acknowledgement, retransmission order, duplicate handling | TBD |
| Event policy | Summary interval, anomaly thresholds, debounce/persistence, heartbeat interval | 1–5 minute summaries; immediate events; thresholds TBD from baseline |
| Power branch | Modem peak current, converter, battery, solar, fuse, wiring, measured daily Wh | Small battery candidate; measured load required |
| Mechanical package | Single tube, small buoyancy collar, dry electronics enclosure, cable glands, retrieval and mooring | Redesign in progress |

## Required acceptance tests

1. Bench Wi-Fi upload and cloud authentication.
2. LTE coverage, registration, data-usage, reconnect, and modem peak-current measurement at the proposed deployment site.
3. Pressure and movement baseline capture used to tune event thresholds.
4. Summary interval, immediate-event latency, sequence/duplicate prevention, and timestamp preservation.
5. Controlled Internet disconnect with local buffering and queued synchronization.
6. Cloud restart/API outage behavior, stale-data marking, storage retention, export, and dashboard freshness.
7. Credential rejection, TLS, least-privilege access, and exposed-port review.
8. Battery/regulator test during modem registration and transmission peaks.
9. Waterproofing, cable strain relief, condensation, corrosion, retrieval, and compact can-buoy buoyancy/stability review.

Do not release the final pressure interface, LTE power branch, cloud endpoint, enclosure feedthroughs, or unattended deployment until this register is complete.
