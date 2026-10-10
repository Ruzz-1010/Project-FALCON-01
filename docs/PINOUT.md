# Adviser-Revised Pinout Register v6.1


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Status: provisional bench allocation. Exact purchased modules and PCB revision must be verified before wiring or fabrication.

| Function | Provisional ESP32 interface | Note |
| --- | --- | --- |
| Pressure ADC SDA/SCL | GPIO21 / GPIO22 | ADS1115 for protected 4–20 mA or analog pressure interface; verify address/pull-ups |
| GPS RX/TX | GPIO16 / GPIO17 | Cross TX/RX; verify GPS logic voltage |
| Wind speed | GPIO25 | Pulse input with appropriate pull-up/debounce |
| Optional water temperature | GPIO26 | DS18B20 OneWire with 4.7 kOhm pull-up |
| Wind direction | ADS1115 A0 | Calibrated 3.3 V divider; ADS1115 on I2C |
| Tamper/vibration | GPIO32 | Exact module and active level TBD |
| Enclosure switch | GPIO33 | Debounced digital input; active level TBD |
| Buzzer driver | GPIO27 | GPIO drives transistor/MOSFET, never an unverified load directly |
| Bench telemetry | ESP32 USB | Development laptop/Bay Station commissioning only |
| Deployed telemetry | 4G/LTE modem UART | UART and modem power-control pins TBD after exact module, antenna, and peak-current approval |

Battery, solar, and enclosure-temperature interfaces remain subject to exact part selection and address/range review. Conductivity/salinity is excluded from the required Phase 1 pinout. The BNO085 SPI assignments in older revisions are released from the required Phase 1 design. Load cell/HX711 pins are not assigned.

Use 3.3 V logic, protected regulated power, common documented ground, external-connector transient protection, and test points for VBAT/5V/3V3/GND/UART/SDA/SCL. Do not connect raw battery voltage to ESP32, ADC, or modem signal pins. Freeze the pressure connector and LTE modem branch only after the exact datasheets, peak current, logic levels, antenna requirements, and sealing plan are approved.
