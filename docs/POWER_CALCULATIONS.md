# Provisional Buoy Power Calculations — Bay Station Baseline

Authority: [POWER_SYSTEM.md](POWER_SYSTEM.md). Values below are planning envelopes only.

## Load worksheet to complete

| Load | Voltage | Idle | Active | Peak | Duty cycle | Daily Wh | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ESP32 controller | TBD | TBD | TBD | TBD | TBD | TBD | 24-hour bench log |
| Bar02 + approved sensors | TBD | TBD | TBD | TBD | TBD | TBD | Datasheets + bench log |
| LTE/cellular modem | TBD | TBD | TBD | TBD | TBD | TBD | Registration/reconnect/transmit test |
| Security electronics | TBD | TBD | TBD | TBD | TBD | TBD | Armed/alarm test |
| Conversion losses | — | — | — | — | — | TBD | Measured converter efficiency |

Do not total or finalize the design until exact parts and measured duty cycles exist.

## Battery planning

- Nominal provisional battery: `12.8 V × 20 Ah = 256 Wh`.
- Provisional usable energy at 80%: `256 Wh × 0.80 = 204.8 Wh`.
- No-solar runtime: `usable Wh ÷ measured average W`.

## Solar planning

- Preliminary harvest: `panel W × 4 peak-sun-hours × 0.70`.
- 40 W candidate: `112 Wh/day`.
- 60 W candidate: `168 Wh/day`.
- Required margin must cover poor weather, temperature, fouling, orientation, conversion losses, charge limits, and LTE peaks.

## Bay Station exclusion

The mini PC is shore based and facility powered or separately backed by a UPS. Its energy use is measured separately and never included in buoy autonomy.

## Acceptance gates

1. No brownout during repeated modem registration and transmit peaks.
2. Every branch fuse and conductor is sized from measured peak/fault requirements.
3. Battery/MPPT/panel compatibility is documented from exact datasheets.
4. 24-hour load logging and at least 72-hour supervised solar endurance pass.
