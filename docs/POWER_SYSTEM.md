# FALCON Buoy Power System — Event Driven Cloud Baseline v3.0


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

The buoy and cloud/development computer are separate power domains. No mini PC or LoRa gateway is installed on the buoy.

## Buoy power path

```text
Solar panel -> LiFePO4-compatible MPPT -> 12.8 V LiFePO4 battery
             -> fused disconnect/distribution -> protected regulated rails
             -> ESP32 + sensors + LTE modem/Wi-Fi + security electronics
```

The reduced-prototype starting point is a 12.8 V 6–10 Ah LiFePO4 battery (76.8–128 Wh nominal), an 80% usable-energy planning limit, and a 10–20 W solar candidate. These are design assumptions—not validated endurance claims.

| Complete measured average buoy load | Daily energy | Approximate no-solar runtime from 80 Wh usable |
| ---: | ---: | ---: |
| 2 W | 48 Wh/day | 102.4 h |
| 4 W | 96 Wh/day | 51.2 h |
| 6 W | 144 Wh/day | 34.1 h |

Preliminary solar harvest uses `panel rating × 4 peak-sun-hours × 70% net efficiency`:

| Candidate | Planning harvest | Status |
| --- | ---: | --- |
| 10 W | 28 Wh/day | Accept only if measured load and modem peaks retain margin |
| 20 W | 56 Wh/day | Preferred low-cost prototype candidate pending measurements |

At the 1.5 W event-driven planning load, the 10 W candidate leaves limited
recovery margin while the 20 W candidate provides a larger nominal margin.
Panel Voc/Isc, charger compatibility, mounting, and measured-load verification
remain release gates.

The 6–10 Ah battery is intended for supervised short-duration and overnight
testing. It must not be described as multi-day autonomous operation until the
event-driven LTE load, night-time deficit, and charging performance are measured.

Detailed nominal, margin, poor-weather, and 72-hour calculations are recorded
in [POWER_CALCULATIONS.md](POWER_CALCULATIONS.md).

## Required measurements before release

- 24-hour current log covering sampling, idle, security, modem registration, reconnect, and LTE transmit peaks.
- Converter efficiency, ripple, temperature, voltage drop, and brownout behavior.
- Battery BMS/charge limits and MPPT compatibility with panel Voc/Isc.
- Fuse, wire, connector, disconnect, reverse-polarity, and transient-protection ratings.
- Supervised solar/recovery trial with logged signal, current, charging, and temperature data.

## Cloud/development power

The development computer and cloud service use separate infrastructure power. Measure local-host startup, idle, storage, dashboard, and processing loads separately. Never include these loads in the buoy battery/solar calculation.

Final panel, charger, battery, converter, fuse, and wire selections remain `TBD` until the LTE modem and all installed buoy loads are frozen and bench measured.
