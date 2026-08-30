# FALCON Buoy Power System — Bay Station Baseline v2.0

The buoy and shore Bay Station are separate power domains. No mini PC is installed on the buoy.

## Buoy power path

```text
Solar panel -> LiFePO4-compatible MPPT -> 12.8 V LiFePO4 battery
             -> fused disconnect/distribution -> protected regulated rails
             -> ESP32 + sensors + LTE modem + security electronics
```

The provisional starting point is a 12.8 V 20 Ah LiFePO4 battery (256 Wh nominal), an 80% usable-energy planning limit (204.8 Wh), and either a 40 W or 60 W solar candidate. These are design assumptions—not validated endurance claims.

| Complete measured average buoy load | Daily energy | Approximate no-solar runtime from 204.8 Wh |
| ---: | ---: | ---: |
| 2 W | 48 Wh/day | 102.4 h |
| 4 W | 96 Wh/day | 51.2 h |
| 6 W | 144 Wh/day | 34.1 h |

Preliminary solar harvest uses `panel rating × 4 peak-sun-hours × 70% net efficiency`:

| Candidate | Planning harvest | Status |
| --- | ---: | --- |
| 40 W | 112 Wh/day | Accept only if measured load and modem peaks retain margin |
| 60 W | 168 Wh/day | Preferred prototype starting candidate pending measurements |

## Required measurements before release

- 24-hour current log covering sampling, idle, security, network registration, reconnect, and LTE transmit peaks.
- Converter efficiency, ripple, temperature, voltage drop, and brownout behavior.
- Battery BMS/charge limits and MPPT compatibility with panel Voc/Isc.
- Fuse, wire, connector, disconnect, reverse-polarity, and transient-protection ratings.
- Minimum 72-hour supervised solar-endurance trial.

## Bay Station power

The shore mini PC uses facility power or a separately engineered UPS. Measure its startup, idle, storage, dashboard, and AI loads separately. Never include Bay Station energy in the buoy battery/solar calculation.

Final panel, MPPT, battery, converter, fuse, and wire selections remain `TBD` until the LTE modem and all installed buoy loads are frozen and bench measured.
