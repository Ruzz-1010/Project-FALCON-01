# Provisional Buoy Power Calculations — Bay Station Baseline

Authority: [POWER_SYSTEM.md](POWER_SYSTEM.md). Values below are planning envelopes only.

## Load worksheet to complete

| Load | Voltage | Idle | Active | Peak | Duty cycle | Daily Wh | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ESP32 controller | TBD | TBD | TBD | TBD | TBD | TBD | 24-hour bench log |
| Bar02 + approved sensors | TBD | TBD | TBD | TBD | TBD | TBD | Datasheets + bench log |
| LoRa buoy radio | TBD | TBD | TBD | TBD | TBD | TBD | Gateway registration/reconnect/transmit test |
| Security electronics | TBD | TBD | TBD | TBD | TBD | TBD | Armed/alarm test |
| Conversion losses | — | — | — | — | — | TBD | Measured converter efficiency |

Do not total or finalize the design until exact parts and measured duty cycles exist.

## System-level planning scenarios

Because the LoRa radio, Bay Station Internet backhaul, and several auxiliary parts are not yet frozen, the
following are **whole-buoy planning scenarios**, not component consumption
claims. They let the team size a safe prototype before the 24-hour bench log is
available.

| Scenario | Average buoy load | Daily demand | Intended use |
| --- | ---: | ---: | --- |
| Low | 2 W | 48 Wh/day | Optimistic duty-cycled operation |
| Design | 4 W | 96 Wh/day | Recommended planning baseline |
| Stress | 6 W | 144 Wh/day | Continuous/reconnect-heavy upper test case |

Formula: `daily demand (Wh/day) = average load (W) × 24 h`.

## Battery planning

- Nominal provisional battery: `12.8 V × 20 Ah = 256 Wh`.
- Provisional usable energy at 80%: `256 Wh × 0.80 = 204.8 Wh`.
- No-solar runtime: `usable Wh ÷ measured average W`.

### Battery results

| Average load | 20 Ah no-solar runtime | 20 Ah autonomy | Nominal capacity required for 72 h at 80% usable |
| ---: | ---: | ---: | ---: |
| 2 W | 102.4 h | 4.27 days | 14.1 Ah; select at least 15 Ah |
| 4 W | 51.2 h | 2.13 days | 28.1 Ah; select at least 30 Ah |
| 6 W | 34.1 h | 1.42 days | 42.2 Ah; select at least 45 Ah |

Formula: `required Ah = average W × autonomy h ÷ (12.8 V × 0.80)`.
Therefore, the provisional 20 Ah battery does **not** meet a 72-hour no-solar
target at the 4 W design load. It is acceptable only as an early prototype
battery or if the verified autonomy requirement is shorter.

## Solar planning

- Preliminary harvest: `panel W × 4 peak-sun-hours × 0.70`.
- 40 W candidate: `112 Wh/day`.
- 60 W candidate: `168 Wh/day`.
- Required margin must cover poor weather, temperature, fouling, orientation, conversion losses, charge limits, and LoRa radio peaks. Bay Station SIM/4G/5G energy is a separate shore budget.

### Nominal four-peak-sun-hour energy balance

| Average load | Daily demand | 40 W panel balance | 60 W panel balance |
| ---: | ---: | ---: | ---: |
| 2 W | 48 Wh | +64 Wh/day | +120 Wh/day |
| 4 W | 96 Wh | +16 Wh/day | +72 Wh/day |
| 6 W | 144 Wh | −32 Wh/day | +24 Wh/day |

Positive balance means theoretical energy remains for battery recovery after
serving that day's load. It is not a guaranteed field yield.

For a 25% energy margin, the minimum calculated panel rating is:

| Average load | Break-even panel | Panel with 25% margin |
| ---: | ---: | ---: |
| 2 W | 17.1 W | 21.4 W |
| 4 W | 34.3 W | 42.9 W |
| 6 W | 51.4 W | 64.3 W |

Formula: `panel W = daily demand ÷ (4 h × 0.70)`; multiply by `1.25` for the
planning margin. This supports a **60 W minimum prototype recommendation only
if measured average load remains at or below 4 W**. A 6 W average load requires
a larger panel to retain the same margin.

### Poor-weather sensitivity

For a deliberately conservative day of `2 peak-sun-hours × 60% net yield`:

| Panel | Harvest | Break-even average load |
| ---: | ---: | ---: |
| 40 W | 48 Wh/day | 2 W |
| 60 W | 72 Wh/day | 3 W |

The battery must supply the daily deficit whenever the measured buoy load is
above those values. Multi-day weather autonomy must be checked using the actual
deployment site's solar resource, shading, tilt, salt fouling, and seasonal data.

## Recommended provisional baseline

- Use the 4 W design scenario until a complete 24-hour log replaces it.
- Use a 60 W nominal solar candidate for the supervised prototype.
- Use 20 Ah only for early testing; use at least 30 Ah if the requirement is
  72 hours without solar at a verified 4 W average load.
- Select MPPT, panel, battery, converters, wiring, connectors, and fuses only
  after exact voltage/current limits and LoRa peak behavior are documented. Select the Bay Station SIM/4G/5G backhaul from a separate shore power budget.
- Do not call this an endurance validation until the 72-hour supervised solar
  test passes.

## Measurement worksheet method

For each branch, log timestamp, input voltage, current, operating state, and
temperature at one-second resolution during registration/reconnect tests and at
one-minute resolution for the complete 24-hour run. Calculate:

- `instantaneous W = V × A`;
- `interval Wh = W × interval seconds ÷ 3600`;
- `daily Wh = sum(interval Wh)`;
- `average W = daily Wh ÷ 24`;
- peak current as the maximum captured value, not the daily average.

The final power budget must use measured converter-input energy so conversion
losses are included rather than counted twice.

## Bay Station exclusion

The mini PC is shore based and facility powered or separately backed by a UPS. Its energy use is measured separately and never included in buoy autonomy.

## Acceptance gates

1. No brownout during repeated LoRa radio registration and transmit peaks.
2. Every branch fuse and conductor is sized from measured peak/fault requirements.
3. Battery/MPPT/panel compatibility is documented from exact datasheets.
4. 24-hour load logging and at least 72-hour supervised solar endurance pass.
