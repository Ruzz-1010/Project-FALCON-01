#!/usr/bin/env python3
"""Generate the FALCON-01 illustrated wiring reference sheet."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/blueprints/FALCON-BP-007-illustrated-wiring-diagram.svg"


def text(x,y,s,cls="txt",anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{escape(str(s))}</text>'


def device(x,y,w,h,title,ref,art):
    return (f'<g transform="translate({x} {y})"><path d="M0 12L12 0H{w}V{h}H0Z" class="device"/>'
            f'{text(w/2,20,title,"devtitle","middle")}{text(14,40,ref,"ref")}{art}</g>')


def drawing():
    W,H=1800,1200
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '''<defs><style>
svg{background:#f8fafb;shape-rendering:geometricPrecision}path,line,polyline,polygon,rect,circle,ellipse{vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round}.sheet{fill:#f8fafb;stroke:#18394d;stroke-width:2}.panel{fill:none;stroke:#31556a;stroke-width:1.2}.device{fill:#fff;stroke:#24485d;stroke-width:1.4}.detail{fill:none;stroke:#24485d;stroke-width:1.1}.fine{fill:none;stroke:#607b8a;stroke-width:.75}.pin{fill:#fff;stroke:#24485d;stroke-width:1}.pwr{fill:none;stroke:#a16207;stroke-width:2}.i2c{fill:none;stroke:#2563eb;stroke-width:1.7}.uart{fill:none;stroke:#7c3aed;stroke-width:1.7}.gpio{fill:none;stroke:#0f766e;stroke-width:1.7}.gnd{fill:none;stroke:#374151;stroke-width:2}.radio{fill:none;stroke:#be123c;stroke-width:1.7;stroke-dasharray:7 4}.title{font:700 25px Arial;fill:#102f42}.subtitle{font:600 10px Arial;letter-spacing:.7px;fill:#526b79}.head{font:700 13px Arial;fill:#17394d}.devtitle{font:700 8px Arial;fill:#17394d}.ref{font:700 8px Consolas;fill:#8b1e3f}.txt{font:7.5px Arial;fill:#304c5c}.small{font:6.5px Arial;fill:#536b78}.net{font:700 7px Consolas;fill:#17394d}.warn{font:700 8.5px Arial;fill:#a61b3c}.num{font:700 8px Arial;fill:#fff}.call{fill:#17394d;stroke:none}
</style><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#31556a"/></marker></defs>''',
       '<rect x="18" y="18" width="1764" height="1164" class="sheet"/>',
       text(45,58,"PROJECT FALCON-01 — ILLUSTRATED ELECTRONICS WIRING DIAGRAM","title"),
       text(45,81,"ACTUAL-PART DRAWING STYLE · ADVISER-ALIGNED PHASE 1 BASELINE · POWER / SENSOR / TELEMETRY INTERFACES","subtitle"),
       '<rect x="1450" y="38" width="285" height="46" class="panel"/>',text(1592,66,"REFERENCE — VERIFY BEFORE WIRING","warn","middle")]

    # Sensor drawings: recognizable board/mechanical forms.
    panel_specs=[(40,110,420,770,"A — FIELD SENSORS"),(480,110,650,770,"B — ESP32 CONTROL & SIGNAL WIRING"),(1150,110,610,420,"C — POWER & HEALTH MONITORING"),(1150,550,610,330,"D — TELEMETRY / SHORE LINK")]
    for x,y,w,h,t in panel_specs:
        s += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="panel"/>',text(x+14,y+25,t,"head")]

    # Bar02: JST-GH board, sensing can and pressure port.
    art='''<path d="M18 48H155V128H18Z" class="detail"/><path d="M38 62h45v24H38m70-2a21 21 0 1 0 0-1" class="detail"/><circle cx="108" cy="83" r="10" class="fine"/><path d="M98 104h20v23H98M31 128v17m14-17v17m14-17v17m14-17v17" class="fine"/>'''
    s.append(device(58,150,185,165,"BLUE ROBOTICS BAR02 R2","S01",art))
    s += [text(258,190,"J2 · JST-GH-4","net"),text(258,211,"1 RED   +3V3_SENSOR","txt"),text(258,230,"2 GREEN I2C_SCL","txt"),text(258,249,"3 WHITE I2C_SDA","txt"),text(258,268,"4 BLACK GND","txt"),text(258,292,"Pressure sensing face exposed to water;","small"),text(258,307,"rear electronics remain dry.","small")]

    # GPS board with ceramic patch antenna and u.FL.
    art='''<path d="M18 45H160V132H18Z" class="detail"/><rect x="35" y="58" width="62" height="55" class="detail"/><path d="M112 58h32v26h-32m0 14h32m-32 12h32" class="fine"/><circle cx="148" cy="120" r="5" class="detail"/><path d="M30 132v14m20-14v14m20-14v14m20-14v14" class="fine"/>'''
    s.append(device(58,335,185,165,"ADAFRUIT ULTIMATE GPS","S02",art))
    s += [text(258,377,"J3 · MODULE HEADER","net"),text(258,400,"PAD 2  +3V3_SENSOR","txt"),text(258,420,"PAD 3  GND","txt"),text(258,440,"PAD 4  GPS_RX ← GPIO17","txt"),text(258,460,"PAD 5  GPS_TX → GPIO16","txt"),text(258,485,"TX/RX cross at the controller.","small")]

    # Weather meter with cups and vane.
    art='''<path d="M90 45v92M55 72h70M90 72L58 52M90 72l32-20M58 52a17 10 0 1 0 0-18M122 52a17 10 0 1 1 0-18M90 72v-25" class="detail"/><path d="M112 108h42l-22-18v36zM112 108H72" class="detail"/><path d="M78 137h25v15H78" class="fine"/>'''
    s.append(device(58,520,185,175,"SPARKFUN WEATHER METER","S03",art))
    s += [text(258,560,"J7 · ANEMOMETER","net"),text(258,580,"1 +3V3 · 2 PULSE · 3 GND","txt"),text(258,610,"J8 · WIND VANE","net"),text(258,630,"1 +3V3 · 2 VANE · 3 GND","txt"),text(258,653,"Vane → ADS1115 A0 / 3.3 V divider","small")]

    # Celsius probe.
    art='''<path d="M30 80h82v34H30zM112 87h30v20h-30M142 97h20M30 90H16m14 14H16" class="detail"/><path d="M44 80v34m54-34v34" class="fine"/>'''
    s.append(device(58,715,185,135,"BLUE ROBOTICS CELSIUS R2","S04",art))
    s += [text(258,754,"J9 · DEPLOYMENT CANDIDATE","net"),text(258,776,"+3V3 · I2C_SCL · I2C_SDA · GND","txt"),text(258,800,"Verify exact harness/address", "small"),text(258,814,"before PCB freeze.","small"),text(258,834,"DS18B20: bench-only alternative.","small")]

    # ESP32 actual module drawing.
    esp='''<path d="M42 55H232V385H42Z" class="detail"/><path d="M78 70h118v104H78M92 82h90v65H92" class="detail"/><path d="M102 295h72v52h-72M115 307h46v28h-46" class="detail"/><path d="M42 83H25m17 25H25m17 25H25m17 25H25m17 25H25m17 25H25m17 25H25m17 25H25m17 25H25m17 25H25m17 25H25m190-250h17m-17 25h17m-17 25h17m-17 25h17m-17 25h17m-17 25h17m-17 25h17m-17 25h17m-17 25h17m-17 25h17m-17 25h17" class="fine"/><circle cx="72" cy="355" r="10" class="detail"/><circle cx="202" cy="355" r="10" class="detail"/>'''
    s.append(device(665,175,275,430,"ESP32-DEVKITC V4","U3",esp))
    s += [text(802,625,"USB / 5 V commissioning only","small","middle"),text(802,642,"3.3 V logic · common documented GND","small","middle")]

    # Left nets from sensor area into ESP32.
    paths=[("M460 220H550V280H665","i2c","I2C SDA/SCL",535,210),("M460 420H575V360H665","uart","GPS UART · GPIO16/17",535,410),("M460 600H600V470H665","gpio","WIND_PULSE · GPIO25",520,590),("M460 640H620V530H665","gpio","WIND_VANE → ADS1115 A0",500,665),("M460 770H550V330H665","i2c","CELSIUS I2C · VERIFY",485,760)]
    for d,c,l,x,y in paths: s += [f'<path d="{d}" class="{c}"/>',text(x,y,l,"net")]

    # Supporting breakout cards beside MCU.
    ads='''<path d="M18 48H142V125H18Z" class="detail"/><rect x="56" y="66" width="44" height="38" class="detail"/><path d="M25 58h20m-20 15h20m-20 15h20m-20 15h20m70-45h20m-20 15h20m-20 15h20m-20 15h20" class="fine"/>'''
    s.append(device(955,180,155,145,"ADS1115 ADC","U4",ads))
    mcp='''<path d="M18 48H142V125H18Z" class="detail"/><rect x="57" y="68" width="42" height="36" class="detail"/><circle cx="30" cy="60" r="4" class="fine"/><circle cx="130" cy="60" r="4" class="fine"/><path d="M24 116h112" class="fine"/>'''
    s.append(device(955,340,155,145,"MCP9808","H01",mcp))
    s += [text(1032,500,"I2C 0x48 / 0x18","net","middle"),text(1032,518,"MCP9808: mount away from heat","small","middle")]

    # Security contact + buzzer driver, clearly provisional.
    s += ['<path d="M965 575h55v20h-55m72 0h55v-20h-55" class="detail"/>',text(1028,615,"CONTACT SWITCH · GPIO33","net","middle"),
          '<path d="M975 690h32l18-18v56l-18-18h-32zM1025 686q18 8 0 16M1034 678q30 16 0 32" class="detail"/>',text(1028,750,"BUZZER + MOSFET · GPIO27","net","middle"),text(1028,768,"Exact buzzer/driver remains TBD","warn","middle")]
    s += ['<path d="M940 590H965" class="gpio"/>','<path d="M940 700H975" class="gpio"/>']

    # Power sources and actual breakout-style INA260 boards.
    s += ['<path d="M1175 160h120v85h-120zM1215 160v85m40-85v85m-80-28h120m-120-29h120" class="detail"/>',text(1235,264,"P1 · 2 × 30 W SOLAR","devtitle","middle"),
          '<path d="M1335 170h110v68h-110zM1350 187h45v25h-45m60-15h20" class="detail"/>',text(1390,264,"P2 · MPPT","devtitle","middle"),
          '<path d="M1495 165h185v80h-185zM1515 185h145v40h-145" class="detail"/>',text(1587,264,"P3 · 12.8 V LiFePO4","devtitle","middle"),
          '<path d="M1295 202H1335M1445 202H1495" class="pwr"/>']
    ina='''<path d="M15 45H150V125H15Z" class="detail"/><path d="M28 58h38v28H28m75-4h32v25h-32" class="detail"/><rect x="68" y="62" width="30" height="35" class="detail"/><path d="M28 112h105" class="fine"/>'''
    s.append(device(1180,300,165,145,"INA260 SOLAR · 0x41","H03",ina)); s.append(device(1385,300,165,145,"INA260 BATTERY · 0x40","H02",ina))
    s += ['<path d="M1235 245V300" class="pwr"/><path d="M1490 245V300" class="pwr"/>',text(1580,325,"HIGH-CURRENT PATHS","net"),text(1580,345,"stay off carrier headers","small"),text(1580,365,"Logic header only:","small"),text(1580,380,"3V3 · GND · SDA · SCL","small"),
          '<path d="M1180 470H1650" class="pwr"/>',text(1415,490,"FUSED INPUT → REVERSE POLARITY / TVS → 5 V BUCK → 3V3 LDO","net","middle"),text(1415,510,"TP: VBAT · +5V · +3V3 · GND · validate ratings by load test","small","middle")]

    # SIM7600 detailed HAT and shore station.
    sim='''<path d="M18 48H250V210H18Z" class="detail"/><rect x="55" y="72" width="118" height="85" class="detail"/><path d="M68 86h92v58H68" class="fine"/><rect x="188" y="72" width="42" height="58" class="detail"/><circle cx="45" cy="182" r="8" class="detail"/><circle cx="75" cy="182" r="8" class="detail"/><circle cx="105" cy="182" r="8" class="detail"/><path d="M185 160h45v28h-45" class="detail"/>'''
    s.append(device(1175,590,270,245,"WAVESHARE SIM7600G-H 4G HAT","C02",sim))
    s += [text(1310,850,"Separate regulated 5 V branch","small","middle"),text(1310,864,"Peak current and interface: TBD","small","middle"),
          '<path d="M1450 685H1515" class="uart"/>',text(1482,675,"UART/USB","net","middle"),
          '<path d="M1515 625h200v150h-200zM1540 650h150v90h-150M1580 775v25h50v-25" class="detail"/>',text(1615,825,"SHORE BAY STATION","devtitle","middle"),
          '<path d="M1310 590V565q15-22 30 0M1320 575q5-8 10 0" class="radio"/><path d="M1445 650q40-55 75 0" class="radio"/>',
          text(1615,845,"Database · pressure processing","small","middle"),text(1615,860,"AI prediction · dashboard · alerts","small","middle")]

    # Bottom connector table / legend / controls.
    s += ['<rect x="40" y="900" width="1720" height="230" class="panel"/>',text(55,926,"E — CONTROLLED CONNECTOR SUMMARY / DRAWING NOTES","head"),
          text(60,955,"J2 BAR02", "net"),text(155,955,"3V3 · SCL · SDA · GND", "txt"),text(60,980,"J3 GPS", "net"),text(155,980,"3V3 · GND · GPS_RX · GPS_TX", "txt"),text(60,1005,"J4/J5 INA260", "net"),text(155,1005,"3V3 · GND · SCL · SDA (logic only)", "txt"),
          text(460,955,"J6 MCP9808", "net"),text(600,955,"3V3 · SCL · SDA · GND", "txt"),text(460,980,"J7 ANEMOMETER", "net"),text(600,980,"3V3 · WIND_PULSE · GND", "txt"),text(460,1005,"J8 WIND VANE", "net"),text(600,1005,"3V3 · WIND_VANE · GND", "txt"),
          text(850,955,"J9 CELSIUS", "net"),text(960,955,"Final I2C harness/address: VERIFY", "txt"),text(850,980,"LTE LINK", "net"),text(960,980,"UART/USB and voltage levels: NOT FROZEN", "txt"),text(850,1005,"SERVICE", "net"),text(960,1005,"USB/UART for bench commissioning only", "txt"),
          '<line x1="60" y1="1030" x2="1740" y2="1030" class="fine"/>',
          '<line x1="70" y1="1055" x2="110" y2="1055" class="pwr"/>',text(120,1059,"POWER","net"),'<line x1="210" y1="1055" x2="250" y2="1055" class="i2c"/>',text(260,1059,"I2C","net"),'<line x1="335" y1="1055" x2="375" y2="1055" class="uart"/>',text(385,1059,"UART/USB","net"),'<line x1="495" y1="1055" x2="535" y2="1055" class="gpio"/>',text(545,1059,"GPIO/ANALOG","net"),'<line x1="680" y1="1055" x2="720" y2="1055" class="radio"/>',text(730,1059,"CELLULAR","net"),
          text(60,1092,"NOTES: 1) Pin numbers are provisional until exact purchased modules and connector orientations are verified.  2) Disconnect USB, battery and solar before rewiring.","small"),
          text(60,1110,"3) No BNO085 or Orange Pi is part of the Phase 1 buoy harness.  4) KiCad schematic and verified harness register control fabrication—not this illustrated reference.","small"),
          '<rect x="1220" y="1042" width="520" height="70" class="panel"/>',text(1235,1064,"DRAWING", "small"),text(1340,1064,"FALCON-BP-007", "head"),text(1235,1086,"STATUS", "small"),text(1340,1086,"REFERENCE / NOT FOR FABRICATION", "warn"),text(1580,1064,"REV", "small"),text(1625,1064,"P0", "head"),text(1580,1086,"DATE", "small"),text(1625,1086,"2026-09-01", "head")]
    s += [text(45,1162,"PROJECT FALCON-01 · COASTAL MONITORING BUOY · VERIFY EVERY PURCHASED MODULE, CONNECTOR, VOLTAGE AND PIN 1 BEFORE ENERGIZING","subtitle"),'</svg>']
    return '\n'.join(s)


if __name__ == "__main__":
    OUT.write_text(drawing(),encoding="utf-8")
    print(f"Generated {OUT.relative_to(ROOT)}")
