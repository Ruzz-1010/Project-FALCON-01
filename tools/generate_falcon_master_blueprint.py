#!/usr/bin/env python3
"""Generate the Gemini-style FALCON master blueprint from real V2 GLB edges.

This is a coordinated reference sheet, not a fabrication release. Orthographic
linework is projected from the repository GLB; unresolved engineering values
remain explicit instead of being invented.
"""

from pathlib import Path
import math

from generate_falcon_blueprint import ROOT, MODEL, load_glb, cad_edges, clip_segment, esc

OUT = ROOT / "docs/blueprints/FALCON-BP-000-master-assembly-systems.svg"


def panel(out, x, y, w, h, title):
    out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="box"/>',
            f'<text x="{x+14}" y="{y+26}" class="head">{esc(title)}</text>']


def project(out, edges, x, y, w, h, ax, ay, predicate, limit=5000):
    axis = ({0, 1, 2} - {ax, ay}).pop()
    selected = [e for e in edges if predicate(e) and (e[3] or axis in e[4])]
    if not selected:
        out.append(f'<text x="{x+w/2}" y="{y+h/2}" class="warn" text-anchor="middle">CAD GEOMETRY NOT FOUND</text>')
        return
    points = [p for e in selected for p in e[:2]]
    lo = [min(p[i] for p in points) for i in range(3)]
    hi = [max(p[i] for p in points) for i in range(3)]
    sx, sy = max(hi[ax]-lo[ax], .001), max(hi[ay]-lo[ay], .001)
    scale = min((w-38)/sx, (h-46)/sy)
    ox = x+w/2-(lo[ax]+hi[ax])*scale/2
    oy = y+h/2+(lo[ay]+hi[ay])*scale/2
    unique = {}
    for a, b, *_ in selected:
        clipped = clip_segment(ox+a[ax]*scale, oy-a[ay]*scale, ox+b[ax]*scale, oy-b[ay]*scale,
                               x+5, y+5, x+w-5, y+h-5)
        if not clipped:
            continue
        x1,y1,x2,y2 = clipped
        if math.hypot(x2-x1,y2-y1) < 1.1:
            continue
        key = tuple(sorted(((round(x1,1),round(y1,1)),(round(x2,1),round(y2,1)))))
        unique[key]=(x1,y1,x2,y2,math.hypot(x2-x1,y2-y1))
    kept=sorted(unique.values(),key=lambda z:z[4],reverse=True)[:limit]
    out.append('<path class="obj" d="'+' '.join(f'M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}' for x1,y1,x2,y2,_ in kept)+'"/>')
    out.append(f'<line x1="{x+w/2}" y1="{y}" x2="{x+w/2}" y2="{y+h}" class="ctr"/>')


def project_iso(out, edges, x, y, w, h, predicate, limit=5000):
    """Axonometric CAD edge projection for recognizable component details."""
    selected=[e for e in edges if predicate(e)]
    if not selected:
        out.append(f'<text x="{x+w/2}" y="{y+h/2}" class="warn" text-anchor="middle">CAD GEOMETRY NOT FOUND</text>')
        return
    def iso(p): return (p[0]-.62*p[1], p[2]+.30*(p[0]+p[1]))
    pts=[iso(p) for e in selected for p in e[:2]]
    lo=(min(p[0] for p in pts),min(p[1] for p in pts)); hi=(max(p[0] for p in pts),max(p[1] for p in pts))
    sx,sy=max(hi[0]-lo[0],.001),max(hi[1]-lo[1],.001)
    scale=min((w-16)/sx,(h-16)/sy)
    ox=x+w/2-(lo[0]+hi[0])*scale/2; oy=y+h/2+(lo[1]+hi[1])*scale/2
    unique={}
    for e in selected:
        a,b=iso(e[0]),iso(e[1])
        clipped=clip_segment(ox+a[0]*scale,oy-a[1]*scale,ox+b[0]*scale,oy-b[1]*scale,x+3,y+3,x+w-3,y+h-3)
        if not clipped: continue
        x1,y1,x2,y2=clipped
        length=math.hypot(x2-x1,y2-y1)
        if length<.8: continue
        key=tuple(sorted(((round(x1,1),round(y1,1)),(round(x2,1),round(y2,1)))))
        unique[key]=(x1,y1,x2,y2,length)
    kept=sorted(unique.values(),key=lambda z:z[4],reverse=True)[:limit]
    out.append('<path class="obj" d="'+' '.join(f'M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}' for x1,y1,x2,y2,_ in kept)+'"/>')


def text_rows(out, x, y, rows, line=24, cls="text"):
    for idx, row in enumerate(rows):
        out.append(f'<text x="{x}" y="{y+idx*line}" class="{cls}">{esc(row)}</text>')


def drawing(edges):
    W=2048; H=2048
    ext_terms=("BATTERY","BMS","MPPT","DC_DC","FUSED","DISCONNECT","ORANGE_PI","ESP32","MODEM_ENVELOPE","DISTRIBUTION_BOARD","FAN_","AIR_GUIDE","HEAT_SINK","THERMAL_BRIDGE","LEAK_TRAY","GASKET","HINGE","LATCH","FASTENER","MEMBRANE_VENT","ANCHOR","CHAIN","BALLAST","SHACKLE","LANYARD","CLEVIS")
    def exterior(e):
        name=e[2].upper()
        return not any(t in name for t in ext_terms) and max(e[0][2],e[1][2])>.35
    def mooring(e): return any(t in e[2].upper() for t in ("ANCHOR","CHAIN","BALLAST","SHACKLE","LANYARD","CLEVIS"))
    def equipment(e): return any(t in e[2].upper() for t in ("LIFEPO4_BATTERY","BATTERY_BMS","MPPT_CONTROLLER","DC_DC_CONVERTER","FUSED_POWER","MAIN_BATTERY_DISCONNECT","ESP32_CONTROLLER","LTE_4G_MODEM","SENSOR_DISTRIBUTION"))
    def sensor(e): return any(t in e[2].upper() for t in ("WIND_","GNSS_","NAVIGATION_LIGHT","PRESSURE_","BAR02_","SENSOR_GUARD"))
    def named(*terms):
        terms=tuple(t.upper() for t in terms)
        return lambda e: any(t in e[2].upper() for t in terms)

    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '''<defs><style>
svg{shape-rendering:geometricPrecision;background:#f7fafc}path,line,polyline,polygon,rect,circle{vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round}.sheet{fill:#f7fafc;stroke:#18364a;stroke-width:2}.box{fill:#fbfdfe;stroke:#29485c;stroke-width:1.2}.obj{fill:none;stroke:#21465c;stroke-width:.78}.strong{fill:none;stroke:#18364a;stroke-width:1.6}.thin{fill:none;stroke:#4e6878;stroke-width:.8}.ctr{fill:none;stroke:#9aabb5;stroke-width:.65;stroke-dasharray:9 3 2 3}.wire{fill:none;stroke:#345d73;stroke-width:1.2;marker-end:url(#arrow)}.data{fill:none;stroke:#6b7280;stroke-width:1.1;stroke-dasharray:7 4;marker-end:url(#arrow)}.power{fill:none;stroke:#8a633a;stroke-width:1.3;marker-end:url(#arrow)}.title{font-family:Arial,sans-serif;font-size:27px;font-weight:800;fill:#102b3c}.subtitle{font-family:Arial,sans-serif;font-size:11px;font-weight:600;fill:#4b6473;letter-spacing:.7px}.head{font-family:Arial,sans-serif;font-size:13px;font-weight:800;fill:#17384c}.subhead{font-family:Arial,sans-serif;font-size:11px;font-weight:800;fill:#284b5f}.text{font-family:Arial,sans-serif;font-size:10px;fill:#304b5c}.small{font-family:Arial,sans-serif;font-size:8px;fill:#4e6573}.tiny{font-family:Arial,sans-serif;font-size:7px;fill:#607582}.code{font-family:Consolas,monospace;font-size:9px;font-weight:700;fill:#1f4257}.warn{font-family:Arial,sans-serif;font-size:11px;font-weight:800;fill:#9f1239}.tag{fill:#edf4f7;stroke:#78909c;stroke-width:.8}.part{fill:#f0f5f7;stroke:#284b5f;stroke-width:1}.pcb{fill:#e7f0f3;stroke:#31566b;stroke-width:1}.battery{fill:#e8ecef;stroke:#2f4e60;stroke-width:1.2}.solar{fill:#edf3f6;stroke:#284b5f;stroke-width:1}.water{fill:#edf6f7;stroke:#5d8491;stroke-width:.8;stroke-dasharray:5 4}
</style><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#345d73"/></marker></defs>''',
         '<rect x="18" y="18" width="2012" height="2012" class="sheet"/>',
         '<text x="50" y="62" class="title">PROJECT FALCON-01 — COASTAL MONITORING BUOY</text>',
         '<text x="50" y="88" class="subtitle">MASTER ASSEMBLY · SUBSYSTEMS · ELECTRONICS · POWER · MOORING · V2 CAD REFERENCE</text>',
         '<rect x="1650" y="42" width="330" height="48" rx="4" class="tag"/><text x="1815" y="72" class="warn" text-anchor="middle">REFERENCE / NOT FOR FABRICATION</text>']

    # Top: actual projected views.
    panel(out,50,120,570,630,"A — FRONT ELEVATION · CAD-PROJECTED")
    project(out,edges,68,160,534,505,0,2,exterior,7000)
    out += ['<line x1="110" y1="690" x2="560" y2="690" class="thin"/>',
            '<text x="335" y="712" class="subhead" text-anchor="middle">FLOAT Ø0.650 m · V2 CAD REF</text>',
            '<text x="335" y="731" class="small" text-anchor="middle">Overall installed height and loaded waterline: VERIFY IN NATIVE CAD / FLOTATION TEST</text>']
    panel(out,640,120,330,630,"B — RIGHT ELEVATION")
    project(out,edges,660,160,290,535,1,2,exterior,5000)
    out.append('<text x="805" y="730" class="small" text-anchor="middle">ORTHOGRAPHIC · DO NOT SCALE</text>')
    panel(out,990,120,500,300,"C — PLAN VIEW")
    project(out,edges,1010,160,460,225,0,1,exterior,5000)
    panel(out,990,440,500,310,"D — ELECTRONICS POD / EQUIPMENT PLAN")
    project(out,edges,1015,480,450,225,0,1,equipment,3500)
    out.append('<text x="1240" y="730" class="small" text-anchor="middle">Orange Pi excluded · shore Bay Station only</text>')
    panel(out,1510,120,470,630,"E — EXPLODED ASSEMBLY VIEW · NTS")
    # Every exploded item below is projected from named V2 CAD geometry.
    out.append('<line x1="1710" y1="155" x2="1710" y2="710" class="ctr"/>')
    exploded=[
        ("E01","SENSOR PLATFORM",170,named("WIND_","GNSS_","NAVIGATION_LIGHT","LTE_4G_ANTENNA","WIFI_ANTENNA")),
        ("E02","DUAL SOLAR ARRAY",255,named("SOLAR_30W","DUAL_SOLAR")),
        ("E03","TAPERED FRAME",340,named("REV5_MAST_","MAST_","BAY_","TOP_SENSOR_PLATFORM")),
        ("E04","SEALED ELECTRONICS POD",430,named("RECT_POD_","REV5_RECTANGULAR")),
        ("E05","FLOAT / KEEL",525,named("MAIN_FLOAT_TRADITIONAL","MAIN_FLOAT_EDGE","MAIN_FLOAT_UPPER","MAIN_FLOAT_LOWER")),
        ("E06","BALLAST + MOORING",625,named("ADJUSTABLE_LOW_BALLAST","BALLAST_V2_","MOORING_LOAD","SHACKLE","SNUBBER")),
    ]
    for code,label,yy,pred in exploded:
        project_iso(out,edges,1555,yy,260,72,pred,2200)
        out += [f'<path d="M1818 {yy+36}H1865" class="thin"/>',f'<text x="1874" y="{yy+31}" class="code">{code}</text>',f'<text x="1874" y="{yy+46}" class="small">{label}</text>']
    out.append('<text x="1745" y="730" class="small" text-anchor="middle">Exploded reference only · separation gaps are not dimensions</text>')

    # Middle subsystem flow.
    panel(out,50,775,940,400,"F — SUBSYSTEM INTERCONNECTION / DATA FLOW")
    # CAD-projected hardware replaces illustrative icons.
    project_iso(out,edges,75,815,170,100,named("WIND_","GNSS_","NAVIGATION_LIGHT"),2200)
    project_iso(out,edges,75,940,170,100,named("WATER_PRESSURE_SENSOR","PRESSURE_GUARD","BAR02_"),2200)
    out += ['<text x="160" y="930" class="subhead" text-anchor="middle">TOP SENSOR ARRAY</text>',
            '<text x="160" y="1055" class="subhead" text-anchor="middle">PRESSURE SENSOR ASSEMBLY</text>']
    project_iso(out,edges,280,820,255,225,named("RECT_POD_","UPPER_POD_ELECTRONICS","ESP32_CONTROLLER","LTE_4G_MODEM","SENSOR_DISTRIBUTION"),3500)
    out += ['<text x="407" y="1070" class="subhead" text-anchor="middle">SEALED ELECTRONICS POD</text>',
            '<text x="407" y="1088" class="small" text-anchor="middle">protected I/O · ESP32 · cellular modem</text>']
    project_iso(out,edges,570,835,150,190,named("ESP32_CONTROLLER","SENSOR_DISTRIBUTION"),1800)
    out.append('<text x="645" y="1050" class="subhead" text-anchor="middle">CONTROL / I/O</text>')
    project_iso(out,edges,750,835,150,190,named("LTE_4G_MODEM","LTE_4G_ANTENNA"),1800)
    out += ['<text x="825" y="1050" class="subhead" text-anchor="middle">CELLULAR TELEMETRY</text>',
            '<path d="M245 910H280M535 910H570M720 910H750" class="data"/>',
            '<path d="M825 835q18-26 38-7q28-18 43 9q22 0 22 20" class="data"/>',
            '<text x="495" y="1125" class="small" text-anchor="middle">SENSORS → PROTECTED POD I/O → ESP32 ACQUISITION → LTE/INTERNET → SHORE BAY STATION / DASHBOARD</text>']

    panel(out,1010,775,480,400,"G — POWER MANAGEMENT")
    project_iso(out,edges,1030,820,130,150,named("SOLAR_30W","DUAL_SOLAR"),2200)
    project_iso(out,edges,1180,820,105,150,named("MPPT_CONTROLLER"),1200)
    project_iso(out,edges,1310,820,145,150,named("LIFEPO4_BATTERY","BATTERY_BMS"),1800)
    out += ['<text x="1095" y="990" class="subhead" text-anchor="middle">2 × 30 W SOLAR</text>',
            '<text x="1232" y="990" class="subhead" text-anchor="middle">MPPT</text>',
            '<text x="1382" y="990" class="subhead" text-anchor="middle">12.8 V 20 Ah LiFePO4</text>',
            '<path d="M1160 900H1180M1285 900H1310M1382 970V1010H1140" class="power"/>',
            '<path d="M1140 1040h30l8-15 15 30 15-30 15 30 15-15h25" class="strong"/><text x="1200" y="1080" class="small" text-anchor="middle">FUSE · TVS · REVERSE-POLARITY · DISCONNECT</text>',
            '<path d="M1290 1040q8-18 16 0q8-18 16 0q8-18 16 0h18" class="strong"/><path d="M1375 1015h70v50h-70zM1388 1040h44" class="strong"/>',
            '<text x="1320" y="1080" class="subhead" text-anchor="middle">5 V BUCK</text><text x="1410" y="1080" class="subhead" text-anchor="middle">3V3 LDO</text>',
            '<path d="M1263 1040H1290M1356 1040H1375" class="power"/>',
            '<circle cx="1445" cy="885" r="5" class="part"/><text x="1432" y="870" class="code">TP_VBAT</text>',
            '<circle cx="1356" cy="1040" r="5" class="part"/><text x="1332" y="1020" class="code">TP_5V</text>',
            '<circle cx="1445" cy="1040" r="5" class="part"/><text x="1417" y="1010" class="code">TP_3V3</text>',
            '<text x="1250" y="1125" class="small" text-anchor="middle">CAD envelopes above · standard electrical symbols below · ratings controlled by measured load test</text>']

    panel(out,1510,775,470,400,"H — MOORING / ANCHORAGE")
    project_iso(out,edges,1535,820,185,300,named("ANCHOR_CHAIN_LINK","BALLAST_CHAIN_LINK"),3500)
    project_iso(out,edges,1740,835,200,265,named("CONCRETE_MOORING_ANCHOR","ANCHOR_REINFORCED","ANCHOR_316SS_MOORING_EYE"),3500)
    out += ['<text x="1627" y="1130" class="subhead" text-anchor="middle">CHAIN / CONNECTING HARDWARE</text>',
            '<text x="1840" y="1130" class="subhead" text-anchor="middle">CONCRETE ANCHOR · CAD REF</text>',
            '<text x="1745" y="1152" class="small" text-anchor="middle">Scope, WLL, corrosion allowance and anchor mass remain site-engineering verification items.</text>']

    # Bottom reference schedules.
    panel(out,50,1200,680,520,"J — CONTROLLED COMPONENT REGISTER")
    headers=[("ID",65),("COMPONENT",120),("STATUS",430),("FUNCTION",545)]
    for t,x in headers: out.append(f'<text x="{x}" y="1245" class="subhead">{t}</text>')
    rows=[("S01","Blue Robotics Bar02 R2","PROTOTYPE","Pressure / wave input"),("S02","Adafruit Ultimate GPS PID 746","PROTOTYPE","Position / geofence"),("S03","SparkFun SEN-15901","PROTOTYPE","Wind speed / direction"),("S04","Blue Robotics Celsius R2","CANDIDATE","Water temperature"),("H01","Adafruit MCP9808 PID 1782","SELECTED","Enclosure temperature"),("H02","Adafruit INA260 PID 4226 ×2","PROTOTYPE","Battery / solar health"),("C01","ESP32-DevKitC V4","SELECTED","Buoy controller"),("C02","SIM7600G-H 4G HAT","CANDIDATE","Cellular telemetry"),("P01","LiFePO4 12.8 V 20 Ah","RATING SET","Exact SKU / case TBD"),("SEC","Contact switch PID 375","PROTOTYPE","Enclosure-open state"),("A01","Buzzer + driver","TBD","Audible security alarm")]
    yy=1280
    for rid,name,status,func in rows:
        out += [f'<line x1="50" y1="{yy-20}" x2="730" y2="{yy-20}" class="thin"/>',f'<text x="65" y="{yy}" class="code">{rid}</text>',f'<text x="120" y="{yy}" class="text">{esc(name)}</text>',f'<text x="430" y="{yy}" class="small">{esc(status)}</text>',f'<text x="545" y="{yy}" class="small">{esc(func)}</text>']; yy+=37

    panel(out,750,1200,740,520,"K — SIMPLIFIED SENSOR / CONTROLLER WIRING")
    out += [# ESP32 board with castellated/header pins and module
            '<path d="M1050 1290h155v300h-155zM1080 1315h95v80h-95M1088 1330h78v45h-78" class="strong"/>',
            '<path d="M1050 1320h-14m14 30h-14m14 30h-14m14 30h-14m14 30h-14m14 30h-14m14 30h-14m14 30h-14m14 30h-14M1205 1320h14m-14 30h14m-14 30h14m-14 30h14m-14 30h14m-14 30h14m-14 30h14m-14 30h14" class="thin"/>',
            '<text x="1127" y="1425" class="head" text-anchor="middle">ESP32-DevKitC V4</text><text x="1127" y="1445" class="small" text-anchor="middle">acquisition · validation · buffering</text>',
            # left locking connectors and sensor symbols
            '<path d="M795 1285h55v34h-55m0 50h55v34h-55m0 50h55v34h-55m0 50h55v34h-55m0 50h55v34h-55" class="strong"/>',
            '<text x="790" y="1274" class="subhead">LOCKING FIELD CONNECTORS</text>',
            '<text x="860" y="1307" class="text">J2 BAR02 · 3V3 / SDA / SCL / GND</text><text x="860" y="1391" class="text">J3 GPS · 5V / TX / RX / GND</text>',
            '<text x="860" y="1475" class="text">J7 WIND SPEED · 3V3 / PULSE / GND</text><text x="860" y="1559" class="text">J8 WIND DIR · 3V3 / ADC / GND</text>',
            '<text x="860" y="1643" class="text">J9 WATER TEMP · 3V3 / SDA / SCL / GND</text>',
            # clean named nets to MCU
            '<path d="M850 1302H990V1350H1036M850 1386H975V1410H1036M850 1470H960V1470H1036M850 1554H975V1530H1036M850 1638H990V1560H1036" class="data"/>',
            '<text x="950" y="1295" class="code">I2C_SDA / I2C_SCL</text><text x="930" y="1377" class="code">GPS_TX / GPS_RX</text><text x="925" y="1462" class="code">WIND_SPEED</text><text x="930" y="1546" class="code">WIND_DIR_ADC</text>',
            # right communications, I2C pullups, testpoints
            '<path d="M1219 1360H1300M1219 1410H1300M1219 1460H1300M1219 1510H1300" class="data"/>',
            '<path d="M1300 1335v50h120v-50zM1300 1395v50h120v-50zM1300 1455v50h120v-50zM1300 1515v50h120v-50z" class="strong"/>',
            '<text x="1360" y="1366" class="subhead" text-anchor="middle">J10 LTE UART / USB</text><text x="1360" y="1426" class="subhead" text-anchor="middle">J11 DEBUG UART</text>',
            '<text x="1360" y="1486" class="subhead" text-anchor="middle">J12 FUTURE I2C</text><text x="1360" y="1546" class="subhead" text-anchor="middle">J13 EXPANSION</text>',
            '<path d="M1240 1595v-45m25 45v-45M1230 1550h20m5 0h20" class="strong"/><text x="1252" y="1615" class="small" text-anchor="middle">4.7 kΩ I2C PULL-UPS</text>',
            '<circle cx="1320" cy="1600" r="5" class="part"/><circle cx="1350" cy="1600" r="5" class="part"/><circle cx="1380" cy="1600" r="5" class="part"/><circle cx="1410" cy="1600" r="5" class="part"/>',
            '<text x="1365" y="1622" class="small" text-anchor="middle">TP: 3V3 · 5V · SDA · SCL · TX · RX · GND</text>',
            '<line x1="780" y1="1665" x2="1455" y2="1665" class="strong"/><text x="790" y="1658" class="code">GND</text>',
            '<text x="1120" y="1695" class="small" text-anchor="middle">Functional wiring only—KiCad schematic controls pin numbers and manufacturing netlist · Orange Pi remains ashore</text>']

    panel(out,1510,1200,470,260,"L — GENERAL NOTES")
    text_rows(out,1530,1245,["1. Orthographic linework is projected from PROJECT-FALCON-V2.glb.","2. V2 geometry remains a proposed replacement reference.","3. Do not scale this drawing; verify native CAD and purchased parts.","4. Dimensions, mass and placement marked TBD must not be invented.","5. Complete stability, structure, ingress, thermal and mooring reviews.","6. Orange Pi/Bay Station computer remains ashore."],30)
    out.append('<text x="1745" y="1435" class="warn" text-anchor="middle">PRELIMINARY ENGINEERING REFERENCE</text>')

    # Title block.
    panel(out,1510,1480,470,240,"M — DRAWING CONTROL")
    out += ['<line x1="1510" y1="1550" x2="1980" y2="1550" class="box"/>','<line x1="1745" y1="1480" x2="1745" y2="1720" class="box"/>',
            '<text x="1530" y="1525" class="small">PROJECT</text><text x="1530" y="1585" class="title">FALCON-01</text>',
            '<text x="1765" y="1525" class="small">DRAWING TITLE</text><text x="1765" y="1580" class="subhead">MASTER ASSEMBLY &amp; SYSTEMS</text>',
            '<text x="1530" y="1630" class="small">DRAWING NO.</text><text x="1630" y="1630" class="head">FALCON-BP-000</text>',
            '<text x="1765" y="1630" class="small">REVISION</text><text x="1850" y="1630" class="head">P0</text>',
            '<text x="1530" y="1670" class="small">SCALE</text><text x="1630" y="1670" class="head">NTS</text>',
            '<text x="1765" y="1670" class="small">DATE</text><text x="1850" y="1670" class="head">2026-09-01</text>',
            '<text x="1530" y="1703" class="small">SOURCE</text><text x="1630" y="1703" class="text">V2 GLB + DOCS</text>',
            '<text x="1765" y="1703" class="small">STATUS</text><text x="1850" y="1703" class="warn">REFERENCE</text>']

    # Footer approvals.
    out += ['<rect x="50" y="1745" width="1930" height="235" class="box"/>','<text x="70" y="1780" class="head">RELEASE GATES / APPROVAL</text>']
    text_rows(out,70,1815,["□ Native CAD dimension audit     □ Purchased-part fit / connector clearance     □ Loaded mass / displacement / waterline / freeboard", "□ CG / stability / righting test     □ Structural load and fastener review     □ IP / leak / thermal / corrosion validation", "□ Solar / battery measured load budget     □ Pressure installation and wave-reference validation     □ Mooring WLL / anchor design review"],31)
    out += ['<line x1="70" y1="1945" x2="520" y2="1945" class="thin"/><text x="70" y="1964" class="small">PREPARED BY / DATE</text>',
            '<line x1="610" y1="1945" x2="1060" y2="1945" class="thin"/><text x="610" y="1964" class="small">ENGINEERING REVIEW / DATE</text>',
            '<line x1="1150" y1="1945" x2="1600" y2="1945" class="thin"/><text x="1150" y="1964" class="small">THESIS ADVISER APPROVAL / DATE</text>',
            '<text x="1950" y="1964" class="warn" text-anchor="end">NOT FOR FABRICATION</text>','</svg>']
    return '\n'.join(out)


def main():
    doc, blob = load_glb(MODEL)
    edges = cad_edges(doc, blob)
    OUT.write_text(drawing(edges), encoding="utf-8")
    print(f"Generated {OUT.relative_to(ROOT)} from {len(edges):,} CAD feature edges")


if __name__ == "__main__":
    main()
