#!/usr/bin/env python3
"""Generate the structured Project FALCON ESP32 sensor-carrier schematic."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ROOT_UUID = "8f84bda8-4a60-4fb6-9df1-43d0356dc759"
OUT = Path(__file__).with_name("FALCON_CARRIER.kicad_sch")
LIB_OUT = Path(__file__).with_name("FALCON.kicad_sym")


def uid(key: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"falcon-carrier/schematic-v1/{key}"))


def effects(hidden=False, size=1.27, bold=False) -> str:
    return f'(effects (font (size {size:g} {size:g})' + (' (bold yes)' if bold else '') + ')' + (' (hide yes)' if hidden else '') + ')'


@dataclass(frozen=True)
class Pin:
    number: str
    name: str
    net: str
    electrical: str = "passive"


@dataclass(frozen=True)
class Part:
    ref: str
    value: str
    pins: tuple[Pin, ...]
    x: float
    y: float
    footprint: str = ""
    description: str = "Project FALCON engineering component"


def P(number, name, net, electrical="passive") -> Pin:
    return Pin(str(number), name, net, electrical)


def symbol_definition(part: Part) -> str:
    height = max(7.62, (len(part.pins) - 1) * 2.54 + 5.08)
    pins = []
    for index, pin in enumerate(part.pins):
        pins.append(f'''      (pin {pin.electrical} line (at -10.16 {-index * 2.54:.2f} 0) (length 5.08)
        (name "{pin.name}" {effects()}) (number "{pin.number}" {effects()}))''')
    return f'''    (symbol "FALCON:{part.value}"
      (pin_names (offset 1.016))
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "{part.ref.rstrip('0123456789') or 'U'}" (at 0 5.08 0) {effects()})
      (property "Value" "{part.value}" (at 0 2.54 0) {effects()})
      (property "Footprint" "{part.footprint}" (at 0 0 0) {effects(True)})
      (property "Datasheet" "" (at 0 0 0) {effects(True)})
      (property "Description" "{part.description}" (at 0 0 0) {effects(True)})
      (symbol "{part.value}_1_1"
        (rectangle (start -5.08 2.54) (end 15.24 {-height + 2.54:.2f})
          (stroke (width 0.254) (type default)) (fill (type background)))
{chr(10).join(pins)}
      )
      (embedded_fonts no)
    )'''


def symbol_instance(part: Part) -> tuple[str, list[str]]:
    x, y = round(part.x / 1.27) * 1.27, round(part.y / 1.27) * 1.27
    entries, labels = [], []
    for index, pin in enumerate(part.pins):
        entries.append(f'    (pin "{pin.number}" (uuid "{uid(part.ref + "/pin/" + pin.number)}"))')
        labels.append(f'''  (label "{pin.net}" (at {x - 10.16:.2f} {y + index * 2.54:.2f} 0)
    {effects(size=1.0)} (uuid "{uid(part.ref + '/label/' + pin.number)}"))''')
    return f'''  (symbol
    (lib_id "FALCON:{part.value}") (at {x:.2f} {y:.2f} 0) (unit 1)
    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid(part.ref)}")
    (property "Reference" "{part.ref}" (at {x:.2f} {y - 5.08:.2f} 0) {effects(bold=True)})
    (property "Value" "{part.value}" (at {x:.2f} {y - 2.54:.2f} 0) {effects(size=1.0)})
    (property "Footprint" "{part.footprint}" (at {x:.2f} {y:.2f} 0) {effects(True)})
    (property "Datasheet" "" (at {x:.2f} {y:.2f} 0) {effects(True)})
    (property "Description" "{part.description}" (at {x:.2f} {y:.2f} 0) {effects(True)})
{chr(10).join(entries)}
    (instances (project "FALCON_CARRIER" (path "/{ROOT_UUID}" (reference "{part.ref}") (unit 1))))
  )''', labels


def frame(title, x1, y1, x2, y2) -> str:
    pts = f'(xy {x1} {y1}) (xy {x2} {y1}) (xy {x2} {y2}) (xy {x1} {y2}) (xy {x1} {y1})'
    return f'''  (polyline (pts {pts})
    (stroke (width 0.35) (type default)) (fill (type none)) (uuid "{uid('frame/' + title)}"))
  (text "{title}" (at {x1 + 3} {y1 + 4} 0) {effects(size=1.8, bold=True)}
    (uuid "{uid('title/' + title)}"))'''


def note(text, x, y, key) -> str:
    return f'  (text "{text}" (at {x} {y} 0) {effects(size=1.0)} (uuid "{uid("note/" + key)}"))'


R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
LED0603 = "LED_SMD:LED_0603_1608Metric"
TP = "TestPoint:TestPoint_Plated_Hole_D1.0mm"
HDR3 = "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical"
HDR4 = "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
HDR6 = "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"

PARTS = [
    # POWER MANAGEMENT. Solar charging stays external through a proper MPPT.
    Part("J14", "SOLAR_INPUT_TO_EXTERNAL_MPPT", (P(1, "SOLAR+", "SOLAR_RAW"), P(2, "SOLAR-", "GND")), 35, 35, "Connector_JST:JST_VH_B2P-VH-B_1x02_P3.96mm_Vertical", "Solar boundary only; never connect panel directly to battery"),
    Part("J15", "BATTERY_INPUT_12V8", (P(1, "+", "+VBAT_RAW"), P(2, "-", "GND")), 70, 35, "Connector_JST:JST_VH_B2P-VH-B_1x02_P3.96mm_Vertical"),
    Part("F1", "FUSE_3A_DC_TBD", (P(1, "IN", "+VBAT_RAW"), P(2, "OUT", "+VBAT_FUSED")), 103, 35, "Fuse:Fuse_1206_3216Metric", "Confirm fuse from measured load and conductor rating"),
    Part("D1", "SMBJ18A_TVS", (P(1, "K", "+VBAT_FUSED"), P(2, "A", "GND")), 133, 35, "Diode_SMD:D_SMA"),
    Part("Q3", "REVERSE_POLARITY_PFET_30V", (P(1, "S", "+VBAT_FUSED"), P(2, "G", "GND"), P(3, "D", "+VBAT")), 163, 35, "Package_TO_SOT_SMD:SOT-23", "Exact low-RDS(on) part requires thermal validation"),
    Part("SW1", "MAIN_POWER_SWITCH", (P(1, "IN", "+VBAT"), P(2, "OUT", "+VBAT_SW")), 195, 35, "Button_Switch_THT:SW_CW_G1_SPST"),
    Part("U7", "5V_2A_BUCK_MODULE", (P(1, "VIN", "+VBAT_SW", "power_in"), P(2, "GND", "GND", "power_in"), P(3, "VOUT", "+5V", "power_out"), P(4, "EN", "+VBAT_SW", "input")), 228, 35, HDR4, "Lock exact buck and footprint before fabrication"),
    Part("C3", "10UF_25V_INPUT", (P(1, "+", "+VBAT_SW"), P(2, "-", "GND")), 258, 35, C0603),
    Part("C4", "47UF_10V_OUTPUT", (P(1, "+", "+5V"), P(2, "-", "GND")), 285, 35, "Capacitor_SMD:C_1210_3225Metric"),
    Part("U1", "AP2112K_3V3", (P(1, "VIN", "+5V", "power_in"), P(2, "GND", "GND", "power_in"), P(3, "EN", "+5V", "input"), P(5, "VOUT", "+3V3", "power_out")), 315, 35, "Package_TO_SOT_SMD:SOT-23-5"),
    Part("C1", "1UF_LDO_IN", (P(1, "+", "+5V"), P(2, "-", "GND")), 345, 35, C0603),
    Part("C2", "1UF_LDO_OUT", (P(1, "+", "+3V3"), P(2, "-", "GND")), 372, 35, C0603),
    Part("D2", "5V_POWER_LED", (P(1, "A", "+5V"), P(2, "K", "LED5_K")), 35, 62, LED0603),
    Part("R9", "1K_LED5", (P(1, "1", "LED5_K"), P(2, "2", "GND")), 62, 62, R0603),
    Part("D3", "3V3_POWER_LED", (P(1, "A", "+3V3"), P(2, "K", "LED3_K")), 90, 62, LED0603),
    Part("R10", "1K_LED3", (P(1, "1", "LED3_K"), P(2, "2", "GND")), 118, 62, R0603),
    Part("J16", "USB_C_SERVICE_POWER", (P(1, "VBUS", "USB_VBUS"), P(2, "GND", "GND"), P(3, "CC1", "USB_CC1"), P(4, "CC2", "USB_CC2"), P(5, "D+_NC", "USB_DPLUS_NC"), P(6, "D-_NC", "USB_DMINUS_NC")), 153, 60, "Connector_USB:USB_C_Receptacle_USB2.0_16P", "Power-only; USB data intentionally isolated"),
    Part("R11", "5K1_CC1", (P(1, "1", "USB_CC1"), P(2, "2", "GND")), 188, 62, R0603),
    Part("R12", "5K1_CC2", (P(1, "1", "USB_CC2"), P(2, "2", "GND")), 215, 62, R0603),
    Part("F2", "USB_POLYFUSE_1A", (P(1, "IN", "USB_VBUS"), P(2, "OUT", "USB_5V_FUSED")), 244, 62, "Fuse:Fuse_1206_3216Metric"),
    Part("JP1", "USB_SERVICE_ENABLE", (P(1, "USB", "USB_5V_FUSED"), P(2, "RAIL", "+5V")), 275, 62, "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", "Fit only with battery buck isolated"),

    # ESP32 CONTROLLER. Official DevKitC V4 38-pin numbering is retained.
    Part("U2", "ESP32_DEVKITC_V4_WROOM32E", (
        P(3, "EN", "ESP_EN", "input"), P(5, "GPIO34", "FAN1_TACH", "input"), P(6, "GPIO35", "FAN2_TACH", "input"), P(7, "GPIO32", "LEAK_SIGNAL", "input"), P(8, "GPIO33", "FAN_PWM_GPIO", "output"),
        P(9, "GPIO25", "WIND_SPEED", "input"), P(10, "GPIO26", "WATER_TEMP", "bidirectional"), P(11, "GPIO27", "BNO_INT", "input"), P(12, "GPIO14", "BNO_RST", "output"), P(14, "GND", "GND", "power_in"),
        P(15, "GPIO13", "BNO_CS", "output"), P(19, "5V", "+5V", "power_in"), P(24, "GPIO2", "STATUS_LED", "output"), P(25, "GPIO0", "BOOT_GPIO0", "bidirectional"), P(26, "GPIO4", "EXP_GPIO4", "bidirectional"),
        P(27, "GPIO16/RX2", "GPS_TX", "input"), P(28, "GPIO17/TX2", "GPS_RX", "output"), P(30, "GPIO18", "BNO_SCK", "output"), P(31, "GPIO19", "BNO_MISO", "input"), P(32, "GND", "GND", "power_in"),
        P(33, "GPIO21", "I2C_SDA", "bidirectional"), P(34, "RX0", "UART_RX", "input"), P(35, "TX0", "UART_TX", "output"), P(36, "GPIO22", "I2C_SCL", "bidirectional"), P(37, "GPIO23", "BNO_MOSI", "output"), P(38, "GND", "GND", "power_in")),
        85, 92, "${KIPRJMOD}/vendor/Espressif.pretty/ESP32-DevKitC.kicad_mod", "Official ESP32-DevKitC V4 / WROOM-32E carrier"),
    Part("SW2", "RESET_BUTTON", (P(1, "EN", "ESP_EN"), P(2, "GND", "GND")), 140, 95, "Button_Switch_SMD:SW_SPST_TL3342"),
    Part("R13", "10K_EN_PULLUP", (P(1, "1", "+3V3"), P(2, "2", "ESP_EN")), 170, 95, R0603),
    Part("SW3", "BOOT_BUTTON", (P(1, "GPIO0", "BOOT_GPIO0"), P(2, "GND", "GND")), 200, 95, "Button_Switch_SMD:SW_SPST_TL3342"),
    Part("R14", "10K_BOOT_PULLUP", (P(1, "1", "+3V3"), P(2, "2", "BOOT_GPIO0")), 230, 95, R0603),
    Part("R15", "330R_STATUS", (P(1, "GPIO", "STATUS_LED"), P(2, "LED", "STATUS_LED_A")), 260, 95, R0603),
    Part("D4", "STATUS_LED", (P(1, "A", "STATUS_LED_A"), P(2, "K", "GND")), 290, 95, LED0603),
    Part("C5", "100NF_5V_DECOUPLING", (P(1, "+", "+5V"), P(2, "-", "GND")), 325, 95, C0603),
    Part("C6", "10UF_5V_BULK", (P(1, "+", "+5V"), P(2, "-", "GND")), 355, 95, "Capacitor_SMD:C_0805_2012Metric"),

    # SENSOR INTERFACES.
    Part("U3", "BNO085_IMU_SPI", (P(1, "3V3", "+3V3"), P(2, "GND", "GND"), P(3, "SCK", "BNO_SCK"), P(4, "MISO", "BNO_MISO"), P(5, "MOSI", "BNO_MOSI"), P(6, "CS", "BNO_CS"), P(7, "INT", "BNO_INT"), P(8, "RST", "BNO_RST")), 35, 162, HDR6),
    Part("J2", "PRESSURE_BAR02_I2C", (P(1, "3V3", "+3V3"), P(2, "SCL", "I2C_SCL"), P(3, "SDA", "I2C_SDA"), P(4, "GND", "GND")), 82, 162, HDR4),
    Part("J3", "GPS_UART_MODULE", (P(1, "3V3", "+3V3"), P(2, "GND", "GND"), P(3, "GPS_TX", "GPS_TX"), P(4, "GPS_RX", "GPS_RX")), 120, 162, HDR4),
    Part("J7", "WIND_SPEED_SENSOR", (P(1, "3V3", "+3V3"), P(2, "PULSE", "WIND_SPEED"), P(3, "GND", "GND")), 158, 162, HDR3),
    Part("U4", "WIND_DIRECTION_ADS1115", (P(1, "3V3", "+3V3"), P(2, "GND", "GND"), P(3, "SCL", "I2C_SCL"), P(4, "SDA", "I2C_SDA"), P(5, "A0", "WIND_DIR")), 195, 162, HDR6),
    Part("J8", "WIND_DIRECTION_SENSOR", (P(1, "3V3", "+3V3"), P(2, "ADC", "WIND_DIR"), P(3, "GND", "GND")), 235, 162, HDR3),
    Part("J9", "TEMPERATURE_DS18B20", (P(1, "3V3", "+3V3"), P(2, "DATA", "WATER_TEMP"), P(3, "GND", "GND")), 275, 162, HDR3),
    Part("J4", "BATTERY_MONITOR_INA260", (P(1, "3V3", "+3V3"), P(2, "GND", "GND"), P(3, "SCL", "I2C_SCL"), P(4, "SDA", "I2C_SDA")), 315, 162, HDR4),
    Part("J5", "SOLAR_MONITOR_INA260", (P(1, "3V3", "+3V3"), P(2, "GND", "GND"), P(3, "SCL", "I2C_SCL"), P(4, "SDA", "I2C_SDA")), 355, 162, HDR4),
    Part("R1", "4K7_I2C_SDA_PULLUP", (P(1, "3V3", "+3V3"), P(2, "SDA", "I2C_SDA")), 45, 208, R0603),
    Part("R2", "4K7_I2C_SCL_PULLUP", (P(1, "3V3", "+3V3"), P(2, "SCL", "I2C_SCL")), 80, 208, R0603),
    Part("R3", "10K_WIND_PULLUP", (P(1, "3V3", "+3V3"), P(2, "PULSE", "WIND_SPEED")), 115, 208, R0603),
    Part("R4", "4K7_ONEWIRE_PULLUP", (P(1, "3V3", "+3V3"), P(2, "DATA", "WATER_TEMP")), 150, 208, R0603),
    Part("J6", "ENCLOSURE_TEMP_MCP9808", (P(1, "3V3", "+3V3"), P(2, "SCL", "I2C_SCL"), P(3, "SDA", "I2C_SDA"), P(4, "GND", "GND")), 195, 208, HDR4),
    Part("J10", "LEAK_SENSOR_INTERFACE", (P(1, "3V3", "+3V3"), P(2, "SIGNAL", "LEAK_SIGNAL"), P(3, "GND", "GND")), 235, 208, HDR3),

    # COMMUNICATION. J20 is the only external-edge-computer representation.
    Part("J20", "EXTERNAL_EDGE_UART", (P(1, "5V_SERVICE", "+5V"), P(2, "GND", "GND"), P(3, "ESP_TX", "UART_TX"), P(4, "ESP_RX", "UART_RX")), 40, 242, HDR4, "UART to a separately powered external edge computer; connector only"),
    Part("J21", "ESP32_PROGRAM_HEADER", (P(1, "3V3", "+3V3"), P(2, "GND", "GND"), P(3, "TX0", "UART_TX"), P(4, "RX0", "UART_RX"), P(5, "EN", "ESP_EN"), P(6, "BOOT", "BOOT_GPIO0")), 85, 242, HDR6),
    Part("J22", "FUTURE_I2C_HEADER", (P(1, "3V3", "+3V3"), P(2, "GND", "GND"), P(3, "SDA", "I2C_SDA"), P(4, "SCL", "I2C_SCL")), 130, 242, HDR4),
    Part("J23", "EXPANSION_HEADER", (P(1, "3V3", "+3V3"), P(2, "5V", "+5V"), P(3, "GND", "GND"), P(4, "GPIO4", "EXP_GPIO4"), P(5, "SDA", "I2C_SDA"), P(6, "SCL", "I2C_SCL")), 175, 242, HDR6),
]

for index, net in enumerate(("+3V3", "+5V", "+VBAT", "UART_TX", "UART_RX", "I2C_SDA", "I2C_SCL", "GND"), 1):
    value = "TESTPOINT_" + net.replace("+", "P").replace("I2C_", "")
    PARTS.append(Part(f"TP{index}", value, (P(1, net, net),), 230 + (index - 1) * 22, 244, TP))

definitions, instances, labels, seen = [], [], [], set()
for part in PARTS:
    if part.value not in seen:
        definitions.append(symbol_definition(part))
        seen.add(part.value)
    instance, local_labels = symbol_instance(part)
    instances.append(instance)
    labels.extend(local_labels)

drawings = [
    frame("1. POWER MANAGEMENT", 15, 18, 405, 80),
    frame("2. ESP32 CONTROLLER", 15, 84, 405, 150),
    frame("3. SENSOR INTERFACES", 15, 154, 405, 226),
    frame("4. COMMUNICATION", 15, 230, 205, 281),
    frame("5. DEBUG & EXPANSION", 210, 230, 405, 281),
    note("POWER → ESP32 → SENSORS → COMMUNICATION", 270, 14, "flow"),
    note("SOLAR PANEL → EXTERNAL LiFePO4 MPPT → BATTERY. NEVER CONNECT PANEL DIRECTLY TO BATTERY.", 20, 76, "solar"),
    note("USB-C IS SERVICE POWER ONLY. ISOLATE BATTERY BUCK BEFORE FITTING JP1.", 285, 76, "usb"),
    note("EXTERNAL EDGE COMPUTER IS SEPARATELY POWERED; UART HEADER J20 ONLY; NOT ON THIS PCB", 20, 278, "edge"),
]

document = f'''(kicad_sch
  (version 20250114) (generator "eeschema") (generator_version "10.0")
  (uuid "{ROOT_UUID}") (paper "A3")
  (title_block
    (title "PROJECT FALCON — ESP32 SENSOR CARRIER") (date "2026-08-21") (rev "SCHEMATIC V1.0")
    (company "PROJECT FALCON-01")
    (comment 1 "FUNCTIONAL-BLOCK ENGINEERING RELEASE CANDIDATE")
    (comment 2 "Final buck/protection parts, connector fit, ERC and DRC require release sign-off"))
  (lib_symbols
{chr(10).join(definitions)}
  )
{chr(10).join(drawings)}
{chr(10).join(labels)}
{chr(10).join(instances)}
  (sheet_instances (path "/" (page "1")))
  (embedded_fonts no)
)
'''
OUT.write_text(document, encoding="utf-8")
LIB_OUT.write_text(f'''(kicad_symbol_lib
  (version 20231120) (generator "kicad_symbol_editor")
{chr(10).join(definitions)}
)
''', encoding="utf-8")
print(f"Generated {OUT.name}: {len(PARTS)} symbols, {len(seen)} library definitions")
print(f"Generated {LIB_OUT.name}")
