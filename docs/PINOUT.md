# Adviser-Revised Pinout Register v6.2

Status: provisional bench allocation. Exact purchased modules and PCB revision must be verified before wiring or fabrication.

| Function | Provisional ESP32 interface | Note |
| --- | --- | --- |
| Shared I2C SDA/SCL | GPIO21 / GPIO22 | ADS1115 loop receiver plus approved 3.3 V I2C modules; verify addresses/pull-ups |
| Pressure loop input | ADS1115 input, final channel TBD | HPT604 4–20 mA through protected 150 ohm 0.1% shunt; never connect loop voltage directly to ESP32 |
| GPS RX/TX | GPIO16 / GPIO17 | Cross TX/RX; verify GPS logic voltage |
| Wind speed | GPIO25 | Pulse input with appropriate pull-up/debounce |
| Water temperature | GPIO26 | DS18B20 OneWire with 4.7 kOhm pull-up |
| Wind direction | ADS1115 A0 | Calibrated 3.3 V divider; ADS1115 on I2C |
| Tamper/vibration | GPIO32 | Exact module and active level TBD |
| Enclosure switch | GPIO33 | Debounced digital input; active level TBD |
| Buzzer driver | GPIO27 | GPIO drives transistor/MOSFET, never an unverified load directly |
| Bench telemetry | ESP32 USB | Development laptop/Bay Station commissioning only |
| Deployed telemetry | LoRa buoy radio interface | SPI/UART and interrupt pins TBD after regional module approval; requires barangay-hall gateway |
| Bay Station Internet | SIM/4G/5G modem/router | Installed at the barangay-hall Bay Station; not part of buoy pinout |

Battery, solar, and enclosure-temperature interfaces remain subject to exact part selection and address/range review. Conductivity/salinity is excluded from the required Phase 1 pinout. The BNO085 SPI assignments in older revisions are released from the required Phase 1 design. Load cell/HX711 pins are not assigned.

The Bar02 I2C allocation is retained only in historical bench material. Freeze the ADS1115 channel, grounding, gain, RC filter, TVS/clamps, and connector only after the HPT604 order code and revised schematic are approved.

Use 3.3 V logic, protected regulated power, common documented ground, external-connector transient protection, and test points for VBAT/5V/3V3/GND/UART/SDA/SCL. Do not connect raw battery voltage to ESP32 or radio signal pins. Freeze the LoRa connector only after its datasheet, regional frequency approval, peak current, logic levels, and antenna requirements are approved. The Bay Station SIM/4G/5G interface is documented separately because it is not installed on the buoy.
