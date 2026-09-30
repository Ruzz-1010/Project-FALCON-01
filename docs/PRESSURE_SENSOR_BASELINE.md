# Project FALCON Pressure-Sensor Baseline

Revision: 1.0  
Date: 2026-09-10  
Status: recommended deployment candidate; procurement, supplier confirmation, integration, and validation pending

## Decision

The recommended Phase 1 long-duration deployment candidate is a **Holykell HPT604 Type A submersible level transmitter** ordered with the following provisional configuration:

- `0–2 mH2O` vented-gauge range;
- `4–20 mA`, two-wire output;
- `±0.5% full-scale` accuracy or better;
- 316L-wetted construction;
- fixed IP68 vented cable, with an anti-corrosive cable option requested;
- protected 12 V buoy supply.

This exact configuration is a procurement target, not installed or validated hardware. Before payment, the supplier must confirm in writing the complete order code, continuous saltwater suitability, wetted materials, seal material, cable jacket, cable length, range, overload, response time, supply range, and calibration certificate. The final range must also be checked against installation depth, expected dynamic pressure, tide, and overpressure margin.

The **Blue Robotics Bar02 R2 is reclassified as bench-only / short-duration comparison hardware**. The manufacturer requires its gel sensing element to dry for at least two hours per day and states that it must not remain submerged for more than 24 hours. It therefore cannot be the unattended long-term deployment baseline.

## Why this candidate

The HPT604 is an industrial submersible level transmitter with a fixed vented IP68 cable and 4–20 mA current-loop option. A current loop is more appropriate than a long exposed I2C cable for the buoy-to-pod run because it is less sensitive to cable voltage drop and electrical noise. The Type A manufacturer sheet lists 7–30 V DC for 4–20 mA, response time no greater than 20 ms, typical accuracy no worse than ±0.5% full scale, and medium compatibility with 316L stainless steel. These specifications are promising but do not by themselves prove multi-month seawater durability in the FALCON installation.

## Required electrical interface

```text
Protected +12 V
    -> fuse / resettable protection
    -> reverse-polarity and surge protection
    -> HPT604 4–20 mA loop
    -> 150 ohm, 0.1%, low-tempco shunt resistor
    -> RC input filter and clamping protection
    -> ADS1115 differential/single-ended ADC at 3.3 V
    -> protected I2C -> ESP32

Loop return, ADC ground, and system ground follow the reviewed grounding plan.
```

Across 150 ohms, 4–20 mA becomes approximately `0.60–3.00 V`, which fits a 3.3 V ADC input with margin. Resistor power at 20 mA is about `0.06 W`; use at least a 0.25 W precision part after tolerance and fault review. The exact TVS, filter, connector, fuse, grounding, and ADC gain must be frozen in the revised schematic and verified on the bench.

At a 12 V loop supply, the sensor-loop planning load is approximately `0.048–0.240 W` before converter losses. For a 0–2 mH2O range, ±0.5% FS corresponds to about ±10 mm of static water level before installation, temperature, ADC, calibration, dynamic-response, and wave-reconstruction errors. This is not a ±10 mm wave-height accuracy claim.

The existing Bar02 JST-GH I2C connector and current carrier PCB are **not electrically compatible** with this 4–20 mA sensor. They must not be adapted by merely changing a label. PCB fabrication remains blocked until the new analog loop input is designed, reviewed, and tested.

## Vented-cable installation rule

The gauge-reference vent tube must terminate in a dry, breathable location using the supplier-approved desiccant or breather arrangement. Do not block the vent, immerse the cable end, or seal it into trapped pressure. Provide strain relief, drip routing, corrosion protection, a service loop, and a replaceable desiccant/vent inspection schedule inside the dry electronics area.

## Procurement and budget gate

The project budget target is **below PHP 10,000 for the sensor**, excluding shipping and import charges. Public marketplace prices are only screening evidence; obtain a dated supplier quotation for the exact configuration. Include the ADS1115, precision shunt, protection, connector/gland, and cable termination as a separate interface allowance. Do not substitute a high-range threaded automotive or pump transducer simply because it is cheaper: excessive range reduces shallow-wave resolution and usually does not solve underwater cable sealing.

If the exact HPT604 configuration cannot be confirmed below the budget, request quotations for an equivalent continuous-submersion 4–20 mA vented-gauge transmitter and apply the same acceptance gates. A KELLER Series 26Y is a future higher-cost alternative, not the current budget baseline.

## Validation gates

1. Supplier confirmation and receiving inspection.
2. Dry electrical test at 4, 12, and 20 mA simulation points before connecting the probe.
3. Static water-column calibration at at least five increasing and decreasing depths.
4. Independent verification run with frozen coefficients.
5. Controlled dynamic wave comparison with synchronized reference displacement.
6. Cable, vent, leak, salt-exposure, fouling, corrosion, drift, and temperature checks.
7. 24-hour integrated bench soak, supervised 72-hour wet trial, then adviser-approved staged field trials.
8. Maintenance and retrieval interval based on observed drift, fouling, desiccant state, and connector condition.

The dashboard must continue to label the derived value **Estimated wave height**. It must preserve raw loop current/pressure, calibration version, quality state, installation depth, and timestamps. A sensor fault must produce `INVALID`, `STALE`, or `OFFLINE`, never a fabricated zero.

## Primary references

- Holykell, *HPT604 Type A level sensor datasheet*: https://www.holykell.com/wp-content/uploads/2023/08/HPT604A-Level-sensor-Datasheet-Holykell-V26-CS-1.pdf
- Holykell, *HPT604 product family*: https://www.holykell.com/products/HPT604-H_Water_Level_Sensor_with_Economical_Model.html
- Blue Robotics, *Bar sensor guide*: https://bluerobotics.com/learn/bar-sensors-guide/
- KELLER, *Series 26Y standard level probe* (future alternative): https://keller-pressure.com/en/products/level-probes/standard-level-probes/series-26y
