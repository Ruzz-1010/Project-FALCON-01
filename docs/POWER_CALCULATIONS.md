# Provisional Buoy Power Calculations — Event Driven Cloud Baseline


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Authority: [POWER_SYSTEM.md](POWER_SYSTEM.md). Values below are planning envelopes only.

## Load worksheet to complete

| Load | Voltage | Idle | Active | Peak | Duty cycle | Daily Wh | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ESP32 controller | TBD | TBD | TBD | TBD | TBD | TBD | 24-hour bench log |
| Approved pressure, wind, and movement sensors | TBD | TBD | TBD | TBD | TBD | TBD | Datasheets + bench log |
| 4G/LTE modem or Wi-Fi radio | TBD | TBD | TBD | TBD | TBD | TBD | Registration/reconnect/event-upload test |
| Security and local storage | TBD | TBD | TBD | TBD | TBD | TBD | Armed/alarm and buffer test |
| Conversion losses | — | — | — | — | — | TBD | Measured converter efficiency |

Do not total or finalize the design until exact parts and measured duty cycles exist.

## Event-driven planning scenarios

Because the LTE modem, cloud path, and auxiliary parts are not yet frozen, the following are whole-buoy planning scenarios, not component consumption claims. Event-driven reporting lowers average radio duty, but registration and upload create short current peaks.

| Scenario | Average buoy load | Daily demand | Intended use |
| --- | ---: | ---: | --- |
| Low | 0.5 W | 12 Wh/day | Deep sleep and infrequent summaries |
| Design | 1.5 W | 36 Wh/day | Initial event-driven planning baseline |
| Stress | 3 W | 72 Wh/day | Frequent reconnects or event uploads |

Formula: `daily demand (Wh/day) = average load (W) × 24 h`.

## Battery planning

- Nominal validation battery candidate: `12.8 V × 10 Ah = 128 Wh`. Acceptable substitute: `12.8 V × 12 Ah = 153.6 Wh` if the 10 Ah pack is unavailable.
- Provisional usable energy at 80%: `nominal Wh × 0.80`.
- No-solar runtime: `usable Wh ÷ measured average W`.
- The regulator must survive the LTE modem's transmit and registration peaks even when average energy use is low.

| Average load | 12.8 V 10 Ah battery at 80% usable | 12.8 V 12 Ah substitute at 80% usable |
| ---: | ---: | ---: |
| 0.5 W | 205 h | 246 h |
| 1.5 W | 68 h | 82 h |
| 3 W | 34 h | 41 h |

These are calculations, not field results. The 12.8 V 10 Ah LiFePO4 pack is the realistic validation baseline because it gives enough reserve for LTE/GPS peaks, night operation, cloudy periods, and uncertain sensor load. Multi-day autonomy still requires measured load and solar recovery tests.

## Solar planning

- Preliminary harvest: `panel W × 4 peak-sun-hours × 0.70`.
- Proposed compact array: `6 panels × 3 W = 18 W`, with preliminary harvest `18 W × 4 peak-sun-hours × 0.70 = 50.4 Wh/day`.
- The 18 W value is the current proposal plan; final output must be measured because small panels lose power from heat, angle, shading, salt, and charge-controller losses.
- Margin must cover poor weather, shading, fouling, orientation, conversion losses, charge limits, and LTE modem peaks.

| Average load | Daily demand | 18 W solar array balance |
| ---: | ---: | ---: |
| 0.5 W | 12 Wh | +38 Wh/day |
| 1.5 W | 36 Wh | +14 Wh/day |
| 3 W | 72 Wh | −22 Wh/day |

Positive balance means theoretical energy remains for battery recovery. It is not a guaranteed field yield.

## Recommended provisional baseline

- Use the measured event-driven load as the design scenario after the first 24-hour log.
- Start with a 12.8 V 10 Ah LiFePO4 battery with built-in BMS; use 12.8 V 12 Ah only if the 10 Ah version is unavailable.
- Start with the current solar plan of six 3 W compact panels, for 18 W total nameplate capacity.
- Select the regulator, battery, panel, wiring, connectors, and fuses after the exact LTE peak current and modem sleep/transmit duty cycle are documented.
- Do not call this endurance validation until a supervised test passes with logged current, charging, temperature, signal state, and recovery data.

## Measurement worksheet method

For each branch, log timestamp, input voltage, current, operating state, network state, and temperature at one-second resolution during modem registration/reconnect tests and at one-minute resolution for the complete 24-hour run. Calculate:

- `instantaneous W = V × A`;
- `interval Wh = W × interval seconds ÷ 3600`;
- `daily Wh = sum(interval Wh)`;
- `average W = daily Wh ÷ 24`;
- peak current as the maximum captured value, not the daily average.

The final power budget must use measured converter-input energy so conversion losses are included rather than counted twice.

## Cloud infrastructure exclusion

Cloud hosting and any development computer are separate shore/infrastructure costs. They are not included in buoy autonomy calculations.

## Acceptance gates

1. No brownout during repeated LTE modem registration and event-upload peaks.
2. Every branch fuse and conductor is sized from measured peak/fault requirements.
3. Battery, regulator, panel, and modem compatibility is documented from exact datasheets.
4. A 24-hour load log and a supervised solar/recovery test pass.

