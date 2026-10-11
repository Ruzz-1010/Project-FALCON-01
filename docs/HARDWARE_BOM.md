# FALCON-01 Revised Event-Driven BOM and Procurement Baseline

<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Status: proposal-stage equipment baseline, revised 2026-10-10 after DOST feedback. This is **not** a fabrication release and **not** a purchase order. Prices are Philippine-peso planning ranges from currently observed online listings, local supplier references, and conservative allowances. Reconfirm live price, stock, seller rating, warranty, exact SKU, cable length, output type, wetted material, and delivery date before buying.

## Design rule for this BOM

The minimum proposal is a **compact ESP32 buoy** that samples locally and uploads only summaries or events. It should not transmit every second. The baseline equipment is water pressure, wind speed/direction, GPS, solar/battery power, local buffering, and Wi-Fi/LTE internet. LoRa and a large Bay Station are fallback or legacy options only.

## Recommended minimum build

| Group | Item | Qty | Planning cost | Why it is included | Buy or validate first |
| --- | --- | ---: | ---: | --- | --- |
| Controller | ESP32 DevKit 30/38-pin | 1 | ₱350–₱600 | Main local sampler, event detector, and cloud packet controller | Buy first |
| Primary wave input | Low-range 4–20 mA submersible pressure transmitter, preferably 0–1 mH2O or 0–2 mH2O | 1 | ₱1,997–₱3,444 | Core pressure signal for estimated wave height | Validate seller specs first |
| Pressure interface | ADS1115, 150 Ω precision shunt, RC filter, clamp/protection parts | 1 lot | ₱250–₱700 | Converts 4–20 mA loop to ESP32-readable voltage | Buy with pressure sensor |
| Wind | Wind speed and direction sensor set, pulse/analog or RS485 depending on chosen model | 1 | ₱1,204–₱2,500 | Required wind channel after DOST revision | Validate output and wiring |
| Position/security | NEO-6M GPS module or equivalent GNSS board | 1 | ₱497–₱800 | Exact position, drift/geofence, timestamp support, security evidence | Buy first or simulate only for bench |
| Internet path | A7670E/SIM7600 LTE board with antenna and SIM, or Wi-Fi for lab/near-shore validation | 1 | ₱1,800–₱4,500 | Direct cloud upload without mandatory LoRa/Bay Station | Validate coverage and current peaks |
| Power monitor | INA219/INA260 or voltage divider plus current test point | 1 | ₱180–₱600 | Battery and solar validation | Buy after power branch choice |
| Local buffer | microSD module and 8–32 GB card, or ESP32 flash ring buffer for short tests | 0–1 | ₱250–₱700 | Prevent data loss during Wi-Fi/LTE outage | Include if field trial is remote |
| Motion/tamper event | MPU6050/GY-521, SW-420, reed switch, or enclosure switch | 0–1 lot | ₱100–₱900 | Optional event trigger/security input; not a wave sensor | Add only if event rule needs it |
| Optional context | DS18B20 waterproof temperature probe | 0–1 | ₱65–₱180 | Context only; not part of minimum research claim | Defer if budget is tight |

## Power, enclosure, and deployment hardware

| Group | Item | Qty | Planning cost | Notes |
| --- | --- | ---: | ---: | --- |
| Battery | 12.8 V LiFePO4 6–10 Ah with BMS, or smaller pack after measured duty-cycle test | 1 | ₱2,000–₱6,000 | DOST asked to avoid oversized battery; final size follows LTE peak and overnight load. |
| Solar | 10–30 W compact panel for prototype; 40–100 W only if measured load demands it | 1 | ₱1,000–₱3,000 | Keep small for compact buoy; 100 W local catalog reference is around ₱2,200 but may be physically too large. |
| Charge control | LiFePO4-compatible PWM/MPPT controller or protected solar charger | 1 | ₱850–₱3,500 | Choose based on battery chemistry and panel voltage; cheap boards require bench verification. |
| Regulators/protection | 12 V loop branch, 5 V/LTE branch, 3.3 V sensor rail, fuses, TVS, reverse protection | 1 lot | ₱800–₱2,500 | LTE modem branch must survive registration/transmit current peaks. |
| Enclosure | Waterproof electronics box, cable glands, vent/desiccant if gauge pressure sensor is used | 1 lot | ₱2,500–₱7,000 | Includes sealing hardware; exact size follows layout. |
| Float body | Compact can buoy body, PVC/HDPE/fiberglass or locally fabricated float | 1 | ₱2,000–₱8,000 | Must pass displacement, ballast, leak, and recovery tests. |
| Mooring | Eye bolt, chain, rope, shackle, swivel, anchor/deadweight, recovery line | 1 lot | ₱2,000–₱6,000 | Missing item in earlier list; size by depth, current, seabed, and retrieval method. |
| Fabrication and tests | Sealants, fasteners, brackets, calibration container, spare connectors, transport allowance | 1 lot | ₱2,000–₱5,000 | Needed before any validation claim. |

## Working total scenarios

| Scenario | Includes | Planning total | Use case |
| --- | --- | ---: | --- |
| Bench-only cloud prototype | ESP32, pressure interface simulator or one pressure sensor, GPS, Wi-Fi, minimal power, no full mooring | ₱8,000–₱18,000 | Proposal demo and software validation. |
| Compact Option A field-capable prototype | Full core sensors, LTE, small solar/battery, sealed enclosure, compact float, mooring/anchor allowance | ₱19,000–₱45,000 | Recommended DOST low-cost direction. |
| Option B catamaran backup | Same sensors plus wider deck/twin-float mechanical allowance | ₱22,000–₱55,000 | Use only if stability is prioritized over lowest fabrication effort. |
| With LoRa fallback added | Adds LoRa pair, shore receiver, mast/cabling allowance | Add ₱2,000–₱8,000 | Optional fallback when LTE coverage/data plan fails. |

## Purchase priority

1. Buy or borrow ESP32, ADS1115, shunt/protection parts, GPS, and one candidate pressure transmitter.
2. Bench-test the pressure loop and LTE current peaks before buying the final battery and solar panel.
3. Add wind speed/direction sensor after output type and calibration plan are confirmed.
4. Buy enclosure, cable glands, float body, and mooring hardware only after the internal layout and mass estimate are frozen.
5. Keep LoRa/Bay Station parts out of the base budget unless Wi-Fi/LTE validation fails.

## Procurement evidence required before final approval

For every item, record supplier, URL, price date, exact variant, photo, datasheet/manual, wiring, measured idle/transmit current when applicable, and reason for selection. For marketplace listings, the seller page is screening evidence only; final buying should use a dated screenshot or quotation.

## Source direction

- Shopee Philippines listing for 4–20 mA submersible water level transmitter, observed planning range ₱1,997–₱3,444: https://shopee.ph/Submersible-2-Liquid-Sensor-Tank-Pressure-4-20Ma-Hydrostatic-Water-River-Level-Transmitter-1-4-0M-i.1380515196.26470979857
- Shopee Philippines listing family for 1 m / 3 m / 5 m 4–20 mA hydrostatic level meter: https://shopee.ph/Water-Level-Transmitter-1m-3m-5m-Liquid-Water-Level-Sensor-4-20mA-Pool-Tank-Hydrostatic-Level-Meter-i.906740842.22061716970
- Holykell HPT604 Type A level sensor datasheet: https://www.holykell.com/wp-content/uploads/2023/08/HPT604A-Level-sensor-Datasheet-Holykell-V26-CS-1.pdf
- Blue Robotics Bar sensor guide: https://bluerobotics.com/learn/bar-sensors-guide/
- Makerlab PH wind speed sensor listing reference: https://makerlab.ph/products/anemometer-wind-speed-0-to-5v-analog
- SolarCalc PH catalog reference for local solar planning prices, including 100 W panel ₱2,200 as of 2026-03-15: https://solarcalcph.com/catalog/
- Spark Fruit PH 10 A solar charge controller listing: https://sparkfruit-ph.com/products/20a61c7d5de4e6d0f4c299f51d5bf970
- Shopee Philippines MPPT charge controller search reference, observed low-cost LiFePO4 MPPT listing around ₱847 in September 2026 crawl: https://shopee.ph/search?keyword=mppt+solar+charge+controller
