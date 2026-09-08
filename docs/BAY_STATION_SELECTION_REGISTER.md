# Bay Station LoRa and Internet Selection Register

Status: required adviser/fabrication gate. `TBD` means not purchased or approved; it must not be presented as installed.

| Item | Required decision/evidence | Current state |
| --- | --- | --- |
| Shore mini PC | Exact make/model, RAM/storage, OS, ports, cooling, measured service load, supplier, price | TBD; development laptop substitute |
| LoRa primary link | Buoy radio, barangay-hall gateway/receiver, legal band/region, antenna height, range, power, enclosure, and packet protocol | Required target path; exact module and gateway TBD |
| SIM/4G/5G Bay Station backhaul | Bay Station modem/router, site coverage, provider, data plan, recurring cost, antenna and failover | Required Internet backhaul; exact equipment/provider TBD |
| Transport | HTTPS or MQTT over TLS, endpoint/port, payload limit, acknowledgement behavior | TBD |
| Device identity | Per-buoy ID, credential provisioning, rotation/revocation, no secrets in repository | TBD |
| Packet identity | Monotonic sequence/UUID plus original sample timestamp for deduplication | TBD |
| ESP32 buffer | Storage medium, record count/time capacity, overwrite rule, integrity and wear behavior | TBD |
| Retry policy | Backoff, reconnect, acknowledgement, retransmission order, duplicate handling | TBD |
| Link priority | LoRa from buoy to barangay-hall gateway; Bay Station uses SIM/4G/5G for cloud/remote access; buffer if LoRa fails | TBD; must be implemented and tested |
| Bay Station network | Barangay-hall host/site, local LAN, cloud/remote access, firewall, TLS certificate, backup/export | TBD |
| Bay Station power | Facility outlet, UPS requirement/runtime, safe shutdown and automatic restart | TBD |

## Required acceptance tests

1. LoRa coverage survey between the proposed deployment location and barangay hall.
2. LoRa range, line-of-sight, obstruction, packet-loss, latency, and gateway-recovery measurement.
3. SIM/4G/5G Bay Station coverage, registration, data-usage, reconnect, and backhaul measurement.
4. Packet-loss, latency, reconnect-time, and timestamp-preserving upload measurement for both hops.
5. Controlled LoRa disconnect and Bay Station Internet disconnect with local buffering and later cloud synchronization.
6. Duplicate prevention after repeated acknowledgement loss/retransmission.
7. Credential rejection, authorization, TLS, and exposed-port review.
8. Bay Station reboot/service recovery, storage retention, export, and UPS test where applicable.

Do not release the LoRa/Bay Station Internet schematics, PCB footprints, antenna placement, power branches, enclosure feedthroughs, final BOM, or unattended deployment until this register is complete.
