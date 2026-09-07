# Bay Station and Cellular Selection Register

Status: required adviser/fabrication gate. `TBD` means not purchased or approved; it must not be presented as installed.

| Item | Required decision/evidence | Current state |
| --- | --- | --- |
| Shore mini PC | Exact make/model, RAM/storage, OS, ports, cooling, measured service load, supplier, price | TBD; development laptop substitute |
| LTE modem | Exact module/board, Philippine bands, carrier certification, interface, supply, peak current, antenna connector | TBD |
| LoRa fallback | Buoy radio, shore gateway/receiver, legal band/region, antenna height, range, power, enclosure, and packet protocol | Optional fallback; exact module and gateway TBD |
| SIM/provider | Site survey for at least two networks, signal/availability, data plan, recurring cost | TBD |
| Transport | HTTPS or MQTT over TLS, endpoint/port, payload limit, acknowledgement behavior | TBD |
| Device identity | Per-buoy ID, credential provisioning, rotation/revocation, no secrets in repository | TBD |
| Packet identity | Monotonic sequence/UUID plus original sample timestamp for deduplication | TBD |
| ESP32 buffer | Storage medium, record count/time capacity, overwrite rule, integrity and wear behavior | TBD |
| Retry policy | Backoff, reconnect, acknowledgement, retransmission order, duplicate handling | TBD |
| Link priority | LTE first; LoRa only when LTE is unavailable and the shore gateway is reachable; buffer if both fail | TBD; must be implemented and tested |
| Bay Station network | Institutional host/site, LAN/remote access, firewall, TLS certificate, backup/export | TBD |
| Bay Station power | Facility outlet, UPS requirement/runtime, safe shutdown and automatic restart | TBD |

## Required acceptance tests

1. Coverage survey at the proposed deployment location and Bay Station path.
2. Repeated modem registration/transmission peak-current and brownout test.
3. Packet-loss, latency, reconnect-time, and data-usage measurement.
4. LoRa range, line-of-sight, obstruction, packet-loss, latency, and gateway-recovery measurement.
5. Controlled LTE/LoRa disconnect and failover with timestamp-preserving buffered upload.
6. Duplicate prevention after repeated acknowledgement loss/retransmission.
7. Credential rejection, authorization, TLS, and exposed-port review.
8. Bay Station reboot/service recovery, storage retention, export, and UPS test where applicable.

Do not release the LTE/LoRa schematics, PCB footprints, antenna placement, power branches, enclosure feedthroughs, final BOM, or unattended deployment until this register is complete.
