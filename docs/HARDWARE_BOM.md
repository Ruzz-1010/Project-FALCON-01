# FALCON-01 Phase 1 Procurement Baseline

> This is a planning BOM, not a fabrication release. Reconfirm quantities, dimensions, connector variants, cable lengths, brackets, enclosure parts, ballast, and solar mounting hardware after the replacement prototype is approved.

Status: budgetary Bay Station baseline, revised 2026-08-30. Prices are shown in
Philippine pesos using an indicative rate of **PHP 61.71 per USD**. They are raw
list-price conversions before shipping, import fees, tax, and Philippine reseller
markup. Confirm the live exchange rate, stock, revision, and ratings before ordering.

## Primary Sensors and Control

| Qty | Selected item | Budget | Procurement note |
| ---: | --- | ---: | --- |
| 1 | Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E, 38-pin | PHP 620–1,235 | Exact carrier reference; do not substitute WROVER because GPIO16/17 are required |
| 1 | Blue Robotics Bar02 R2 | PHP 4,940–5,555 | Select Bar02, JST-GH lead, bulkhead seal |
| 1 | Adafruit ADS1115, PID 1085 | PHP 925 | Wind vane direction input; 3.3 V divider |
| 1 | SparkFun Weather Meter SEN-15901 | PHP 4,935 | Prototype only; salt-exposure maintenance required |

## Supporting Telemetry and Control

These items support operation, power validation, and security. They are not additional project sensors or primary monitoring objectives.

| Qty | Selected item | Budget | Procurement note |
| ---: | --- | ---: | --- |
| 1 | Adafruit Ultimate GPS, PID 746 | PHP 1,850 | Supporting position/time/geofence telemetry; external antenna optional |
| 2 | Adafruit INA260, PID 4226 | PHP 1,230 | Supporting battery/solar power telemetry; verify current range |
| 0–1 | Adafruit MCP9808, PID 1782 | PHP 925 | Optional enclosure diagnostic only |
| 0–1 | Adafruit magnetic contact switch, PID 375 | PHP 100–500 | Optional enclosure security input |
| 0–1 | Buzzer and driver/protection | PHP 100–500 | Optional local alert output |
| 1 | Bay Station SIM/4G/5G modem/router + antenna/SIM | TBD; separate shore budget | Bay Station Internet backhaul for cloud upload and remote access; freeze after site coverage, data-plan, interface, antenna and reconnect tests |
| 1 | LoRa buoy radio module + barangay-hall LoRa gateway/receiver and antennas | TBD | Required target telemetry path; requires legal regional band selection, elevated shore placement, clear-path/range testing, and separate power/enclosure review |
| 1 | Shore Bay Station mini PC | TBD; separate shore budget | Facility powered; exact model selected from measured database/dashboard/AI workload; never installed on buoy |
| 0–1 | Enclosure fan/auxiliary cooling | TBD after thermal test | Include only if the buoy electronics enclosure demonstrates a measured need |

The previous subtotal is obsolete because adviser-approved security parts remain TBD. Recalculate the procurement total only after exact models and current supplier quotations are verified. It excludes fans,
power, connectors, enclosure, shipping, and optional antenna.

## Power and Installation Allowance

| Qty | Item | Budget | Release condition |
| ---: | --- | ---: | --- |
| 1 | 12.8 V 20 Ah LiFePO4 with BMS | PHP 4,940–9,875 | Supplier datasheet and charge limits recorded |
| 1 | 40 W or 60 W panel candidate | PHP 3,395–7,405 | Final rating follows measured buoy-only load; verify Voc/Isc with MPPT |
| 1 | LiFePO4 MPPT controller | PHP 3,085–8,025 | Genuine MPPT; programmable LiFePO4 profile |
| 1 | LoRa buoy radio regulated branch | TBD | Size from selected radio transmit peaks and brownout test; shore gateway is budgeted separately |
| 1 | Bay Station SIM/4G/5G backhaul branch | TBD | Separate shore power budget; size from selected modem/router registration and transmit peaks |
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

The previous total is withdrawn because the LoRa buoy link, Bay Station Internet backhaul, security inputs, final power branches, and enclosure needs are unresolved. Recalculate the buoy and shore budgets separately after exact supplier quotations and measured power requirements exist.

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
