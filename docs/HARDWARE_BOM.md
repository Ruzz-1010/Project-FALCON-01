# FALCON-01 Phase 1 Procurement Baseline

Status: budgetary prototype BOM, checked 2026-08-15. Prices are shown in
Philippine pesos using an indicative rate of **PHP 61.71 per USD**. They are raw
list-price conversions before shipping, import fees, tax, and Philippine reseller
markup. Confirm the live exchange rate, stock, revision, and ratings before ordering.

## Sensors and Control

| Qty | Selected item | Budget | Procurement note |
| ---: | --- | ---: | --- |
| 1 | ESP32 DevKit / ESP-WROOM-32 | PHP 620–1,235 | Match `esp32dev`; photograph exact pin labels |
| 1 | Adafruit BNO085, PID 4754 | PHP 1,540 | Use SPI with INT/RST; add headers/cable |
| 1 | Blue Robotics Bar02 R2 | PHP 4,940–5,555 | Select Bar02, JST-GH lead, bulkhead seal |
| 1 | Adafruit Ultimate GPS, PID 746 | PHP 1,850 | UART; external antenna optional |
| 2 | Adafruit INA260, PID 4226 | PHP 1,230 | Battery `0x40`, solar `0x41`; verify current range |
| 1 | Adafruit ADS1115, PID 1085 | PHP 925 | Wind vane A0; 3.3 V divider |
| 1 | MCP9808 breakout | PHP 620–925 | Enclosure temperature, `0x18` |
| 1 | SparkFun Weather Meter SEN-15901 | PHP 4,935 | Prototype only; salt-exposure maintenance required |
| 1 | Sealed DS18B20 probe | PHP 495–925 | Optional water temperature; verify genuine waterproof build |
| 1 | Orange Pi Zero 3 4 GB | PHP 2,160–3,705 | Buy from an authorized listing; include storage/heatsink |

Known sensor/control subtotal is approximately **PHP 19,320–21,050**, excluding power,
connectors, enclosure, shipping, and optional antenna.

## Power and Installation Allowance

| Qty | Item | Budget | Release condition |
| ---: | --- | ---: | --- |
| 1 | 12.8 V 20 Ah LiFePO4 with BMS | PHP 4,940–9,875 | Supplier datasheet and charge limits recorded |
| 1 | 60 W panel (80 W preferred) | PHP 3,395–7,405 | Voc/Isc compatible with MPPT |
| 1 | LiFePO4 MPPT controller | PHP 3,085–8,025 | Genuine MPPT; programmable LiFePO4 profile |
| 1 | 5 V / 3 A synchronous buck | PHP 925–2,470 | Orange Pi brownout/ripple/thermal test |
| 1 | Separate 5 V / 2 A buck | PHP 620–1,850 | ESP32/sensor branch test |
| lot | Fuses, disconnect, terminals, glands, marine wire | PHP 4,320–9,875 | Rated schedule and ingress review |

Raw converted planning total: **PHP 36,600–60,550** before enclosure fabrication,
freight, taxes, and spares. A more practical landed budget is approximately
**PHP 42,000–79,000**, allowing 15–30% for shipping, import costs, local markup,
connectors, and spares. Do not purchase every item until the exact supplier links
and physical board revisions are reviewed together.

## Primary Sources

- [Adafruit BNO085 product](https://www.adafruit.com/product/4754)
- [Blue Robotics Bar02/Bar30 product](https://bluerobotics.com/store/sensors-cameras/sensors/bar-depth-pressure-sensor/)
- [Adafruit INA260 product](https://www.adafruit.com/product/4226)
- [Adafruit ADS1115 product](https://www.adafruit.com/product/1085)
- [Adafruit Ultimate GPS product](https://www.adafruit.com/product/746)
- [SparkFun Weather Meter Kit](https://www.sparkfun.com/weather-meter-kit.html)
- [Bangko Sentral ng Pilipinas exchange-rate reference](https://www.bsp.gov.ph/SitePages/Statistics/exchangerate.aspx)

## Receiving Checklist

Record supplier, order number, exact SKU/revision, datasheet URL, photo of both
sides, measured dimensions, connector type, and measured idle current. A selected
part becomes installed hardware only after this record and a bench test exist.
