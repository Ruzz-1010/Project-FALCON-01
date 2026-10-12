# FALCON Buoy Power System — Event Driven Cloud Baseline v3.0


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

The buoy and cloud/development computer are separate power domains. No mini PC or LoRa gateway is installed on the buoy.

## Buoy power path

```text
6 x 3 W solar panels -> LiFePO4 solar charge controller -> 12.8 V 10 Ah LiFePO4 battery with built-in BMS
             -> fused disconnect/distribution -> protected regulated rails
             -> ESP32 + sensors + LTE modem/Wi-Fi + security electronics
```

The reduced-prototype starting point is a 12.8 V 10 Ah LiFePO4 battery with built-in BMS, an 80% usable-energy planning limit, and six compact 3 W solar panels for 18 W total nameplate capacity. A 12.8 V 12 Ah pack is acceptable if the 10 Ah version is unavailable. These are design assumptions, not validated endurance claims.

| Complete measured average buoy load | Daily energy | 12.8 V 10 Ah at 80% usable | 12.8 V 12 Ah at 80% usable |
| ---: | ---: | ---: | ---: |
| 0.5 W | 12 Wh/day | 205 h | 246 h |
| 1.5 W | 36 Wh/day | 68 h | 82 h |
| 3 W | 72 Wh/day | 34 h | 41 h |

Preliminary solar harvest uses `panel rating × 4 peak-sun-hours × 70% net efficiency`:

| Candidate | Planning harvest | Status |
| --- | ---: | --- |
| 18 W from 6 × 3 W panels | 50.4 Wh/day | Current compact-buoy proposal plan pending measured panel output |


At the 1.5 W event-driven planning load, the 18 W array gives a small theoretical recovery margin. That margin must still be proven because small panels lose output from heat, angle, shading, fouling, charge limits, and weather.
Panel Voc/Isc, charger compatibility, mounting, and measured-load verification
remain release gates.

The 12.8 V 10 Ah LiFePO4 battery is the realistic validation baseline for supervised short-duration and overnight testing. It gives better reserve than small 3.7 V or 7.4 V packs, but it must not be described as multi-day autonomous operation until the event-driven LTE load, night-time deficit, and charging performance are measured.

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
