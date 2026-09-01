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
    panel(out,1510,120,470,630,"E — ASSEMBLY HIERARCHY · NTS")
    # Truthful exploded hierarchy (not fake CAD separation).
    parts=[("E01","TOP SENSOR PLATFORM",184), ("E02","DUAL SOLAR ARRAY",264), ("E03","TAPERED MAST / FRAME",344), ("E04","SEALED ELECTRONICS POD",424), ("E05","MAIN FLOAT / KEEL",504), ("E06","ADJUSTABLE BALLAST",584), ("E07","SINGLE-ANCHOR MOORING",664)]
    for code,label,yy in parts:
        out += [f'<rect x="1580" y="{yy-28}" width="300" height="44" rx="4" class="part"/>',f'<text x="1594" y="{yy}" class="code">{code}</text>',f'<text x="1640" y="{yy}" class="text">{label}</text>']
        if yy<664: out.append(f'<line x1="1730" y1="{yy+16}" x2="1730" y2="{yy+50}" class="data"/>')
    out.append('<text x="1745" y="720" class="small" text-anchor="middle">Hierarchy only; separation distances are not dimensions.</text>')

    # Middle subsystem flow.
    panel(out,50,775,940,400,"F — SUBSYSTEM INTERCONNECTION / DATA FLOW")
    blocks=[(90,850,145,78,"PRESSURE","Bar02 R2"),(90,955,145,78,"WIND","SEN-15901"),(90,1060,145,78,"GPS / TEMP","PID 746 / Celsius R2"),(300,865,180,110,"PROTECTED I/O","I2C · UART · ADC · GPIO"),(530,865,180,110,"ESP32","Acquisition · validation · buffer"),(760,865,180,110,"LTE MODEM","SIM7600G-H candidate"),(760,1035,180,95,"SHORE BAY STATION","DB · API · AI · dashboard")]
    for x,y,w,h,a,b in blocks:
        out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" class="part"/>',f'<text x="{x+w/2}" y="{y+31}" class="subhead" text-anchor="middle">{esc(a)}</text>',f'<text x="{x+w/2}" y="{y+52}" class="small" text-anchor="middle">{esc(b)}</text>']
    for sy in (889,994,1099): out.append(f'<path d="M235 {sy}H275Q288 {sy} 288 950V920H300" class="data"/>')
    out += ['<path d="M480 920H530" class="data"/>','<path d="M710 920H760" class="data"/>','<path d="M850 975V1035" class="data"/>',
            '<text x="510" y="1145" class="small" text-anchor="middle">Pressure-derived estimated wave height · AI prediction is processed at the shore Bay Station.</text>']

    panel(out,1010,775,480,400,"G — POWER MANAGEMENT")
    pblocks=[(1045,840,115,70,"2× SOLAR","30 W CAD ref"),(1200,840,120,70,"MPPT","LiFePO4 profile"),(1360,840,95,70,"BATTERY","12.8 V 20 Ah"),(1090,975,115,70,"FUSE / TVS","disconnect"),(1250,975,95,70,"5 V DC-DC","rating TBD"),(1380,975,75,70,"3V3","local rail")]
    for x,y,w,h,a,b in pblocks:
        out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" class="part"/>',f'<text x="{x+w/2}" y="{y+28}" class="subhead" text-anchor="middle">{esc(a)}</text>',f'<text x="{x+w/2}" y="{y+48}" class="small" text-anchor="middle">{esc(b)}</text>']
    out += ['<path d="M1160 875H1200" class="power"/>','<path d="M1320 875H1360" class="power"/>','<path d="M1408 910V945H1148V975" class="power"/>','<path d="M1205 1010H1250" class="power"/>','<path d="M1345 1010H1380" class="power"/>',
            '<text x="1250" y="1090" class="small" text-anchor="middle">INA260 battery 0x40 · INA260 solar 0x41</text>','<text x="1250" y="1110" class="warn" text-anchor="middle">Final fuses, converters and autonomy require measured load tests.</text>']

    panel(out,1510,775,470,400,"H — MOORING / ANCHORAGE")
    project(out,edges,1540,825,180,280,0,2,mooring,3500)
    out += ['<line x1="1770" y1="830" x2="1770" y2="1100" class="strong"/>','<ellipse cx="1770" cy="850" rx="18" ry="30" class="strong"/>','<path d="M1715 1110L1750 990H1870L1910 1110Z" class="part"/>']
    text_rows(out,1740,900,["PASSIVE SINGLE-ANCHOR MOORING","Chain/line scope: TBD by site depth","Shackle/WLL/corrosion: verify","Anchor geometry: V2 CAD reference","Nominal 367 kg: NOT APPROVED"],28)

    # Bottom reference schedules.
    panel(out,50,1200,680,520,"J — CONTROLLED COMPONENT REGISTER")
    headers=[("ID",65),("COMPONENT",120),("STATUS",430),("FUNCTION",545)]
    for t,x in headers: out.append(f'<text x="{x}" y="1245" class="subhead">{t}</text>')
    rows=[("S01","Blue Robotics Bar02 R2","PROTOTYPE","Pressure / wave input"),("S02","Adafruit Ultimate GPS PID 746","PROTOTYPE","Position / geofence"),("S03","SparkFun SEN-15901","PROTOTYPE","Wind speed / direction"),("S04","Blue Robotics Celsius R2","CANDIDATE","Water temperature"),("H01","Adafruit MCP9808 PID 1782","SELECTED","Enclosure temperature"),("H02","Adafruit INA260 PID 4226 ×2","PROTOTYPE","Battery / solar health"),("C01","ESP32-DevKitC V4","SELECTED","Buoy controller"),("C02","SIM7600G-H 4G HAT","CANDIDATE","Cellular telemetry"),("P01","LiFePO4 12.8 V 20 Ah","RATING SET","Exact SKU / case TBD"),("SEC","Contact switch PID 375","PROTOTYPE","Enclosure-open state"),("A01","Buzzer + driver","TBD","Audible security alarm")]
    yy=1280
    for rid,name,status,func in rows:
        out += [f'<line x1="50" y1="{yy-20}" x2="730" y2="{yy-20}" class="thin"/>',f'<text x="65" y="{yy}" class="code">{rid}</text>',f'<text x="120" y="{yy}" class="text">{esc(name)}</text>',f'<text x="430" y="{yy}" class="small">{esc(status)}</text>',f'<text x="545" y="{yy}" class="small">{esc(func)}</text>']; yy+=37

    panel(out,750,1200,740,520,"K — CONTROLLED INTERFACE MATRIX · NOT A NETLIST")
    rails=[("VBAT",1260),("+5 V",1310),("+3V3",1360),("GND",1410),("I2C SDA/SCL",1460),("GPS UART",1510),("WIND PULSE/ADC",1560),("LTE UART/USB",1610)]
    for label,yy in rails:
        out += [f'<text x="775" y="{yy}" class="code">{label}</text>',f'<line x1="900" y1="{yy-4}" x2="1455" y2="{yy-4}" class="thin"/>']
    nodes=[(940,"ESP32"),(1080,"SENSOR I/O"),(1225,"LTE"),(1355,"TEST POINTS")]
    for xx,label in nodes:
        out += [f'<rect x="{xx}" y="1275" width="105" height="360" rx="4" class="pcb"/>',f'<text x="{xx+52}" y="1300" class="subhead" text-anchor="middle">{label}</text>']
    for yy in [1306,1356,1406,1456,1506,1556,1606]:
        out += [f'<circle cx="940" cy="{yy}" r="4" class="part"/>',f'<circle cx="1185" cy="{yy}" r="4" class="part"/>',f'<circle cx="1330" cy="{yy}" r="4" class="part"/>']
    out += ['<text x="1120" y="1688" class="small" text-anchor="middle">Availability matrix only—not pin-to-pin wiring. No hydraulics · no Orange Pi onboard · locking sensor connectors.</text>']

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
