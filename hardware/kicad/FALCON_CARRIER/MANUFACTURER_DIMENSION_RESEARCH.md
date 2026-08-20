# Manufacturer Dimension Research

Status: **CAD reference captured; physical receiving checks still required**  
Research date: 2026-08-20

This register separates manufacturer evidence from physical validation. Official
CAD can define the intended footprint, but it cannot prove that a reseller sent
the same revision, that headers were soldered straight, or that installed cable
and enclosure clearances are adequate.

| Ref. | Locked/candidate item | Manufacturer evidence | CAD/reference result | Remaining physical gate |
| --- | --- | --- | --- | --- |
| U2 | Espressif ESP32-DevKitC V4, WROOM-32E | [Official DevKitC V4 guide and dimension drawing](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) | Board 27.9 × 48.2 mm; 54.4 mm maximum including USB; 38 pins at 2.54 mm pitch; 25.4 mm row spacing | Delivered WROOM-32E revision, USB overhang, antenna end, and 1:1 header fit |
| U3 | Adafruit BNO085 PID 4754 | [Product specification](https://www.adafruit.com/product/4754) and [official Eagle CAD](https://github.com/adafruit/Adafruit-BNO08x-PCB) | CAD outline 25.4 × 22.86 mm; published height 4.6 mm; two 6-pin 2.54 mm rows; four 2.5 mm holes at (2.54,2.54), (22.86,2.54), (2.54,20.32), and (22.86,20.32) mm | Rev marking, axis/orientation, header height, STEMMA clearance, and 1:1 check |
| J2 | Blue Robotics Bar02 R2, BR-100891 | [Official product specification and R2 CAD](https://bluerobotics.com/store/sensors-cameras/sensors/bar-depth-pressure-sensor/) | CAD envelope is approximately 16 mm diameter × 307.6 mm including lead; M10×1.5 bulkhead; 10.0–10.2 mm clearance port; 4-position 1.25 mm-pitch JST-GH | Select board-side JST-GH orientation and reserve cable bend/strain-relief space |
| J3 | Adafruit Ultimate GPS PID 746 | [Product guide](https://learn.adafruit.com/adafruit-ultimate-gps) and [official Eagle CAD](https://github.com/adafruit/Adafruit-Ultimate-GPS) | CAD outline 25.4 × 34.29 mm; published assembly 25.5 × 35 × 6.5 mm; 9-pin 2.54 mm header; two 2.5 mm holes at (2.54,31.75) and (22.86,31.75) mm | Confirm PA1616S/current revision, antenna sky view, u.FL clearance, header height, and 1:1 check |
| J4/J5 | Adafruit INA260 PID 4226 | [Product specification](https://www.adafruit.com/product/4226) and [official Eagle CAD](https://github.com/adafruit/Adafruit-INA260-PCB) | 22.86 × 22.86 mm PCB; 8-pin 2.54 mm header; two 2.5 mm holes at (2.54,20.32) and (20.32,20.32) mm; 5.08 mm load terminal pitch | Measure pre-soldered terminal height and cable exit; verify J5 address `0x41`; high-current path remains off-carrier |
| U4 | Adafruit ADS1115 PID 1085, STEMMA QT revision | [Product specification](https://www.adafruit.com/product/1085) and [official Eagle CAD](https://github.com/adafruit/ADS1X15-Breakout-Board-PCBs) | 25.4 × 17.78 × 4.6 mm; two 6-pin 2.54 mm rows; four 2.5 mm holes at (2.54,2.54), (22.86,2.54), (2.54,15.24), and (22.86,15.24) mm | Confirm June-2022-or-newer shape, A0 access, header height, and 1:1 check |
| J6 | Adafruit MCP9808 PID 1782 candidate | [Official product specification](https://www.adafruit.com/product/1782) | Published 21 × 13 × 2 mm PCB/assembly baseline; 8-pin original header version | BOM did not lock an exact SKU; confirm PID 1782 versus STEMMA version before footprint creation |

## Critical finding

The Blue Robotics Bar02 R2 cable order is **1 Vin/red, 2 SCL/green,
3 SDA/white, 4 GND/black**. The earlier logical connector register placed GND
on pin 2. The schematic generator and connector register were corrected to the
manufacturer order during this research. Plug-view orientation must still be
checked on the received mating connector before applying power.

## Items that cannot be dimensioned yet

J1 and J7–J12 connector bodies, U1 regulator, U5 fan driver, leak detector,
sealed DS18B20 probe, fan, and H1–H4 enclosure coordinates remain undefined
because the project has not selected exact manufacturer part numbers. Their
footprints must remain provisional; dimensions from generic marketplace photos
are not acceptable engineering evidence.
