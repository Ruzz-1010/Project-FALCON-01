# Project FALCON-01 — Durable Memory

Last updated: 2026-11-07. Read this first when taking over the project.

## Project identity

- **Project:** FALCON-01, a low-cost solar-powered near-shore observation buoy.
- **Academic status:** undergraduate title/proposal-defense prototype; hardware integration and field validation are not complete.
- **Controller:** ESP32 for acquisition, validation, buffering, timestamps, summaries, and upload scheduling.
- **Main measurement:** water pressure. Wave height is derived/estimated, not directly measured and not yet reference-calibrated.
- **Context channels:** wind speed/direction, GPS position/time, battery and solar status, enclosure health/tamper, and communication state.
- **Connectivity:** Wi-Fi for bench work; LTE/4G is the proposed field link.
- **Products:** operator dashboard, read-only public Palawan map, storage, alerts, and an AI-assisted 15-minute research estimate.

## Current hardware baseline

Treat exact seller specifications as pending until datasheets and bench tests confirm them.

| Item | Current decision | Evidence state |
| --- | --- | --- |
| ESP32 | Main buoy controller | Selected; integration pending |
| Pressure transmitter | 24 V, two-wire 4–20 mA, SS316, purchased 5 m measurement range | User-reported/purchased; calibration pending |
| Pressure interface | Precision shunt resistor → ADS1115 16-bit ADC → ESP32 over I²C | Required design; resistor and safe range must be finalized |
| 24 V rail | Fused DC–DC boost converter from the 12.8 V battery | Proposed; continuous-load/thermal test pending |
| Battery | 12.8 V 8 Ah LiFePO4 with BMS | Selected capacity; load test pending |
| Solar | Six compact nominal 5 V panels, two strings of three in series, then paralleled (3S2P) | Proposed; verify actual Vmp, Imp, and wattage |
| Charge controller | LiFePO4-compatible and matched to final array | Model not frozen |
| Wind | Anemometer plus wind-vane/direction sensor | Required; exact models/interfaces not frozen |
| GPS | GNSS receiver for position, time, drift, and geofence | Required; exact model not frozen |
| Power monitor | INA260 or approved equivalent | Proposed; verify rail range and placement |

The ADS1115 does not sense pressure directly. The transmitter senses pressure and outputs 4–20 mA; the shunt converts current to voltage; the ADS1115 digitizes voltage; the ESP32 converts it to current, pressure, and then an estimated wave value. Never connect 24 V directly to the ADS1115 or ESP32 ADC.

## Pressure placement and wave method

The transmitter must be fixed relative to the seabed or an independent mooring reference. It must not hang at a constant distance below the floating buoy, because buoy and sensor would heave together and suppress the relative pressure change. The 5 m rating is the measurement span, not an instruction to hang it 5 m below the buoy and not, by itself, the maximum total sea depth.

Processing baseline:

1. acquire a proposed 4 Hz pressure burst with stable timestamps;
2. convert 4–20 mA to pressure after bench calibration;
3. remove offset/baseline, spikes, slow trend, invalid and saturated samples;
4. convert pressure fluctuation to water-column displacement;
5. apply frequency-dependent pressure-response correction for sensor depth;
6. reject frequency bins with weak response/SNR so correction does not amplify noise excessively;
7. calculate pressure-derived spectral wave height and compare it with an independent reference.

The simple `ΔP/(ρg)` and max-minus-min calculation is only an initial or controlled-test estimate. It is not the complete field method for irregular waves. A 4 Hz rate gives a 2 Hz Nyquist limit, but the usable band must also respect transmitter response time and calibration results.

## AI decision

AI-assisted **15-minute wave-height prediction is current thesis scope**, not merely a future enhancement. The planned Python model uses recent validated pressure-derived wave-height observations and wind context. It must use a chronological train/validation/test split and be compared with persistence and damped-trend baselines using MAE, RMSE, and mean bias. Until trained and evaluated, the current deterministic forecast code is a software baseline/demo, not a validated ML result.

Use the wording **AI-assisted 15-minute research estimate**. It is not an official PAGASA forecast, warning, or measured value. Advanced models, longer horizons, and larger multi-site datasets are future enhancements.

## Dashboards

- `dashboard-next/`: canonical operator dashboard with detailed wave, pressure, wind, GPS/security, power, health, records, and alerts.
- `public-dashboard/`: separate read-only Palawan map with simplified station condition, wind, reporting state, and last update. No controls, raw logs, or protected security details.
- Public demo pins: Puerto Princesa, Dumaran, Roxas, and San Vicente. They remain test/simulated stations until physical endpoints exist.
- `edge/static/dashboard/`: built operator dashboard served by the Python service.

## Truth states

| Label | Meaning |
| --- | --- |
| `LIVE` | Current physical telemetry within the freshness limit |
| `SIMULATED` | Presentation/development data only |
| `ESTIMATED` | Derived from a measured quantity |
| `CALIBRATION REQUIRED` | No accepted reference calibration |
| `MODEL OUTPUT` | Prediction, never a measured value |
| `COLLECTING` | Insufficient validated history |
| `STALE` / `OFFLINE` | No sufficiently recent telemetry |

## Canonical files and code

```text
docs/prd.md             scope and acceptance requirements
docs/architecture.md    hardware/software/data architecture
docs/rules.md           truth, safety, and validation rules
docs/design.md          UI and physical design baseline
docs/task.md            status, blockers, and next work
docs/memory.md          durable decisions and takeover context
dashboard-next/         operator dashboard source
public-dashboard/       public Palawan map
edge/falcon_edge/       Python service, storage, alerts, prediction baseline
edge/static/dashboard/  built operator dashboard
src/                    ESP32 firmware
hardware/kicad/         carrier-board work; verify against final modules
docs-archive/           historical reference only
```

The thesis filename has changed several times. Before editing a DOCX, ask which file is authoritative. The most recently discussed local file was `/home/ruzz/Downloads/ThesisPaperchecked-11-01-26-3.docx`.

## Commands

```bash
PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v
cd dashboard-next && npm run build
cd public-dashboard && npm run build
cd edge && python3 -m falcon_edge.service
```

## Critical open risks

- Pressure placement, depth-response correction, calibration, and reference procedure still need physical validation.
- The 24 V loop, boost converter, shunt, ADS1115 range, protection, grounding, and transmitter response are not bench-proven.
- Seller solar ratings may be inconsistent; six panels cannot be called 30 W until verified.
- Battery autonomy and 24/7 operation require measured load and solar tests.
- Wind, GPS, modem, controller, connectors, fuse, and enclosure models are not frozen.
- The ML model has not been trained or chronologically evaluated.
- The repository is detached/mid-rebase with extensive user changes. Preserve them; do not commit or reset until deliberately resolved.

## Durable decisions

| Date | Decision |
| --- | --- |
| 2026-10-10 | Use the DOST revision scope; ESP32 buoy, pressure-derived wave estimate, wind, GPS, event-driven telemetry, and no buoy-side mini PC. |
| 2026-11-01 | `dashboard-next/` is the canonical operator interface. |
| 2026-11-02 | Maintain six canonical active docs; archive older material. |
| 2026-11-07 | The 15-minute AI-assisted prediction is current scope and must be tested against transparent baselines. |
| 2026-11-07 | Fix the pressure sensor to a seabed/mooring reference and include attenuation/noise correction. |
