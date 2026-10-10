# FALCON-01 Phase 1 Procurement Baseline Revised


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

> This is a planning BOM, not a fabrication release. Reconfirm quantities, dimensions, connector variants, cable lengths, brackets, enclosure parts, ballast, and solar mounting hardware after the replacement prototype is approved.

Status: budgetary event-driven cloud buoy baseline, revised 2026-10-10. Prices are shown in
Philippine pesos using an indicative rate of **PHP 61.71 per USD**. They are raw
list-price conversions before shipping, import fees, tax, and Philippine reseller
markup. Confirm the live exchange rate, stock, revision, and ratings before ordering.

## Primary Sensors and Control

| Qty | Selected item | Budget | Procurement note |
| ---: | --- | ---: | --- |
| 1 | ESP32 DevKit 30/38-pin | PHP 349–500 | Main controller; exact board and regulator remain subject to bench test |
| 1 | Low-range submersible 4–20 mA pressure transmitter | PHP 1,690–4,278 | Preferred field option; written seawater/material confirmation required |
| 1 | ADS1115 plus 150 ohm precision shunt | PHP 200–600 | Current-loop interface; include protection and calibration points |
| 1 | MPU6050/GY-521 | PHP 533–923 | Movement/tilt event input; threshold tuning required |
| 0–1 | Pulse-output cup anemometer | PHP 1,350–2,500 | Optional wind channel; calibrate before claiming accuracy |

## Supporting Telemetry and Control

These items support operation, power validation, and security. They are not additional project sensors or primary monitoring objectives.

| Qty | Selected item | Budget | Procurement note |
| ---: | --- | ---: | --- |
| 0–1 | NEO-6M GPS module | PHP 208–598 | Supporting position/time/geofence telemetry; omit from bench-only build if not required |
| 1 | INA219 power monitor | PHP 116–250 | Supporting battery/current telemetry; voltage divider is a lower-cost fallback |
| 0–1 | DS18B20 waterproof probe | PHP 65–180 | Optional water-temperature context only |
| 0–1 | Magnetic reed/contact switch | PHP 95–200 | Enclosure security input |
| 0–1 | Buzzer and driver/protection | PHP 100–500 | Optional local alert output |
| 1 | A7670E or SIM7600 4G/LTE board + antenna/SIM | PHP 1,100–4,500 | Required for remote cloud path; freeze after coverage, data-plan, interface, antenna and reconnect tests |
| 0–1 | Wi-Fi access point | Existing or PHP 1,000–2,500 | Laboratory/near-shore path only |
| 0–1 | microSD module + 8–32 GB card | PHP 250–700 | Local outage buffer; ESP32 flash is a lower-cost short-buffer fallback |
| 0–1 | Enclosure fan/auxiliary cooling | TBD after thermal test | Include only if the buoy electronics enclosure demonstrates a measured need |

The previous subtotal is obsolete because adviser-approved security parts remain TBD. Recalculate the procurement total only after exact models and current supplier quotations are verified. It excludes fans,
power, connectors, enclosure, shipping, and optional antenna.

## Power and Installation Allowance

| Qty | Item | Budget | Release condition |
| ---: | --- | ---: | --- |
| 1 | 12.8 V 6–10 Ah LiFePO4 with BMS | PHP 2,000–6,000 | Starting candidate for event-driven prototype; size from measured LTE peaks and overnight deficit |
| 1 | 10 W or 20 W panel candidate | PHP 1,000–3,000 | Final rating follows measured buoy-only load; verify Voc/Isc with charger |
| 1 | LiFePO4 MPPT controller | PHP 3,085–8,025 | Genuine MPPT; programmable LiFePO4 profile |
| 1 | LTE modem regulated branch | TBD | Size from modem registration/transmit peaks and brownout test |
| 1 | ESP32/sensor regulated branch | PHP 620–1,850 | Final voltage/current from complete measured carrier load |
| lot | Fuses, disconnect, terminals, glands, marine wire | PHP 4,320–9,875 | Rated schedule and ingress review |

Internal connector baseline: JST GH 4-position (`BM04B-GHS-TBT`) for Bar02/I2C,
JST GH 3-position (`BM03B-GHS-TBT`) for low-current sensor signals and JST VH
2-position (`B2P-VH-FB-B`) for protected 5 V input. The earlier three-position
fan connector is superseded by the four-wire fan architecture in
`hardware/kicad/FALCON_CARRIER/FAN_SELECTION_BASELINE.md`; its exact dual-header
harness is pending physical connector inspection. Include matching housings, correctly sized
contacts, authorized crimp tooling, and spares; verify availability before
locking the PCB footprints.

The previous total is withdrawn because the exact pressure option, LTE/Wi-Fi cloud path, security inputs, final power branches, and enclosure needs are unresolved. Recalculate the reduced buoy budget after exact supplier quotations and measured power requirements exist.

## Primary Sources

- [Blue Robotics Bar02/Bar30 product](https://bluerobotics.com/store/sensors-cameras/sensors/bar-depth-pressure-sensor/)
- [Adafruit INA260 product](https://www.adafruit.com/product/4226)
- [Adafruit ADS1115 product](https://www.adafruit.com/product/1085)
- [Adafruit Ultimate GPS product](https://www.adafruit.com/product/746)
- [SparkFun Weather Meter Kit](https://www.sparkfun.com/weather-meter-kit.html)
- [Adafruit MCP9808 PID 1782](https://www.adafruit.com/product/1782)
- [Adafruit magnetic contact switch PID 375](https://www.adafruit.com/product/375)
- [Waveshare SIM7600G-H 4G HAT](https://www.waveshare.com/product/iot-communication/sim7600g-h-4g-hat.htm)
- [Bangko Sentral ng Pilipinas exchange-rate reference](https://www.bsp.gov.ph/SitePages/Statistics/exchangerate.aspx)

## Future Upgrade Procurement

Do not include future items in the Phase 1 purchase total. Conditional later
procurement may include a weatherproof H.264-capable USB camera, additional
calibratable environmental sensors, a remote modem, upgraded power hardware,
and a Raspberry Pi 5 4GB with active cooling and a validated 5 V / 5 A-class
supply. Exact products and prices must be researched again at purchase time.
See [`FUTURE_UPGRADES.md`](FUTURE_UPGRADES.md).

## Receiving Checklist

Record supplier, order number, exact SKU/revision, datasheet URL, photo of both
sides, measured dimensions, connector type, and measured idle current. A selected
part becomes installed hardware only after this record and a bench test exist.
