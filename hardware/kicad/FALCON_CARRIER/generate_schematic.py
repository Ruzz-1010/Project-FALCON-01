#!/usr/bin/env python3
"""Generate the reviewed FALCON-01 carrier schematic draft for KiCad 10."""

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5


ROOT_UUID = "8f84bda8-4a60-4fb6-9df1-43d0356dc759"
OUT = Path(__file__).with_name("FALCON_CARRIER.kicad_sch")
LIB_OUT = Path(__file__).with_name("FALCON.kicad_sym")


def uid(key: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"falcon-carrier/{key}"))


def effects(hidden: bool = False) -> str:
    return '(effects (font (size 1.27 1.27))' + (' (hide yes)' if hidden else '') + ')'


def symbol_definition(name: str, pins: list[tuple[str, str]]) -> str:
    height = max(7.62, (len(pins) - 1) * 2.54 + 5.08)
    top = 2.54
    bottom = top - height
    pin_defs = []
    for index, (number, pin_name) in enumerate(pins):
        y = -index * 2.54
        pin_defs.append(
            f'''      (pin passive line (at -10.16 {y:.2f} 0) (length 5.08)
        (name "{pin_name}" {effects()})
        (number "{number}" {effects()}))'''
        )
    return f'''    (symbol "FALCON:{name}"
      (pin_names (offset 1.016) (hide yes))
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0) {effects()})
      (property "Value" "{name}" (at 0 2.54 0) {effects()})
      (property "Footprint" "" (at 0 0 0) {effects(True)})
      (property "Datasheet" "" (at 0 0 0) {effects(True)})
      (property "Description" "FALCON carrier placeholder; verify purchased revision" (at 0 0 0) {effects(True)})
      (symbol "{name}_1_1"
        (rectangle (start -5.08 {top:.2f}) (end 15.24 {bottom:.2f})
          (stroke (width 0.254) (type default)) (fill (type background)))
{chr(10).join(pin_defs)}
      )
      (embedded_fonts no)
    )'''


def symbol_instance(ref: str, name: str, pins: list[tuple[str, str]], x: float, y: float) -> tuple[str, list[str]]:
    pin_entries = []
    labels = []
    for index, (number, net) in enumerate(pins):
        pin_entries.append(f'    (pin "{number}" (uuid "{uid(ref + "/pin/" + number)}"))')
        # KiCad's schematic Y axis increases downward for an unrotated symbol.
        py = y + index * 2.54
        labels.append(
            f'''  (label "{net}" (at {x - 10.16:.2f} {py:.2f} 0)
    {effects()} (uuid "{uid(ref + "/label/" + number)}"))'''
        )
    instance = f'''  (symbol
    (lib_id "FALCON:{name}") (at {x:.2f} {y:.2f} 0) (unit 1)
    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid(ref)}")
    (property "Reference" "{ref}" (at {x:.2f} {y + 5.08:.2f} 0) {effects()})
    (property "Value" "{name}" (at {x:.2f} {y + 2.54:.2f} 0) {effects()})
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0) {effects(True)})
    (property "Datasheet" "" (at {x:.2f} {y:.2f} 0) {effects(True)})
    (property "Description" "FALCON carrier placeholder; footprint TBD" (at {x:.2f} {y:.2f} 0) {effects(True)})
{chr(10).join(pin_entries)}
    (instances (project "FALCON_CARRIER"
      (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))
  )'''
    return instance, labels


MODULES = [
    ("J1", "POWER_INPUT", [("1", "+5V_PROTECTED"), ("2", "GND")], 55, 35),
    ("U1", "REGULATOR_3V3_TBD", [("1", "+5V_PROTECTED"), ("2", "GND"), ("3", "+3V3_SENSOR")], 100, 35),
    ("U2", "ESP32_DEVKIT_INTERFACE", [
        ("1", "+5V_PROTECTED"), ("2", "+3V3_SENSOR"), ("3", "GND"),
        ("4", "I2C_SDA"), ("5", "I2C_SCL"), ("6", "BNO_SCK"),
        ("7", "BNO_MISO"), ("8", "BNO_MOSI"), ("9", "BNO_CS"),
        ("10", "BNO_INT"), ("11", "BNO_RST"), ("12", "GPS_TX"),
        ("13", "GPS_RX"), ("14", "WIND_PULSE"), ("15", "WATER_TEMP"),
        ("16", "LEAK_SIGNAL"), ("17", "FAN_PWM")], 155, 50),
    ("U3", "BNO085_SPI", [
        ("1", "+3V3_SENSOR"), ("2", "GND"), ("3", "BNO_SCK"),
        ("4", "BNO_MISO"), ("5", "BNO_MOSI"), ("6", "BNO_CS"),
        ("7", "BNO_INT"), ("8", "BNO_RST"), ("9", "+3V3_SENSOR"),
        ("10", "+3V3_SENSOR")], 220, 45),
    ("J2", "BAR02_I2C", [("1", "+3V3_SENSOR"), ("2", "GND"), ("3", "I2C_SCL"), ("4", "I2C_SDA")], 55, 75),
    ("J3", "GPS_UART", [("1", "+3V3_SENSOR"), ("2", "GND"), ("3", "GPS_TX"), ("4", "GPS_RX")], 55, 105),
    ("J4", "INA260_BAT_LOGIC", [("1", "+3V3_SENSOR"), ("2", "GND"), ("3", "I2C_SCL"), ("4", "I2C_SDA")], 100, 75),
    ("J5", "INA260_SOLAR_0X41", [("1", "+3V3_SENSOR"), ("2", "GND"), ("3", "I2C_SCL"), ("4", "I2C_SDA")], 100, 105),
    ("J6", "MCP9808_0X18", [("1", "+3V3_SENSOR"), ("2", "GND"), ("3", "I2C_SCL"), ("4", "I2C_SDA")], 55, 135),
    ("U4", "ADS1115_0X48", [("1", "+3V3_SENSOR"), ("2", "GND"), ("3", "I2C_SCL"), ("4", "I2C_SDA"), ("5", "WIND_VANE")], 100, 135),
    ("J7", "ANEMOMETER", [("1", "+3V3_SENSOR"), ("2", "WIND_PULSE"), ("3", "GND")], 55, 165),
    ("J8", "WIND_VANE", [("1", "+3V3_SENSOR"), ("2", "WIND_VANE"), ("3", "GND")], 100, 165),
    ("J9", "DS18B20_OPTION", [("1", "+3V3_SENSOR"), ("2", "WATER_TEMP"), ("3", "GND")], 145, 145),
    ("J10", "LEAK_SENSOR_TBD", [("1", "+3V3_SENSOR"), ("2", "LEAK_SIGNAL"), ("3", "GND")], 190, 145),
    ("U5", "FAN_DRIVER_TBD", [("1", "+5V_PROTECTED"), ("2", "GND"), ("3", "FAN_PWM"), ("4", "FAN_SWITCHED")], 235, 145),
    ("J11", "FAN_TBD", [("1", "+5V_PROTECTED"), ("2", "FAN_SWITCHED")], 235, 175),
    ("J12", "SERVICE_I2C", [("1", "+3V3_SENSOR"), ("2", "GND"), ("3", "I2C_SCL"), ("4", "I2C_SDA")], 190, 175),
    ("R1", "PULLUP_10K", [("1", "+3V3_SENSOR"), ("2", "WIND_PULSE")], 145, 185),
    ("R2", "PULLUP_4K7", [("1", "+3V3_SENSOR"), ("2", "WATER_TEMP")], 190, 205),
]


definitions = []
seen = set()
instances = []
labels = []
for ref, name, pins, x, y in MODULES:
    # Place every symbol and pin endpoint on KiCad's 50 mil (1.27 mm) grid.
    x = round(x / 2.54) * 2.54
    y = round(y / 2.54) * 2.54
    if name not in seen:
        definitions.append(symbol_definition(name, pins))
        seen.add(name)
    instance, instance_labels = symbol_instance(ref, name, pins, x, y)
    instances.append(instance)
    labels.extend(instance_labels)

document = f'''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "10.0")
  (uuid "{ROOT_UUID}")
  (paper "A3")
  (title_block
    (title "FALCON-01 LOW-VOLTAGE CARRIER")
    (date "2026-08-20")
    (rev "SCHEMATIC V0.1")
    (company "PROJECT FALCON-01")
    (comment 1 "NOT APPROVED FOR FABRICATION")
    (comment 2 "Named-net module schematic; footprints and protection values require physical validation"))
  (lib_symbols
{chr(10).join(definitions)}
  )
{chr(10).join(labels)}
{chr(10).join(instances)}
  (sheet_instances (path "/" (page "1")))
  (embedded_fonts no)
)
'''

OUT.write_text(document, encoding="utf-8")
library = f'''(kicad_symbol_lib
  (version 20231120)
  (generator "kicad_symbol_editor")
{chr(10).join(definitions)}
)
'''
LIB_OUT.write_text(library, encoding="utf-8")
print(f"Generated {OUT}")
print(f"Generated {LIB_OUT}")
