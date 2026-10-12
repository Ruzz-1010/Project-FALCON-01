# Project FALCON Complete Equipment Budget and Approval List

Date prepared: 2026-10-12
Status: proposal / validation approval reference; planning prices only

This list includes sensors, ESP32/prototyping parts, power parts, buoy body, waterproofing, mooring hardware, and operating allowances so the panel can compute the full budget proposal.

## Budget summary

| Budget view | Estimated range | Meaning |
| --- | ---: | --- |
| Required full replacement estimate | ₱ 11,901-₱ 23,276 | All required parts including ESP32, breadboard, jumper wires, and buck converters even if the group already owns them. |
| Estimated cash-out if reusable kit parts are already available | ₱ 11,311-₱ 22,026 | Same required build, but subtracts ESP32, breadboard, jumper wires, and buck converter replacement allowance. |
| Field validation with LTE and optional event/security modules | ₱ 13,223-₱ 25,329 | Adds LTE, microSD, MPU6050, SW-420, reed switch, and similar conditional/optional modules. |
| Suggested contingency | Add 10-15% | For shipping changes, seller price changes, extra waterproofing, failed parts, and small hardware not listed by exact SKU. |

## Complete bill of materials

### Core sensors and interface

| Item | Qty | Unit price | Subtotal | Source or note |
| --- | ---: | ---: | ---: | --- |
| Water pressure transmitter, low range 4-20 mA | 1 pc | ₱2,897-₱3,720 | ₱2,897-₱3,720 | Lazada hydrostatic/QDY30A listings; confirm low water-level range, IP68, material, cable, and output. |
| ADS1115 ADC module | 1 pc | ₱135-₱290 | ₱135-₱290 | Lazada/local electronics; needed for pressure interface. |
| 150 ohm shunt, RC filter, fuse/protection parts | 1 set | ₱100-₱250 | ₱100-₱250 | Local electronics; needed for safe 4-20 mA reading. |
| Wind speed and direction sensor | 1 pc | ₱1,204-₱1,639 | ₱1,204-₱1,639 | Shopee/Lazada combined cup anemometer plus vane; confirm direction is included. |
| NEO-6M GPS / GNSS module | 1 pc | ₱299-₱497 | ₱299-₱497 | MakerLab/Lazada GPS listings. |
| INA219 current and power monitor | 1 pc | ₱83-₱180 | ₱83-₱180 | Shopee/imBento/Lazada; used for measured power budget. |
| ESP32 DevKit board | 1 pc | ₱250-₱450 | ₱250-₱450 | REUSE/OWNED for bench if available; replacement estimate shown. Existing kit can be reused for bench; include replacement price for full budget. |

### Communication and data

| Item | Qty | Unit price | Subtotal | Source or note |
| --- | ---: | ---: | ---: | --- |
| A7670E LTE Cat-1 internet module | 1 pc if no stable Wi-Fi | ₱1,015-₱1,151 | ₱1,015-₱1,151 | Buy only if field site has no reliable Wi-Fi; ESP32 Wi-Fi is enough for lab/near-shore validation. |
| microSD module plus 8-32 GB card | 1 set optional | ₱100-₱300 | ₱100-₱300 | Optional data backup if Wi-Fi/LTE drops during field test. |

### Optional event/security

| Item | Qty | Unit price | Subtotal | Source or note |
| --- | ---: | ---: | ---: | --- |
| MPU6050 / GY-521 tilt and motion sensor | 1 pc optional | ₱92-₱223 | ₱92-₱223 | Optional event/security support; does not replace pressure sensor. |
| SW-420 vibration sensor | 1 pc optional | ₱45-₱70 | ₱45-₱70 | Optional hit/tamper trigger. |
| Reed switch or magnetic lid switch | 1 pc optional | ₱70-₱309 | ₱70-₱309 | Optional enclosure open/tamper trigger. |

### Prototyping and wiring

| Item | Qty | Unit price | Subtotal | Source or note |
| --- | ---: | ---: | ---: | --- |
| Breadboard | 1 pc | ₱100-₱250 | ₱100-₱250 | REUSE/OWNED for bench if available; replacement estimate shown. Existing kit can be reused for bench validation only. |
| Jumper wires / Dupont wires | 1 set | ₱80-₱150 | ₱80-₱150 | REUSE/OWNED for bench if available; replacement estimate shown. Existing jumper wires can be reused; include replacement cost for budget. |
| Buck converter modules | 2 pcs | ₱160-₱400 | ₱160-₱400 | REUSE/OWNED for bench if available; replacement estimate shown. Existing modules can be reused; final build should verify voltage and current rating. |
| Perfboard or small prototype PCB | 1 pc | ₱60-₱150 | ₱60-₱150 | For cleaner final wiring than breadboard. |
| Terminal blocks, JST/Dupont connectors, pin headers | 1 lot | ₱150-₱300 | ₱150-₱300 | For removable sensor and power wiring. |
| Heat shrink, electrical tape, cable ties, wire labels | 1 lot | ₱150-₱300 | ₱150-₱300 | Wiring protection and labeling. |
| MAX485/RS485 interface module if wind sensor uses RS485 | 1 pc conditional | ₱50-₱120 | ₱50-₱120 | Needed only if selected wind sensor uses RS485. |

### Power system

| Item | Qty | Unit price | Subtotal | Source or note |
| --- | ---: | ---: | ---: | --- |
| Rechargeable battery pack with BMS | 1 pack | ₱1,500-₱3,500 | ₱1,500-₱3,500 | Protected Li-ion/LiPo or 18650 pack with BMS; target 37-74 Wh class after measured load. |
| Compact solar panel set | 6 pcs x 3 W panels | ₱235-₱500 each | ₱1,410-₱3,000 | Six small 3 W panels for 18 W total nameplate capacity; arrange around buoy body/top faces. |
| Solar charger / charge controller | 1 pc | ₱189-₱350 | ₱189-₱350 | Match charger to battery chemistry; do not connect solar directly to lithium battery. |
| BMS/fuse/switch/power protection set | 1 set | ₱250-₱500 | ₱250-₱500 | Battery safety, main switch, and fuse. |
| Battery holder/case and waterproof power connector | 1 set | ₱200-₱550 | ₱200-₱550 | For secured battery mounting and serviceable charging/power connection. |

### Safety and visibility

| Item | Qty | Unit price | Subtotal | Source or note |
| --- | ---: | ---: | ---: | --- |
| Flashing marine warning light / buoy beacon | 1 pc needed; 2 pcs if bundle | ₱459-₱550 | ₱459-₱550 | Current reference around PHP 458.59 plus tax for 2 pcs; use as flashing night marker, not steady area light. |

### Buoy body and waterproofing

| Item | Qty | Unit price | Subtotal | Source or note |
| --- | ---: | ---: | ---: | --- |
| Compact buoy body material, PVC/HDPE/float body | 1 set | ₱800-₱1,800 | ₱800-₱1,800 | Main body for compact buoy; can be PVC/HDPE/drum/foam based on final design. |
| Waterproof electronics enclosure IP65-IP67 | 1 pc | ₱300-₱800 | ₱300-₱800 | Dry compartment for ESP32, battery, charger, and wiring. |
| Cable glands PG7/PG9/PG11 | 1 set | ₱100-₱250 | ₱100-₱250 | Waterproof cable exits for sensors, panel, beacon, and antenna. |
| Marine epoxy, silicone sealant, gasket rubber | 1 lot | ₱250-₱600 | ₱250-₱600 | Sealing and leak protection. |
| Stainless bolts, nuts, washers, brackets | 1 lot | ₱200-₱500 | ₱200-₱500 | Corrosion resistant mounting hardware. |
| Short mast or tube for wind sensor, GPS, and beacon | 1 pc | ₱150-₱400 | ₱150-₱400 | Low mast only; keep compact and stable. |
| Pressure stilling/protection tube | 1 pc | ₱100-₱300 | ₱100-₱300 | Protects pressure sensor from direct impact and helps stabilize pressure reading. |
| Paint, reflective tape, labels | 1 lot | ₱150-₱400 | ₱150-₱400 | Visibility and labeling for field validation. |

### Mooring and deployment

| Item | Qty | Unit price | Subtotal | Source or note |
| --- | ---: | ---: | ---: | --- |
| Small anchor or concrete sinker | 1 pc | ₱500-₱1,500 | ₱500-₱1,500 | Final size depends on test location and current/wave conditions. |
| Chain, 2-3 m | 1 length | ₱300-₱800 | ₱300-₱800 | Adds weight near anchor and reduces rope abrasion. |
| Marine rope, 5-10 m | 1 length | ₱200-₱500 | ₱200-₱500 | Length depends on deployment depth and tide allowance. |
| Shackles, swivel, carabiner, thimble | 1 set | ₱150-₱400 | ₱150-₱400 | Mooring connections and anti-twist hardware. |
| Extra float/rope marker hardware | 1 set optional | ₱100-₱300 | ₱100-₱300 | Optional for retrieval and safety marking. |

### Validation and operations

| Item | Qty | Unit price | Subtotal | Source or note |
| --- | ---: | ---: | ---: | --- |
| SIM load / mobile data allowance | 1 month if LTE used | ₱100-₱300 | ₱100-₱300 | Only needed if LTE module is used. |
| Printing, transport, small consumables | 1 lot | ₱200-₱500 | ₱200-₱500 | Proposal validation and field test allowance. |

## Buying order

1. Use existing ESP32 kit, breadboard, jumper wires, buck converters, LEDs, and buttons for bench validation when possible, but keep replacement prices in the panel budget.
2. Confirm the water pressure transmitter range/output/material first because this is the core research measurement path.
3. Buy the ADS1115/shunt/protection interface with the pressure sensor so the ESP32 can read the 4-20 mA signal safely.
4. Add wind, GPS, INA219, battery, charger, solar panel, and flashing beacon after the pressure path is defined.
5. Measure current draw before final battery and solar sizing.
6. Buy LTE only when the validation site has no stable Wi-Fi; otherwise use ESP32 Wi-Fi for cloud validation.
7. Buy buoy body, waterproofing, cable glands, anchor, chain, rope, and stainless hardware as part of the same proposal budget, not as afterthoughts.
