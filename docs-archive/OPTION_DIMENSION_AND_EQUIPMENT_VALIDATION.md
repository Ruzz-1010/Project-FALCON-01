# FALCON Option Dimension and Equipment Validation

Date: 2026-10-14  
Status: **proposed design envelopes and procurement-control review.** DOST has not selected Option A, B, or C. These dimensions are drawn from the current visual option models for comparison only; they are not fabrication drawings or approved final dimensions.

## Purpose

Use this sheet to compare the three buoy forms, prevent unplanned equipment additions, and obtain comparable fabrication quotes. A selected option still needs a dimensioned drawing, actual purchased-component measurements, mass budget, displacement/waterline calculation, center-of-gravity calculation, heel/righting test, leak test, and controlled-water test before fabrication release.

## Proposed size envelopes

| Option | Render-derived envelope | First-pass float volume | What the number does and does not prove |
| --- | --- | ---: | --- |
| **A — compact can** | Main hull: **Ø840 mm × 500 mm**; visible top equipment: about **930 mm above the model waterline** | About **269 L** if fully immersed; about **109 L / 112 kg seawater-equivalent** at the model waterline | The compact body is easiest to transport and fabricate. It does **not** establish its safe payload, freeboard, or righting moment. |
| **B — catamaran** | Overall: about **1,500 mm long × 1,100 mm wide × 1,000 mm high** to wind head; two pontoons: **Ø220 mm × 1,500 mm** | About **54 L per pontoon**, **109 L / 112 kg** total if fully immersed | The wide stance can help initial stability. The model does **not** establish torsional strength, uneven-loading behavior, or a safe deck payload. |
| **C — ring** | Ring outside diameter: **1,100 mm**; tube diameter: **260 mm**; above-water mast/head: about **900 mm**; damping plate extends to about **565 mm below the model waterline** | About **140 L / 143 kg seawater-equivalent** if fully immersed | The wide ring can provide waterplane area. The model does **not** prove the center-frame joint, moon-pool behavior, or safe payload. |

The volume figures are geometric first-pass estimates using the visual models. They must be recalculated from the chosen manufactured body and confirmed by a loaded flotation test in the intended water type. A buoy must retain documented reserve buoyancy and freeboard; do not set its final payload from the fully immersed value.

## Materials to quote, by option

| Assembly | Option A — compact can | Option B — catamaran | Option C — ring |
| --- | --- | --- | --- |
| Float | UV-stabilized HDPE body or purpose-made HDPE float; clean new sealed container only | Two matching UV-stabilized HDPE pontoons or engineered marine-FRP pontoons | Closed-cell marine foam protected by HDPE or marine-FRP shell |
| Structure | 316 stainless or protected 6061-T6 aluminum short mast/brackets; EPDM-gasketed enclosure | Protected aluminum or 316 crossmembers/deck frame with reinforced pontoon joints | Structural center frame and braces that carry mast and mooring loads; foam must not carry those loads |
| Pressure protection | Rigid PVC-U or HDPE open-bottom stilling/protection tube | Rigid PVC-U or HDPE open-bottom stilling tube between pontoons; it is now shown in the Option B model | Protected pressure mount in moon-pool area; validate water exchange and pressure response |
| Common build material | UV-resistant polycarbonate/IP67 dry enclosure, EPDM gasket, 316 fasteners/back plates, tinned stranded copper wiring, correct waterproof glands, marine-rated rope/chain/shackles/swivel | Same | Same |

Do not use ordinary household plastic, previously used chemical drums, unrated carabiners, exposed breadboards, ordinary Dupont jumpers, or silicone/epoxy alone as the structural attachment for HDPE. IP rating of an unmodified enclosure does not certify the drilled and assembled buoy.

## Controlled equipment list

### Required on every selected buoy

| Group | Approved proposal-stage equipment | Quantity / decision |
| --- | --- | --- |
| Controller | ESP32 DevKit, 30/38 pin | 1 |
| Primary measurement | Low-range 4–20 mA submersible pressure transmitter, preferred 0–1 or 0–2 mH2O after seller confirmation | 1 |
| Pressure interface | ADS1115, 150 Ω precision shunt, RC filter, clamp/protection, protected loop supply | 1 set |
| Wind | Wind speed **and** wind direction sensor; confirm both are included in quote | 1 set |
| Position/security | NEO-6M/equivalent GNSS board and antenna | 1 |
| Battery health | INA219/INA260, or documented voltage/current-test arrangement | Required; define how solar and battery branches are measured |
| Buffer | microSD plus card **or** tested ESP32 flash ring buffer | One method is required for a remote trial |
| Power | 12.8 V 10 Ah LiFePO4 with BMS; LiFePO4-compatible solar charger; fused/protected rails | 1 system |
| Solar | Six 3 W panels, 18 W nameplate total, only as the current compact starting assumption | 6; final arrangement must match selected body and measured load |
| Protection and structure | Dry enclosure, glands, strain relief, stilling/protection tube, ballast arrangement, rated mooring/recovery hardware | 1 set |

### Conditional or optional

| Item | Decision rule |
| --- | --- |
| A7670E/SIM7600 LTE module, antenna and SIM | Required only when the selected field site has no reliable Wi-Fi. Validate local band support, power peaks and data plan. |
| Wi-Fi | Required lab/near-shore Internet path. It may be the only active Internet path for a controlled lab test. |
| MPU6050/LIS3DH, SW-420 or sealed reed switch | Optional tamper/motion event input only. It is not a replacement for the pressure sensor. |
| DS18B20 temperature probe | Optional context only. |
| microSD | Optional hardware only when a tested flash ring buffer is chosen; offline record retention itself remains required for a remote trial. |

### Excluded from the minimum build

- Raspberry Pi, mini PC, Orange Pi, and AI accelerator on the buoy.
- LoRa gateway/Bay Station hardware in the base Wi-Fi/LTE build.
- BNO085 as a required sensor, anchor-chain load cell, salinity, pH, dissolved oxygen, turbidity, camera, and other water-quality sensors.
- Any unselected alternative pressure sensor or duplicate communication path.

## Equipment verification before purchase

1. Pressure probe: exact model/order code, range, 4–20 mA output, supply voltage, wetted material, cable jacket/length, venting, response time, continuous saltwater immersion suitability, and calibration evidence.
2. Wind sensor: speed and direction outputs, supply, mounting, pinout, operating range, and reference-comparison plan.
3. GNSS/LTE: exact board dimensions, antenna connector, logic voltage, peak current, local network bands, and weather protection.
4. Power: exact panel Voc/Isc, series/parallel wiring, compatible LiFePO4 charging profile, battery BMS continuous/peak current, converter ratings, fuses, wire gauge and connectors.
5. Enclosure and body: actual internal component layout plus connector/service clearance before cutting holes; material grade, wall thickness, joining process and leak-test scope in the fabricator quote.
6. Mooring: actual site depth, tide range, seabed, current/wave exposure, retrieval plan and rated hardware. The render rope/chain lengths and anchor blocks are visual placeholders only.

## Acceptance checks before releasing a fabrication drawing

| Check | Required outcome |
| --- | --- |
| Mass and buoyancy | Measured complete mass, calculated displaced volume, loaded waterline and freeboard for the selected body. |
| Stability | Documented center of gravity, controlled heel/righting test and secured ballast test. |
| Dry fit | All selected components, connectors, cable bends and service access fit within the actual enclosure/body. |
| Water protection | Glands, lid/gasket, stilling tube and cable strain relief pass leak and splash/immersion checks appropriate to the planned trial. |
| Pressure response | 4/12/20 mA bench test, static depth calibration and controlled stilling-tube response test. Label output as estimated wave height. |
| Energy | 24-hour logged load including GPS and LTE peaks if LTE is selected; solar charging/recovery trial. |
| Mooring | Load path, attachment plates, rated hardware, chafe protection and retrieval plan reviewed for the actual site. |

## Decision for DOST/team

Choose one option only for detailed mechanical work. Then freeze the equipment above, obtain the actual component dimensions and material quotations, complete the listed checks, and issue a separate dimensioned fabrication drawing. Do not fabricate all three body options or buy optional/duplicate electronics before that decision.

## Sources

- `docs/PROTOTYPE_REDESIGN_BASELINE.md`
- `docs/HARDWARE_BOM.md`
- `docs/POWER_SYSTEM.md`
- `docs/PRESSURE_SENSOR_BASELINE.md`
- `docs/SENSOR_SELECTION_BASELINE.md`
- `THESIS DOCUMENTATION/FALCON Sensor Approval List for Panel.docx`
- current Option A, B and C presentation models under `static website presentation/buoy-options/`
