# Adviser-Revised Pinout Register v6.1

Status: provisional bench allocation. Exact purchased modules and PCB revision must be verified before wiring or fabrication.

| Function | Provisional ESP32 interface | Note |
| --- | --- | --- |
| Shared I2C SDA/SCL | GPIO21 / GPIO22 | Bar02 and compatible 3.3 V I2C modules; verify addresses/pull-ups |
| GPS RX/TX | GPIO16 / GPIO17 | Cross TX/RX; verify GPS logic voltage |
| Wind speed | GPIO25 | Pulse input with appropriate pull-up/debounce |
| Water temperature | GPIO26 | DS18B20 OneWire with 4.7 kOhm pull-up |
| Wind direction | ADS1115 A0 | Calibrated 3.3 V divider; ADS1115 on I2C |
| Tamper/vibration | GPIO32 | Exact module and active level TBD |
| Enclosure switch | GPIO33 | Debounced digital input; active level TBD |
| Buzzer driver | GPIO27 | GPIO drives transistor/MOSFET, never an unverified load directly |
| Bench telemetry | ESP32 USB | Development laptop/Bay Station commissioning only |
| Deployed telemetry | LTE/cellular modem interface | Exact UART/USB interface and pinout TBD after modem approval |

Battery, solar, and enclosure-temperature interfaces remain subject to exact part selection and address/range review. Conductivity/salinity is excluded from the required Phase 1 pinout. The BNO085 SPI assignments in older revisions are released from the required Phase 1 design. Load cell/HX711 pins are not assigned.

Use 3.3 V logic, protected regulated power, common documented ground, external-connector transient protection, and test points for VBAT/5V/3V3/GND/UART/SDA/SCL. Do not connect raw battery voltage to ESP32 or modem signal pins. Freeze the LTE connector only after its datasheet, peak current, logic levels, and antenna requirements are approved.
