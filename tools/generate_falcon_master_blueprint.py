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


def drawing_legacy(edges):
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
svg{shape-rendering:geometricPrecision;background:#f7fafc}path,line,polyline,polygon,rect,circle{vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round}.sheet{fill:#f7fafc;stroke:#18364a;stroke-width:2}.box{fill:#fbfdfe;stroke:#29485c;stroke-width:1.2}.obj{fill:none;stroke:#21465c;stroke-width:.78}.strong{fill:none;stroke:#18364a;stroke-width:1.6}.thin{fill:none;stroke:#4e6878;stroke-width:.8}.ctr{fill:none;stroke:#9aabb5;stroke-width:.65;stroke-dasharray:9 3 2 3}.wire{fill:none;stroke:#345d73;stroke-width:1.2;marker-end:url(#arrow)}.data{fill:none;stroke:#6b7280;stroke-width:1.1;stroke-dasharray:7 4;marker-end:url(#arrow)}.power{fill:none;stroke:#8a633a;stroke-width:1.3;marker-end:url(#arrow)}.title{font-family:Arial,sans-serif;font-size:27px;font-weight:800;fill:#102b3c}.subtitle{font-family:Arial,sans-serif;font-size:11px;font-weight:600;fill:#4b6473;letter-spacing:.7px}.head{font-family:Arial,sans-serif;font-size:13px;font-weight:800;fill:#17384c}.subhead{font-family:Arial,sans-serif;font-size:11px;font-weight:800;fill:#284b5f}.text{font-family:Arial,sans-serif;font-size:10px;fill:#304b5c}.small{font-family:Arial,sans-serif;font-size:8px;fill:#4e6573}.tiny{font-family:Arial,sans-serif;font-size:7px;fill:#607582}.code{font-family:Consolas,monospace;font-size:9px;font-weight:700;fill:#1f4257}.warn{font-family:Arial,sans-serif;font-size:11px;font-weight:800;fill:#9f1239}.tag{fill:#edf4f7;stroke:#78909c;stroke-width:.8}.part{fill:#f0f5f7;stroke:#284b5f;stroke-width:1}.pcb{fill:#e7f0f3;stroke:#31566b;stroke-width:1}.battery{fill:#d9e3e8;stroke:#2f4e60;stroke-width:1.2}.solar{fill:#274c68;stroke:#17384c;stroke-width:1.2}.podface{fill:#dfe7eb;stroke:#24485d;stroke-width:1.4}.podside{fill:#b9c8d0;stroke:#24485d;stroke-width:1.2}.hardware{fill:#cbd7dd;stroke:#24485d;stroke-width:1.2}.screen{fill:#eef5f7;stroke:#31566b;stroke-width:.9}.water{fill:#edf6f7;stroke:#5d8491;stroke-width:.8;stroke-dasharray:5 4}
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
    panel(out,990,440,500,310,"D — SEALED ELECTRONICS POD · CLOSED EXTERIOR")
    out += ['<path d="M1080 515L1140 480H1370L1430 515V665L1370 705H1140L1080 665Z" class="podface"/>',
            '<path d="M1370 515L1430 515V665L1370 705Z" class="podside"/>',
            '<path d="M1105 535H1360V675H1105Z" class="screen"/><path d="M1120 550H1345V660H1120Z" class="strong"/>',
            '<path d="M1095 505L1140 475H1370L1418 505H1095Z" class="hardware"/>',
            '<circle cx="1330" cy="605" r="7" class="strong"/><path d="M1095 560h-18m18 45h-18m18 45h-18M1360 560h18m-18 45h18m-18 45h18" class="strong"/>',
            '<path d="M1160 705v18m45-18v18m45-18v18m45-18v18" class="strong"/>',
            '<text x="1245" y="730" class="small" text-anchor="middle">OPAQUE CLOSED POD · service door, gasket, compression latches and downward glands shown</text>',
            '<text x="1245" y="744" class="tiny" text-anchor="middle">Internal deck placement is controlled separately by FALCON-BP-006</text>']
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
    out += ['<path d="M305 870L350 835H480L525 870V1010L480 1040H350L305 1010Z" class="podface"/>',
            '<path d="M480 870L525 870V1010L480 1040Z" class="podside"/>',
            '<path d="M330 890H472V1015H330Z" class="screen"/><circle cx="455" cy="952" r="5" class="strong"/>']
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
    # Filled hardware illustrations replace transparent CAD envelopes.
    out += ['<path d="M1035 835L1140 815L1150 905L1045 925Z" class="solar"/>',
            '<path d="M1070 828l10 90m25-96l10 90m-75-48l105-20m-101 52l105-20" class="thin"/>',
            '<path d="M1200 830h105v86h-105z" class="hardware"/><rect x="1215" y="845" width="52" height="30" rx="3" class="screen"/><circle cx="1285" cy="855" r="5" class="strong"/><circle cx="1285" cy="875" r="5" class="strong"/><path d="M1215 896h18m12 0h18m12 0h18" class="strong"/>',
            '<path d="M1340 835h120v80h-120z" class="battery"/><path d="M1360 825h18v10h-18m62-10h18v10h-18" class="strong"/><text x="1369" y="822" class="code">−</text><text x="1428" y="822" class="code">+</text><rect x="1360" y="855" width="80" height="35" rx="3" class="screen"/><text x="1400" y="878" class="code" text-anchor="middle">LiFePO4</text>']
    out += ['<text x="1090" y="950" class="subhead" text-anchor="middle">P1 · 2 × 30 W SOLAR</text>',
            '<text x="1247" y="950" class="subhead" text-anchor="middle">P2 · MPPT</text>',
            '<text x="1400" y="950" class="subhead" text-anchor="middle">P3 · LiFePO4</text>',
            '<path d="M1150 875H1200M1295 875H1340" class="power"/>',
            '<line x1="1035" y1="980" x2="1460" y2="980" class="thin"/>',
            '<text x="1035" y="1003" class="code">VBAT POWER PATH</text>',
            '<path d="M1040 1040h36l8-16 14 32 14-32 14 32 14-16h28" class="strong"/>',
            '<text x="1105" y="1078" class="small" text-anchor="middle">F1 FUSE · D1 TVS</text>',
            '<path d="M1168 1040h20l14-16v32l14-16h25" class="strong"/><text x="1205" y="1078" class="small" text-anchor="middle">Q1 REVERSE</text>',
            '<path d="M1241 1040h24m0-15v30m0-15h35" class="strong"/><text x="1270" y="1078" class="small" text-anchor="middle">SW1</text>',
            '<path d="M1300 1040q8-18 16 0q8-18 16 0q8-18 16 0h22" class="strong"/><text x="1335" y="1078" class="small" text-anchor="middle">U1 5 V BUCK</text>',
            '<path d="M1370 1015h75v50h-75zM1384 1040h47" class="strong"/><text x="1407" y="1078" class="small" text-anchor="middle">U2 3V3 LDO</text>',
            '<circle cx="1038" cy="1040" r="5" class="part"/><circle cx="1368" cy="1040" r="5" class="part"/><circle cx="1447" cy="1040" r="5" class="part"/>',
            '<text x="1030" y="1022" class="code">TP1</text><text x="1356" y="1022" class="code">TP2</text><text x="1435" y="1022" class="code">TP3</text>',
            '<text x="1250" y="1125" class="small" text-anchor="middle">TP1 VBAT · TP2 +5 V · TP3 +3V3 · final ratings controlled by measured load test</text>']

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
    rows=[("S01","Holykell HPT604 Type A 4–20 mA","CANDIDATE","Pressure / wave input; exact configuration TBD"),("S02","Adafruit Ultimate GPS PID 746","PROTOTYPE","Position / geofence"),("S03","SparkFun SEN-15901","PROTOTYPE","Wind speed / direction"),("S04","Water temperature","EXCLUDED","Outside Phase 1 scope"),("H01","Adafruit MCP9808 PID 1782","SELECTED","Enclosure temperature"),("H02","Adafruit INA260 PID 4226 ×2","PROTOTYPE","Battery / solar health"),("C01","ESP32-DevKitC V4","SELECTED","Buoy controller"),("C02","LoRa radio","TBD","Buoy-to-Bay-Station telemetry"),("P01","LiFePO4 12.8 V 20 Ah","PROVISIONAL","Final capacity from measured load"),("SEC","Contact switch PID 375","PROTOTYPE","Enclosure-open state"),("A01","Buzzer + driver","TBD","Audible security alarm")]
    yy=1280
    for rid,name,status,func in rows:
        out += [f'<line x1="50" y1="{yy-20}" x2="730" y2="{yy-20}" class="thin"/>',f'<text x="65" y="{yy}" class="code">{rid}</text>',f'<text x="120" y="{yy}" class="text">{esc(name)}</text>',f'<text x="430" y="{yy}" class="small">{esc(status)}</text>',f'<text x="545" y="{yy}" class="small">{esc(func)}</text>']; yy+=37

    panel(out,750,1200,740,520,"K — COMPLETE BUOY ASSEMBLY · ISOMETRIC CAD VIEW")
    project_iso(out,edges,790,1240,660,420,exterior,8500)
    out += ['<path d="M790 1672H1450" class="thin"/>',
            '<text x="1120" y="1692" class="subhead" text-anchor="middle">PROJECT FALCON-01 · COMPLETE ABOVE-WATER ASSEMBLY</text>',
            '<text x="1120" y="1708" class="small" text-anchor="middle">V2 CAD-projected geometry · closed pod configuration · orthographic dimensions remain controlled by BP-001</text>']

    panel(out,1510,1200,470,260,"L — GENERAL NOTES")
    text_rows(out,1530,1245,["1. Orthographic linework is projected from PROJECT-FALCON-V2.glb.","2. V2 geometry remains a proposed replacement reference.","3. Do not scale this drawing; verify native CAD and purchased parts.","4. Dimensions, mass and placement marked TBD must not be invented.","5. Complete stability, structure, ingress, thermal and mooring reviews.","6. Orange Pi/Bay Station computer remains ashore."],30)
    out.append('<text x="1745" y="1435" class="warn" text-anchor="middle">PRELIMINARY ENGINEERING REFERENCE</text>')

    # Title block.
    panel(out,1510,1480,470,240,"M — DRAWING CONTROL")
    out += ['<line x1="1510" y1="1550" x2="1980" y2="1550" class="box"/>','<line x1="1745" y1="1480" x2="1745" y2="1720" class="box"/>',
            '<text x="1530" y="1525" class="small">PROJECT</text><text x="1530" y="1585" class="title">FALCON-01</text>',
            '<text x="1765" y="1525" class="small">DRAWING TITLE</text><text x="1765" y="1580" class="subhead">MASTER ASSEMBLY &amp; SYSTEMS</text>',
            '<text x="1530" y="1630" class="small">DRAWING NO.</text><text x="1630" y="1630" class="head">FALCON-BP-000</text>',
            '<text x="1765" y="1630" class="small">REVISION</text><text x="1850" y="1630" class="head">P1</text>',
            '<text x="1530" y="1670" class="small">SCALE</text><text x="1630" y="1670" class="head">NTS</text>',
            '<text x="1765" y="1670" class="small">DATE</text><text x="1850" y="1670" class="head">2026-09-02</text>',
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


def drawing(edges):
    """Gemini-reference composition using only controlled FALCON content."""
    W=2048; H=2048
    def named(*terms):
        terms=tuple(t.upper() for t in terms)
        return lambda e:any(t in e[2].upper() for t in terms)
    excluded=("BATTERY","BMS","MPPT","DC_DC","FUSED","DISCONNECT","ORANGE_PI","ESP32","MODEM_ENVELOPE","DISTRIBUTION_BOARD","FAN_","AIR_GUIDE","HEAT_SINK","THERMAL_BRIDGE","LEAK_TRAY","ANCHOR","CHAIN","BALLAST")
    def exterior(e): return not any(t in e[2].upper() for t in excluded) and max(e[0][2],e[1][2])>.35
    def mooring(e): return any(t in e[2].upper() for t in ("ANCHOR","CHAIN","SHACKLE","SNUBBER","BALLAST"))
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','''<defs><style>
svg{shape-rendering:geometricPrecision;background:#f8fafb}path,line,polyline,polygon,rect,circle,ellipse{vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round}.sheet{fill:#f8fafb;stroke:#102f42;stroke-width:2.2}.box{fill:#fbfdfe;stroke:#1f4256;stroke-width:1.4}.obj{fill:none;stroke:#10384f;stroke-width:.9}.strong{fill:none;stroke:#102f42;stroke-width:1.7}.thin{fill:none;stroke:#486372;stroke-width:.85}.ctr{fill:none;stroke:#8c9ca6;stroke-width:.65;stroke-dasharray:8 3 2 3}.data{fill:none;stroke:#3f6071;stroke-width:1.2;marker-end:url(#arrow)}.power{fill:none;stroke:#79542c;stroke-width:1.35;marker-end:url(#arrow)}.podface{fill:#e1e8ec;stroke:#183f55;stroke-width:1.45}.podside{fill:#bdcbd2;stroke:#183f55;stroke-width:1.3}.hardware{fill:#cbd7dd;stroke:#183f55;stroke-width:1.2}.solar{fill:#274c68;stroke:#102f42;stroke-width:1.3}.battery{fill:#d9e3e8;stroke:#28495b;stroke-width:1.3}.title{font:800 25px Arial;fill:#0c2b3d}.subtitle{font:600 10px Arial;letter-spacing:.7px;fill:#405d6c}.head{font:800 12px Arial;fill:#12374c}.subhead{font:800 10px Arial;fill:#20475b}.text{font:9px Arial;fill:#254555}.small{font:7.5px Arial;fill:#435f6e}.tiny{font:6.5px Arial;fill:#526b78}.code{font:700 8px Consolas;fill:#173f55}.warn{font:800 10px Arial;fill:#941b36}
</style><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#526c7b"/></marker></defs>''',
         '<rect x="20" y="20" width="2008" height="2008" class="sheet"/>',
         '<text x="48" y="62" class="title">PROJECT FALCON-01 — COASTAL MONITORING BUOY — ASSEMBLY &amp; SUBSYSTEMS BLUEPRINT</text>',
         '<text x="48" y="86" class="subtitle">PROPOSED V2 REFERENCE GEOMETRY · DIMENSIONS IN mm UNLESS NOTED · DO NOT SCALE</text>']

    # Gemini-matched top composition: elevation, side, plan/pod, exploded/BOM.
    panel(out,48,120,585,850,"FRONT ELEVATION — BUOY ASSEMBLY")
    project(out,edges,70,160,540,610,0,2,exterior,8000)
    out += ['<path d="M100 800H575M100 790v20M575 790v20" class="strong"/>','<text x="337" y="824" class="subhead" text-anchor="middle">MAIN FLOAT Ø650 · V2 CAD REF</text>',
            '<path d="M575 170h30m-30 570h30M596 170V740" class="strong" marker-start="url(#arrow)" marker-end="url(#arrow)"/>',
            '<text x="614" y="475" class="code" transform="rotate(-90 614 475)">3391 O/A CAD ENVELOPE</text>',
            '<path d="M190 300H250M190 300l12-6v12M250 300l-12-6v12" class="thin"/><text x="75" y="292" class="code">TOP SENSOR ARRAY</text>',
            '<path d="M190 520H250M190 520l12-6v12M250 520l-12-6v12" class="thin"/><text x="75" y="512" class="code">TAPERED MAST</text>',
            '<path d="M190 650H250M190 650l12-6v12M250 650l-12-6v12" class="thin"/><text x="75" y="642" class="code">SEALED POD / FLOAT</text>',
            '<text x="337" y="910" class="small" text-anchor="middle">Overall height, loaded waterline and freeboard: VERIFY IN NATIVE CAD</text>',
            '<text x="337" y="928" class="small" text-anchor="middle">Complete displacement, stability and flotation testing before fabrication.</text>']
    panel(out,650,120,365,850,"RIGHT ELEVATION")
    project(out,edges,672,160,320,610,1,2,exterior,6500)
    project(out,edges,700,790,265,130,0,1,named("MAIN_FLOAT_TRADITIONAL","MAIN_FLOAT_EDGE"),3500)
    out += ['<text x="832" y="940" class="small" text-anchor="middle">PLAN SECTION AT FLOAT · CAD-PROJECTED</text>']
    panel(out,1032,120,455,410,"PLAN VIEW (TOP VIEW)")
    project(out,edges,1050,155,420,335,0,1,exterior,6500)
    panel(out,1032,548,455,422,"ELECTRONICS POD")
    project(out,edges,1070,595,375,285,0,1,named("RECT_POD_","REV5_RECTANGULAR","ELECTRONICS","DISTRIBUTION_BOARD","ESP32","BATTERY","MPPT"),6000)
    out += ['<line x1="1258" y1="585" x2="1258" y2="900" class="ctr"/>',
            '<line x1="1080" y1="742" x2="1435" y2="742" class="ctr"/>',
            '<text x="1258" y="915" class="small" text-anchor="middle">SEALED POD TOP VIEW · V2 CAD REFERENCE</text>',
            '<text x="1258" y="933" class="small" text-anchor="middle">POD: 300 W × 280 D × 400 H mm · Internal layout: FALCON-BP-006</text>']
    panel(out,1505,120,475,850,"EXPLODED ASSEMBLY VIEW")
    groups=[("F-01","TOP SENSOR ARRAY",155,named("WIND_","GNSS_","NAVIGATION_LIGHT","LTE_4G_ANTENNA")),("F-02","SENSOR PLATFORM",245,named("TOP_SENSOR_PLATFORM","TOP_SENSOR_CROSS")),("F-03","DUAL SOLAR ARRAY",330,named("SOLAR_30W","DUAL_SOLAR")),("F-04","TAPERED MAST",415,named("REV5_MAST_","BAY_")),("F-05","SEALED POD",505,named("RECT_POD_","REV5_RECTANGULAR")),("F-06","MAIN FLOAT / KEEL",600,named("MAIN_FLOAT_TRADITIONAL","MAIN_FLOAT_EDGE","MAIN_FLOAT_UPPER","MAIN_FLOAT_LOWER")),("F-07","BALLAST CONNECTOR",695,named("ADJUSTABLE_LOW_BALLAST","BALLAST_V2_"))]
    out.append('<line x1="1668" y1="148" x2="1668" y2="750" class="ctr"/>')
    for ref,label,y,pred in groups:
        project_iso(out,edges,1540,y,250,70,pred,2600)
        out += [f'<path d="M1795 {y+35}H1840" class="thin"/>',f'<text x="1850" y="{y+31}" class="code">{ref}</text>',f'<text x="1850" y="{y+46}" class="small">{label}</text>']
    out += ['<line x1="1525" y1="785" x2="1960" y2="785" class="strong"/>','<text x="1525" y="810" class="head">PARTS LIST / BILL OF MATERIALS</text>']
    bom=[("F-01","Top sensor array","wind · GNSS · nav light"),("F-02","Sensor platform","6061 structure · CAD ref"),("F-03","Solar array","2 × 30 W · candidate"),("F-04","Tapered mast","6061 frame · CAD ref"),("F-05","Electronics pod","UV-HDPE · sealed"),("F-06","Main float / keel","Ø650 · V2 CAD ref"),("F-07","Ballast / mooring","site engineering TBD")]
    yy=838
    for ref,name,note in bom:
        out += [f'<line x1="1525" y1="{yy-15}" x2="1960" y2="{yy-15}" class="thin"/>',f'<text x="1532" y="{yy}" class="code">{ref}</text>',f'<text x="1585" y="{yy}" class="small">{name}</text>',f'<text x="1745" y="{yy}" class="small">{note}</text>']; yy+=18

    # Master dimension register: values come from the Fusion V2 component
    # parameters and its exported CAD envelope, not illustrative subsystem art.
    panel(out,48,990,940,360,"MASTER DIMENSIONS — FUSION V2 CAD REFERENCE")
    out += ['<text x="70" y="1040" class="subhead">ID</text><text x="135" y="1040" class="subhead">FEATURE</text><text x="420" y="1040" class="subhead">FUSION DIMENSION</text><text x="680" y="1040" class="subhead">ENGINEERING STATUS</text>',
            '<line x1="65" y1="1055" x2="970" y2="1055" class="strong"/>']
    dims=[
        ("D01","Complete buoy envelope","760 W × 760 D × 3391 H mm","CAD-export envelope; excludes site mooring run"),
        ("D02","Main float / keel","Ø650 × 620 H mm","380 upper body + 240 tapered keel; 6 mm wall"),
        ("D03","Tapered mast frame","805 H mm envelope","800 mm design height; 4 × Ø32 legs"),
        ("D04","Sealed electronics pod","300 W × 280 D × 400 H mm","8 mm UV-HDPE wall; 18 mm service lid"),
        ("D05","Dual solar modules","2 × 450 × 300 × 20 mm","30 W each; 20° outward tilt"),
        ("D06","Pressure sensor / guard","Ø24 × 42 / Ø64 × 72 mm","Mounting depth and bracket remain approval items"),
        ("D07","Ballast rail / plates","Ø40 × 500; 4 × Ø220 × 25 mm","Final mass, CG and righting test required"),
        ("D08","Concrete anchor reference","650/450 square × 500 H mm","Nominal 367 kg; site engineering approval required"),
    ]
    yy=1085
    for code,feature,dimension,status in dims:
        out += [f'<text x="70" y="{yy}" class="code">{code}</text>',f'<text x="135" y="{yy}" class="text">{feature}</text>',f'<text x="420" y="{yy}" class="text">{dimension}</text>',f'<text x="680" y="{yy}" class="small">{status}</text>',f'<line x1="65" y1="{yy+13}" x2="970" y2="{yy+13}" class="thin"/>']
        yy += 31
    out += ['<text x="70" y="1330" class="warn">DO NOT SCALE DRAWING — VERIFY FINAL FABRICATION DIMENSIONS IN THE NATIVE FUSION PARAMETRIC MODEL</text>']
    panel(out,48,1370,940,300,"COMPONENT / INTERFACE NOTES")
    text_rows(out,70,1410,["S01  HPT604 Type A — provisional 0–2 mH2O, 4–20 mA; supplier seawater confirmation and validation required.","S02  Ultimate GPS PID 746 — position/geofence; UART GPIO16/17; field scatter test required.","S03  SEN-15901 — wind pulse GPIO25 and vane through ADS1115 A0; marine durability unqualified.","H01/H02  MCP9808 + INA260 ×2 — enclosure temperature and battery/solar electrical health.","C01  ESP32-DevKitC V4 — buoy controller; exact LoRa radio remains TBD.","BENCH ONLY  Bar02 R2; current I2C PCB is obsolete for deployment.","EXCLUDED  BNO085, load-cell/HX711, onboard Orange Pi, water temperature and salinity sensors."],34)
    panel(out,1005,990,482,330,"POWER MANAGEMENT")
    out += ['<path d="M1035 1045L1135 1025L1145 1115L1045 1135Z" class="solar"/><path d="M1068 1038l10 90m25-96l10 90m-73-45l100-20m-96 52l100-20" class="thin"/>',
            '<path d="M1190 1040h105v90h-105z" class="hardware"/><rect x="1205" y="1055" width="52" height="30" rx="3" class="box"/><circle cx="1275" cy="1065" r="5" class="strong"/><circle cx="1275" cy="1085" r="5" class="strong"/>',
            '<path d="M1340 1045h120v82h-120z" class="battery"/><path d="M1360 1035h18v10h-18m62-10h18v10h-18" class="strong"/><rect x="1360" y="1065" width="80" height="35" rx="3" class="box"/><text x="1400" y="1088" class="code" text-anchor="middle">LiFePO4</text>',
            '<path d="M1145 1080H1190M1295 1080H1340" class="power"/>','<text x="1090" y="1160" class="subhead" text-anchor="middle">2 × 30 W SOLAR</text><text x="1242" y="1160" class="subhead" text-anchor="middle">MPPT</text><text x="1400" y="1160" class="subhead" text-anchor="middle">12.8 V BATTERY</text>',
            '<path d="M1060 1230h35l8-15 15 30 15-30 15 30 15-15h24m0 0h20l12-14v28l14-14h28m0 0q8-18 16 0q8-18 16 0q8-18 16 0h30" class="strong"/>',
            '<text x="1245" y="1272" class="small" text-anchor="middle">FUSE · TVS · REVERSE POLARITY · DISCONNECT</text>',
            '<text x="1245" y="1290" class="small" text-anchor="middle">5 V BUCK · 3V3 LDO · VBAT / 5V / 3V3 / GND TEST POINTS</text>']
    panel(out,1005,1340,482,330,"WIRING SCHEMATIC OVERVIEW")
    rails=[("I2C SDA / SCL",1420),("GPS UART RX / TX",1470),("WIND PULSE / ADC",1520),("LTE UART / USB",1570),("3V3 / 5V / GND",1620)]
    for lab,y in rails: out += [f'<text x="1025" y="{y}" class="code">{lab}</text>',f'<path d="M1145 {y-4}H1450" class="thin"/>']
    out += ['<path d="M1190 1400V1640M1320 1400V1640" class="strong"/>','<text x="1190" y="1390" class="subhead" text-anchor="middle">ESP32</text><text x="1320" y="1390" class="subhead" text-anchor="middle">PROTECTED I/O</text>',
            '<text x="1245" y="1646" class="small" text-anchor="middle">FUNCTIONAL OVERVIEW ONLY</text>',
            '<text x="1245" y="1660" class="tiny" text-anchor="middle">Use verified KiCad schematic and harness for fabrication</text>']
    panel(out,1505,990,475,680,"MOORING & ANCHORAGE SYSTEM")
    project_iso(out,edges,1535,1040,180,520,named("ANCHOR_CHAIN_LINK","BALLAST_CHAIN_LINK","SHACKLE","SNUBBER"),5000)
    project_iso(out,edges,1740,1110,205,380,named("CONCRETE_MOORING_ANCHOR","ANCHOR_REINFORCED","ANCHOR_316SS_MOORING_EYE"),4500)
    out += ['<text x="1625" y="1580" class="subhead" text-anchor="middle">CHAIN / CONNECTORS</text><text x="1842" y="1580" class="subhead" text-anchor="middle">CONCRETE ANCHOR · CAD REF</text>',
            '<text x="1742" y="1608" class="small" text-anchor="middle">Scope · WLL · corrosion allowance · anchor mass:</text>',
            '<text x="1742" y="1626" class="small" text-anchor="middle">SITE ENGINEERING TBD</text>']

    panel(out,48,1690,1000,285,"GENERAL NOTES")
    text_rows(out,70,1730,["1. CAD linework is projected from PROJECT-FALCON-V2.glb; do not scale this sheet.","2. Project FALCON estimates wave height from submerged pressure time series at the shore Bay Station.","3. Orange Pi / Bay Station computer remains ashore; no single-board computer is installed on the buoy.","4. Verify purchased components, pin 1, voltages, connector orientation, sealing, loads and calibration.","5. Complete flotation, stability, structure, thermal, ingress, corrosion, power and mooring reviews before build."],36)
    out.append('<text x="70" y="1938" class="warn">REFERENCE / NOT FOR FABRICATION</text>')
    panel(out,1065,1690,915,285,"DRAWING CONTROL")
    out += ['<line x1="1065" y1="1770" x2="1980" y2="1770" class="strong"/><line x1="1510" y1="1690" x2="1510" y2="1975" class="strong"/>',
            '<text x="1090" y="1745" class="small">PROJECT</text><text x="1170" y="1745" class="title">FALCON-01</text>',
            '<text x="1535" y="1745" class="small">DRAWING TITLE</text><text x="1665" y="1745" class="head">ASSEMBLY &amp; SUBSYSTEMS</text>',
            '<text x="1090" y="1820" class="small">DRAWING NO.</text><text x="1210" y="1820" class="head">FALCON-BP-000</text><text x="1535" y="1820" class="small">REVISION</text><text x="1640" y="1820" class="head">P5</text>',
            '<text x="1090" y="1870" class="small">SCALE</text><text x="1210" y="1870" class="head">NTS</text><text x="1535" y="1870" class="small">DATE</text><text x="1640" y="1870" class="head">2026-09-04</text>',
            '<text x="1090" y="1920" class="small">SOURCE</text><text x="1210" y="1920" class="text">V2 GLB + CONTROLLED DOCS</text><text x="1535" y="1920" class="small">STATUS</text><text x="1640" y="1920" class="warn">REFERENCE / NOT FOR FABRICATION</text>','</svg>']
    return '\n'.join(out)


def main():
    doc, blob = load_glb(MODEL)
    edges = cad_edges(doc, blob)
    OUT.write_text(drawing(edges), encoding="utf-8")
    print(f"Generated {OUT.relative_to(ROOT)} from {len(edges):,} CAD feature edges")


if __name__ == "__main__":
    main()
