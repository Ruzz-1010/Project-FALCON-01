# FALCON-01 Phase 1 Procurement Baseline

Status: budgetary prototype BOM, checked 2026-08-15. Prices are USD list prices
before tax, shipping, import fees, and Philippine reseller markup. Confirm stock,
revision, and electrical ratings before ordering.

## Sensors and Control

| Qty | Selected item | Budget | Procurement note |
| ---: | --- | ---: | --- |
| 1 | ESP32 DevKit / ESP-WROOM-32 | $10–20 | Match `esp32dev`; photograph exact pin labels |
| 1 | Adafruit BNO085, PID 4754 | $24.95 | Use SPI with INT/RST; add headers/cable |
| 1 | Blue Robotics Bar02 R2 | $80–90 | Select Bar02, JST-GH lead, bulkhead seal |
| 1 | Adafruit Ultimate GPS, PID 746 | $29.95 | UART; external antenna optional |
| 2 | Adafruit INA260, PID 4226 | $19.90 | Battery `0x40`, solar `0x41`; verify current range |
| 1 | Adafruit ADS1115, PID 1085 | $14.95 | Wind vane A0; 3.3 V divider |
| 1 | MCP9808 breakout | $10–15 | Enclosure temperature, `0x18` |
| 1 | SparkFun Weather Meter SEN-15901 | $79.95 | Prototype only; salt-exposure maintenance required |
| 1 | Sealed DS18B20 probe | $8–15 | Optional water temperature; verify genuine waterproof build |
| 1 | Orange Pi Zero 3 4 GB | $35–60 | Buy from an authorized listing; include storage/heatsink |

Known sensor/control subtotal is approximately **$313–$341**, excluding power,
connectors, enclosure, shipping, and optional antenna.

## Power and Installation Allowance

| Qty | Item | Budget | Release condition |
| ---: | --- | ---: | --- |
| 1 | 12.8 V 20 Ah LiFePO4 with BMS | $80–160 | Supplier datasheet and charge limits recorded |
| 1 | 60 W panel (80 W preferred) | $55–120 | Voc/Isc compatible with MPPT |
| 1 | LiFePO4 MPPT controller | $50–130 | Genuine MPPT; programmable LiFePO4 profile |
| 1 | 5 V / 3 A synchronous buck | $15–40 | Orange Pi brownout/ripple/thermal test |
| 1 | Separate 5 V / 2 A buck | $10–30 | ESP32/sensor branch test |
| lot | Fuses, disconnect, terminals, glands, marine wire | $70–160 | Rated schedule and ingress review |

Planning total: **$593–$981** before enclosure fabrication, freight, taxes, and
spares. Do not purchase every item until the exact supplier links and physical
board revisions are reviewed together.

## Primary Sources

- [Adafruit BNO085 product](https://www.adafruit.com/product/4754)
- [Blue Robotics Bar02/Bar30 product](https://bluerobotics.com/store/sensors-cameras/sensors/bar-depth-pressure-sensor/)
- [Adafruit INA260 product](https://www.adafruit.com/product/4226)
- [Adafruit ADS1115 product](https://www.adafruit.com/product/1085)
- [Adafruit Ultimate GPS product](https://www.adafruit.com/product/746)
- [SparkFun Weather Meter Kit](https://www.sparkfun.com/weather-meter-kit.html)

## Receiving Checklist

Record supplier, order number, exact SKU/revision, datasheet URL, photo of both
sides, measured dimensions, connector type, and measured idle current. A selected
part becomes installed hardware only after this record and a bench test exist.
