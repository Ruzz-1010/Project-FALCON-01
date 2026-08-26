# Sensor Specification v6.0

| Group | Channel | Output | Required truth label |
| --- | --- | --- | --- |
| Core | Bar02/compatible pressure | raw/filtered kPa, baseline, optional depth, estimated wave height | ESTIMATED; CALIBRATION REQUIRED until validated |
| Core | GPS | latitude, longitude, fix, satellites, geofence distance/state | LIVE or SIMULATED |
| Core | Wind speed | speed and units | LIVE or SIMULATED |
| Core | Wind direction | direction/heading | LIVE or SIMULATED |
| Supporting | Sealed DS18B20 | water temperature | LIVE or SIMULATED |
| Health | Battery monitor | voltage, current, state estimate | LIVE or SIMULATED |
| Health | Solar monitor | voltage, current, power/charging | LIVE or SIMULATED |
| Health | Enclosure temperature | temperature | LIVE or SIMULATED |
| Security | GPS geofence | SECURE/WARNING/ALERT/DISARMED | configured persistence required |
| Security | Tamper input | clear/detected | debounced/persistent |
| Security | Enclosure switch | closed/open | debounced |

BNO085 is deprecated as a required sensor. Load cell/HX711 mooring tension is removed. Exact TBD models cannot be added to BOM, pinout, or PCB as final selections without datasheet review. Every channel requires units, range, sampling target, wiring, calibration, invalid/stale behavior, timestamp, and physical test evidence.
