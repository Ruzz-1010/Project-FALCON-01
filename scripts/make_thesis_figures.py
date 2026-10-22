#!/usr/bin/env python3
"""Generate the Chapter 2 thesis figures as SVG files.

Eight figures are produced, all as proposals (nothing is presented as a built or
field-validated system):

  Figure 2.2  System Architecture of Project FALCON
  Figure 2.3  Proposed Hardware Block Diagram
  Figure 2.4  Proposed Software Architecture
  Figure 2.5  Proposed Hardware-Software Integration Diagram
  Figure 2.6  System Flow Chart
  Figure 2.7  Pressure Data Processing Flowchart
  Figure 2.8  AI Prediction Model Workflow
  Figure 2.9  Testing and Validation Workflow

The SVG is rendered to PNG by the browser screenshot step in the same script
when a screenshot driver is unavailable the SVG is left for direct conversion.

Layout is deterministic: every figure is composed from explicit coordinates so
the drawing is reproducible from the script alone.
"""

from __future__ import annotations

import html
from pathlib import Path

OUT = Path("/tmp/opencode/figs")

INK = "#000000"
LINE = "#000000"
BAND = "#ffffff"
SOFT = "#ffffff"
HILITE = "#ffffff"
WHITE = "#ffffff"
GREY = "#000000"

FONT = "Arial, Helvetica, sans-serif"


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def text_block(cx, cy, lines, size=14, bold=False, fill=INK, lh=None, anchor="middle"):
    """Return <text> with centred, wrapped lines."""
    lines = list(lines)
    lh = lh or (size * 1.32)
    total = lh * len(lines)
    y0 = cy - total / 2 + lh * 0.72
    weight = "bold" if bold else "normal"
    out = [f'<text x="{cx:.1f}" y="{y0:.1f}" font-family="{FONT}" font-size="{size}" '
           f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">']
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else lh
        out.append(f'<tspan x="{cx:.1f}" dy="{dy:.1f}">{esc(ln)}</tspan>')
    out.append("</text>")
    return "".join(out)


def box(x, y, w, h, lines, fill=WHITE, stroke=LINE, sw=1.8, rx=6, size=14,
        bold=False, dash=None, textfill=INK):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
         f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>']
    s.append(text_block(x + w / 2, y + h / 2, lines, size=size, bold=bold, fill=textfill))
    return "".join(s)


def lane(x, y, w, h, title, items, fill=SOFT, size=14):
    """A swimlane: header strip on the left, item chips across the lane."""
    hdr_w = 210
    s = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="10" '
         f'fill="{fill}" stroke="{LINE}" stroke-width="2"/>']
    s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{hdr_w}" height="{h:.1f}" rx="10" '
             f'fill="{BAND}" stroke="{LINE}" stroke-width="2"/>')
    s.append(f'<rect x="{x + hdr_w - 12:.1f}" y="{y:.1f}" width="12" height="{h:.1f}" '
             f'fill="{BAND}"/>')
    s.append(text_block(x + hdr_w / 2, y + h / 2, _wrap(title, 17), size=15, bold=True))
    inner_x = x + hdr_w + 26
    inner_w = w - hdr_w - 52
    n = len(items)
    gap = 16
    bw = (inner_w - gap * (n - 1)) / n
    per = max(8, int(bw / (size * 0.54)))
    for i, it in enumerate(items):
        bx = inner_x + i * (bw + gap)
        lines = list(it) if isinstance(it, (list, tuple)) else _wrap(it, per)
        s.append(box(bx, y + 14, bw, h - 28, lines, fill=WHITE, size=size))
    return "".join(s)


def chip(x, y, w, h, lines, fill=WHITE, size=13.5, bold=False, rx=8,
         stroke=LINE, sw=2, dash=None):
    return box(x, y, w, h, lines, fill=fill, stroke=stroke, sw=sw, rx=rx,
               size=size, bold=bold, dash=dash)


def _head(x, y, ang_deg, color=LINE, size=12):
    """Hollow arrowhead: a white wedge outlined in black.

    This matches the adviser's reference flowchart, which uses thin lines with
    open arrowheads rather than solid filled ones.  The wedge fill is white so
    the head stays readable where it meets a box edge.
    """
    import math
    a = math.radians(ang_deg)
    bx = x - size * math.cos(a)
    by = y - size * math.sin(a)
    px = -math.sin(a) * (size * 0.44)
    py = math.cos(a) * (size * 0.44)
    return (f'<polygon points="{x:.1f},{y:.1f} {bx + px:.1f},{by + py:.1f} '
            f'{bx - px:.1f},{by - py:.1f}" fill="{WHITE}" stroke="{color}" '
            f'stroke-width="1.6" stroke-linejoin="round"/>')


def arrow(x1, y1, x2, y2, label=None, color=LINE, sw=1.7, dash=None, lx=None, ly=None,
          size=13, elbow=False, marker="ar"):
    """Straight or single-elbow arrow with an optional label."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    if elbow:
        path = f"M {x1:.1f} {y1:.1f} L {x1:.1f} {y2:.1f} L {x2:.1f} {y2:.1f}"
        ax, ay = x2, y2
    else:
        path = f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"
        ax, ay = x2, y2
    import math
    px, py = (x1, y1) if not elbow else (x1, y2)
    ang = math.degrees(math.atan2(ay - py, ax - px))
    s = [f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d} '
         f'stroke-linecap="round"/>', _head(ax, ay, ang, color)]
    if label:
        mx = lx if lx is not None else (x1 + x2) / 2
        my = ly if ly is not None else (y1 + y2) / 2
        s.append(f'<rect x="{mx - _tw(label, size) / 2 - 5:.1f}" y="{my - size * 0.75:.1f}" '
                 f'width="{_tw(label, size) + 10:.1f}" height="{size * 1.5:.1f}" '
                 f'fill="{WHITE}" stroke="none"/>')
        s.append(f'<text x="{mx:.1f}" y="{my + size * 0.36:.1f}" font-family="{FONT}" '
                 f'font-size="{size}" fill="{GREY}" text-anchor="middle">{esc(label)}</text>')
    return "".join(s)


def diamond(cx, cy, w, h, lines, fill=HILITE, stroke=LINE, size=13):
    pts = f"{cx:.1f},{cy - h / 2:.1f} {cx + w / 2:.1f},{cy:.1f} {cx:.1f},{cy + h / 2:.1f} {cx - w / 2:.1f},{cy:.1f}"
    s = [f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>']
    s.append(text_block(cx, cy, lines, size=size, bold=True))
    return "".join(s)


def plain(x, y, text, size=13, bold=False, anchor="middle", fill=GREY):
    w = "bold" if bold else "normal"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{w}" fill="{fill}" text-anchor="{anchor}">{esc(text)}</text>')


def caption(y, w, text):
    return plain(w / 2, y, text, size=14, bold=True, fill=INK)


def title(w, text, sub=None):
    out = [plain(w / 2, 44, text, size=22, bold=True, fill=INK)]
    if sub:
        out.append(plain(w / 2, 72, sub, size=14, fill=GREY))
    return "".join(out)


def _wrap(text, per):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= per:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def _tw(s, size):
    return len(s) * size * 0.55


def page(width, height, body):
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:#ffffff;}}
#fig{{width:{width}px;height:{height}px;display:block;}}
</style></head><body><svg id="fig" xmlns="http://www.w3.org/2000/svg" \
viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<defs>
<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" \
orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{LINE}"/></marker>
<marker id="arGrey" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" \
orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{GREY}"/></marker>
</defs>
<rect x="0" y="0" width="{width}" height="{height}" fill="{WHITE}"/>
{body}
</svg></body></html>
"""


def group(x, y, w, h, heading, chips, chip_h=52, gap=10, size=13, top_strip=True,
          fill=SOFT):
    """A titled container holding a vertical stack of chips."""
    s = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="10" '
         f'fill="{fill}" stroke="{LINE}" stroke-width="2"/>']
    hd = 34 if top_strip else 0
    if top_strip:
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{hd}" rx="10" '
                 f'fill="{BAND}" stroke="{LINE}" stroke-width="2"/>')
        s.append(f'<rect x="{x:.1f}" y="{y + hd - 12:.1f}" width="{w:.1f}" height="12" '
                 f'fill="{BAND}"/>')
        s.append(text_block(x + w / 2, y + hd / 2, [_wrap(heading, int(w / 8.4))[0]],
                            size=14, bold=True))
    inner_y = y + hd + 12
    avail = h - hd - 24 - gap * (len(chips) - 1)
    if chips:
        ch = min(chip_h, avail / len(chips))
        for i, c in enumerate(chips):
            cy = inner_y + i * (ch + gap)
            lines = list(c) if isinstance(c, (list, tuple)) else _wrap(c, int((w - 40) / (size * 0.54)))
            s.append(box(x + 16, cy, w - 32, ch, lines, fill=WHITE, size=size))
    return "".join(s)


# ==========================================================================
# Figure 2.2 - System Architecture
# ==========================================================================

def fig_2_2() -> str:
    W = 1200
    p = [title(W, "System Architecture of Project FALCON",
               "Four functional layers, with the solar and battery subsystem supplying the buoy")]
    LX, LW, LH = 30, 900, 130
    lanes = [
        (110, "Data Acquisition Layer",
         ["Water-pressure transmitter", "Anemometer and wind vane", "GPS receiver",
          "ESP32 controller"]),
        (286, "Communication Layer",
         ["Wi-Fi for bench and near-shore", "4G/LTE module for a remote trial",
          "Link status, retry and local buffering"]),
        (462, "Cloud Application and Data Layer",
         ["Authenticated ingestion", "Storage and event log",
          "Pressure processing and wave estimation", "Alert service",
          "Isolated prediction"]),
        (638, "Presentation Layer",
         ["Overview", "Buoy Motion", "Sensors", "Logs and Alerts"]),
    ]
    for i, (y, name, items) in enumerate(lanes):
        p.append(lane(LX, y, LW, LH, name, items,
                      fill=SOFT if i % 2 == 0 else WHITE, size=13 if len(items) > 4 else 13.5))
    # vertical connectors with labels in the gaps
    for (y1, y2, lab) in [(240, 286, "validated readings"),
                          (416, 462, "summary and event packets"),
                          (592, 638, "API responses")]:
        p.append(arrow(470, y1, 470, y2))
        p.append(plain(700, (y1 + y2) / 2 + 5, lab, size=13))
    # power subsystem feeding the acquisition layer
    p.append(group(965, 110, 205, 130, "Power Subsystem",
                   ["Solar panel", "Charge controller", "Battery and regulator"], chip_h=32, gap=8))
    p.append(arrow(963, 175, 933, 175, lx=None))
    p.append(caption(792, W, "Figure 2.2.1: System Architecture of Project FALCON"))
    return page(W, 815, "".join(p))


# ==========================================================================
# Figure 2.3 - Hardware block diagram
# ==========================================================================

def fig_2_3() -> str:
    W = 1200
    p = [title(W, "Proposed Hardware Block Diagram of Project FALCON",
               "Proposed equipment grouping inside the buoy body - not a fabrication drawing")]
    # outer buoy body
    p.append(f'<rect x="30" y="100" width="1140" height="545" rx="14" fill="#fbfcfe" '
             f'stroke="{LINE}" stroke-width="2.5" stroke-dasharray="10 7"/>')
    p.append(plain(600, 674, "Buoy body: float, sealed enclosure, mast and mooring (proposed)",
                   size=13))

    p.append(group(55, 125, 295, 400, "Sensing Block",
                   ["Water-pressure transmitter (4-20 mA)",
                    "Anemometer and wind vane",
                    "GPS receiver",
                    "Protected stilling tube"], chip_h=78))
    p.append(group(845, 125, 300, 265, "Communication Block",
                   ["ESP32 Wi-Fi radio (bench path)",
                    "4G/LTE module with antenna and SIM (remote path)"], chip_h=86))
    p.append(group(460, 465, 310, 155, "Power Block",
                   ["Solar panel", "Charge controller, fuse and regulation",
                    "Battery with voltage monitoring"], chip_h=36, gap=8, size=12.5))
    # controller centred
    p.append(box(460, 285, 310, 140,
                 ["ESP32", "CONTROLLER", "acquisition, validation,",
                  "event detection, buffering,", "upload scheduling"],
                 fill=HILITE, size=15, bold=False))

    # sensing -> controller
    p.append(arrow(352, 345, 456, 345, label="4-20 mA / serial", lx=404, ly=328, size=12))
    # controller -> communication
    p.append(arrow(774, 345, 841, 345, label="frames", lx=807, ly=330, size=12))
    # power -> controller
    p.append(arrow(615, 463, 615, 428, label="regulated power", lx=706, ly=448, size=12))
    p.append(caption(724, W, "Figure 2.2.2: Proposed Hardware Block Diagram"))
    return page(W, 754, "".join(p))


# ==========================================================================
# Figure 2.4 - Software architecture
# ==========================================================================

def fig_2_4() -> str:
    W = 1200
    p = [title(W, "Proposed Software Architecture of Project FALCON",
               "Buoy firmware, cloud service, and dashboard - the dashboard reads only the API")]
    p.append(lane(30, 110, 1140, 150, "Buoy Firmware (ESP32)",
                  ["Acquisition loop", "Validation and range checks",
                   "Event detection and debounce", "Telemetry framing",
                   "Local buffer", "Upload scheduling"], fill=SOFT, size=12.5))
    p.append(lane(30, 320, 1140, 150, "Cloud Service",
                  ["Authenticated ingestion", "Data validation", "Storage",
                   "Pressure processing", "Alert service", "REST API",
                   "Isolated prediction"], fill=WHITE, size=12.5))
    p.append(lane(30, 530, 1140, 150, "Dashboard (Front End)",
                  ["Overview", "Buoy Motion", "Sensors", "Logs and Alerts"],
                  fill=SOFT, size=13.5))
    p.append(arrow(600, 260, 600, 320, label="summary and event packets", ly=296))
    p.append(arrow(600, 470, 600, 530, label="HTTPS / REST responses", ly=506))
    p.append(caption(715, W, "Figure 2.2.3: Proposed Software Architecture Diagram"))
    return page(W, 740, "".join(p))


# ==========================================================================
# Figure 2.5 - Hardware-software integration
# ==========================================================================

def fig_2_5() -> str:
    W = 1200
    p = [title(W, "Proposed Hardware-Software Integration Diagram",
               "Where each software task attaches to a physical interface")]
    rows = [
        ("Water-pressure transmitter", "4-20 mA loop", "ADC acquisition and current-to-pressure conversion"),
        ("Anemometer and wind vane", "analogue / pulse", "Wind acquisition and unit conversion"),
        ("GPS receiver", "serial / UART", "Position parsing and geofence check"),
        ("Battery and solar monitor", "divider or monitor", "Voltage monitoring and low-battery rule"),
        ("Wi-Fi and 4G/LTE module", "IP transport", "Link management and upload scheduling"),
        ("microSD or flash buffer", "file / block write", "Buffer write and queued replay"),
    ]
    p.append(plain(265, 105, "PHYSICAL INTERFACE (HARDWARE)", size=14, bold=True, fill=INK))
    p.append(plain(935, 105, "SOFTWARE TASK (FIRMWARE OR SERVICE)", size=14, bold=True, fill=INK))
    y, h, gap = 128, 82, 16
    for i, (hw, proto, sw) in enumerate(rows):
        ry = y + i * (h + gap)
        p.append(box(55, ry, 400, h, _wrap(hw, 30), fill=SOFT, size=14, bold=True))
        p.append(box(745, ry, 400, h, _wrap(sw, 34), fill=WHITE, size=13.5))
        p.append(arrow(463, ry + h / 2, 737, ry + h / 2))
        p.append(plain(600, ry + h / 2 - 12, proto, size=12.5))
    p.append(caption(128 + 6 * 98 + 30, W,
                     "Figure 2.2.4: Proposed Hardware-Software Integration Diagram"))
    return page(W, 128 + 6 * 98 + 60, "".join(p))


# ==========================================================================
# shared flowchart pieces
# ==========================================================================

def fnode(x, y, w, h, lines, size=14, fill=WHITE, stroke=LINE, rx=8, bold=False,
          dash=None):
    return box(x, y, w, h, lines, fill=fill, stroke=stroke, sw=2.2, rx=rx,
               size=size, bold=bold, dash=dash)


def terminus(x, y, w, h, lines, fill=BAND, size=14.5):
    return box(x, y, w, h, lines, fill=fill, stroke=LINE, sw=1.8, rx=h / 2,
               size=size, bold=True)


def route(pts, color=LINE, sw=1.7, dash=None, marker="ar"):
    """Polyline through explicit points with an arrowhead on the final segment."""
    import math
    d = f' stroke-dasharray="{dash}"' if dash else ""
    path = " ".join(("M" if i == 0 else "L") + f" {x:.1f} {y:.1f}"
                    for i, (x, y) in enumerate(pts))
    (ax, ay) = pts[-1]
    (bx, by) = pts[-2] if len(pts) > 1 else pts[0]
    ang = math.degrees(math.atan2(ay - by, ax - bx))
    return (f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d} '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
            + _head(ax, ay, ang, color))


def tag(x, y, text, size=13):
    """Small branch label with a white knockout behind it."""
    w = _tw(text, size) + 8
    return (f'<rect x="{x - w / 2:.1f}" y="{y - size * 0.8:.1f}" width="{w:.1f}" '
            f'height="{size * 1.55:.1f}" fill="{WHITE}"/>'
            f'<text x="{x:.1f}" y="{y + size * 0.38:.1f}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="bold" fill="{GREY}" '
            f'text-anchor="middle">{esc(text)}</text>')


# ==========================================================================
# shared decision-block routing
# ==========================================================================
#
# A decision is always drawn the same way so that the branches read the same in
# every flowchart:
#
#   * the diamond sits in the main column
#   * one branch leaves through the SIDE vertex, gets a Yes/No tag placed just
#     OUTSIDE the diamond (never inside it), and lands on a side box
#   * the other branch leaves through the BOTTOM vertex and is tagged just below
#     the diamond
#   * the side branch rejoins the main line at `rejoin_y`, which is always
#     BETWEEN the bottom tag and the next node, so a tag can never sit on top of
#     a return line
#
# Every arrow is guaranteed to have non-zero length and a positive direction.

DEC_GAP = 96      # diamond bottom -> next node top
DEC_TAG = 22      # diamond bottom -> bottom-branch tag
DEC_REJOIN = 56   # diamond bottom -> horizontal rejoin line


def decision_side(cx, cy, dw, dh, qlines, right, tag_text, box_lines,
                  side_x, side_w, side_h, fill=SOFT, dsize=15, bsize=13.5):
    """Diamond + labelled side exit + side box."""
    out = [diamond(cx, cy, dw, dh, qlines, size=dsize)]
    vx = cx + dw / 2 if right else cx - dw / 2
    ax0 = vx + (8 if right else -8)
    ax1 = (side_x - 8) if right else (side_x + side_w + 8)
    out.append(arrow(ax0, cy, ax1, cy))                     # always L->R or R->L
    out.append(tag((ax0 + ax1) / 2, cy - 19, tag_text))     # above the arrow, outside
    out.append(box(side_x, cy - side_h / 2, side_w, side_h, box_lines, fill=fill, size=bsize))
    return "".join(out)


def bottom_tag(cx, cy, dh, text):
    return tag(cx + 34, cy + dh / 2 + DEC_TAG, text)


def rejoin_line(cx, side_x, side_w, side_bottom, rejoin_y):
    """Side box -> down -> left -> into the main vertical line."""
    scx = side_x + side_w / 2
    return route([(scx, side_bottom), (scx, rejoin_y), (cx, rejoin_y)])


# ==========================================================================
# Figure 2.6 - System flow chart
# ==========================================================================
def fig_2_6() -> str:
    W, X, BW = 1200, 380, 440
    CX = X + BW / 2                      # 600
    p = [title(W, "System Flow Chart of Project FALCON",
               "Sensing is continuous; transmission is conditional")]

    p.append(terminus(X, 110, BW, 54, ["Start - ESP32 begins a sensing cycle"]))
    p.append(arrow(CX, 164, CX, 196))
    p.append(fnode(X, 196, BW, 60, _wrap("Acquire and validate pressure, wind, GPS and power state", 46)))
    p.append(arrow(CX, 256, CX, 288))
    p.append(fnode(X, 288, BW, 60, _wrap("Update the short-window baseline", 46)))
    p.append(arrow(CX, 348, CX, 388))

    # --- decision 1 : threshold crossed? -------------------------------
    dc1y, dh1 = 448, 120
    s1x, s1w, s1h = 880, 290, 64
    p.append(decision_side(CX, dc1y, 340, dh1, ["Threshold", "crossed?"], True, "Yes",
                           ["Send immediate event packet"], s1x, s1w, s1h, fill=HILITE))
    p.append(bottom_tag(CX, dc1y, dh1, "No"))
    p.append(arrow(CX, dc1y + dh1 / 2, CX, 604))
    p.append(rejoin_line(CX, s1x, s1w, dc1y + s1h / 2, dc1y + dh1 / 2 + DEC_REJOIN))

    p.append(fnode(X, 604, BW, 60, _wrap("Accumulate the one-minute summary", 46)))
    p.append(arrow(CX, 664, CX, 704))

    # --- decision 2 : internet available? ------------------------------
    dc2y, dh2 = 764, 120
    s2x, s2w, s2h = 880, 290, 76
    p.append(decision_side(CX, dc2y, 340, dh2, ["Internet", "available?"], True, "No",
                           ["Buffer locally and keep original timestamps"], s2x, s2w, s2h))
    p.append(bottom_tag(CX, dc2y, dh2, "Yes"))
    p.append(arrow(CX, dc2y + dh2 / 2, CX, 920))
    p.append(rejoin_line(CX, s2x, s2w, dc2y + s2h / 2, dc2y + dh2 / 2 + DEC_REJOIN))

    p.append(fnode(X, 920, BW, 60,
                   _wrap("Send the summary; replay queued records after recovery", 46)))
    p.append(arrow(CX, 980, CX, 1016))
    p.append(terminus(X, 1016, BW, 54, ["Sleep until the next sensing cycle"]))

    p.append(plain(CX, 1106, "Every branch preserves the original timestamp of each record.", size=13))
    p.append(caption(1146, W, "Figure 2.2.5: System Flow Chart of Project FALCON"))
    return page(W, 1178, "".join(p))


# ==========================================================================
# Figure 2.7 - Pressure data processing flowchart
# ==========================================================================
def fig_2_7() -> str:
    W, X, BW = 1200, 300, 600
    CX = X + BW / 2                      # 600
    p = [title(W, "Pressure Data Processing Flowchart",
               "The output is always labelled as an estimate, never as a measured wave height")]

    y = 108
    steps = [
        "Acquire the raw analogue value from the current-loop interface",
        "Convert loop current to pressure using the calibrated span",
        "Convert pressure to water-column height using fluid density",
        "Subtract the sensor installation offset to obtain a depth reference",
        "Apply the selected filtering step without erasing wave motion",
    ]
    for i, s in enumerate(steps):
        p.append(fnode(X, y, BW, 58, _wrap(s, 54)))
        p.append(arrow(CX, y + 58, CX, y + 92))       # always reaches the next box top
        y += 92

    dcy, dh = 616, 116                                  # diamond top 558
    lx, lw, lh = 70, 270, 64
    p.append(decision_side(CX, dcy, 360, dh, ["Quality state good?"], False, "No",
                           ["Store null with a non-good state"], lx, lw, lh))
    p.append(bottom_tag(CX, dcy, dh, "Yes"))
    p.append(arrow(CX, dcy + dh / 2, CX, 770))
    p.append(rejoin_line(CX, lx, lw, dcy + lh / 2, dcy + dh / 2 + DEC_REJOIN))

    y = 770
    for s, hl in [("Compute the variation about the short-window baseline", False),
                  ("Derive the estimated wave height from that variation", False),
                  ("Attach timestamp, source, units and quality state", False),
                  ("Store the result, labelled ESTIMATE", True)]:
        p.append(fnode(X, y, BW, 58, _wrap(s, 54), fill=HILITE if hl else WHITE))
        p.append(arrow(CX, y + 58, CX, y + 92))
        y += 92

    p.append(plain(CX, y - 4, "A failed check stores null; a value is never silently replaced.", size=13))
    p.append(caption(y + 34, W, "Figure 2.5.1: Pressure Data Processing Flowchart"))
    return page(W, y + 64, "".join(p))


# ==========================================================================
# Figure 2.8 - AI prediction model workflow
# ==========================================================================
def fig_2_8() -> str:
    W, X, BW = 1200, 330, 540
    CX = X + BW / 2                      # 600
    p = [title(W, "AI Prediction Model Workflow",
               "Research baseline - not yet a trained or field-validated model")]

    y = 108
    for s in ["Read the stored series of estimated wave heights",
              "Prepare records: drop non-good values and enforce minimum history"]:
        p.append(fnode(X, y, BW, 58, _wrap(s, 50)))
        p.append(arrow(CX, y + 58, CX, y + 92))
        y += 92                                                # ends at 292

    dcy, dh = 355, 126
    rx, rw, rh = 900, 270, 76
    p.append(decision_side(CX, dcy, 400, dh, ["Eight or more", "valid records?"], True, "No",
                           ["Return the COLLECTING state", "and show no estimate"], rx, rw, rh))
    p.append(bottom_tag(CX, dcy, dh, "Yes"))
    p.append(arrow(CX, dcy + dh / 2, CX, 514))
    p.append(rejoin_line(CX, rx, rw, dcy + rh / 2, dcy + dh / 2 + DEC_REJOIN))

    y = 514
    for s in ["Produce the 5, 10 or 15-minute short-term estimate",
              "Attach the expected condition, confidence and input label",
              "Display on Overview and write a versioned evaluation record"]:
        p.append(fnode(X, y, BW, 58, _wrap(s, 50)))
        p.append(arrow(CX, y + 58, CX, y + 92))
        y += 92

    p.append(box(150, y, 900, 86,
                 _wrap("Validation gate: calibrated live data, an explicit training / "
                       "validation / test separation, and comparison against the "
                       "damped-trend baseline are required before any prediction "
                       "accuracy may be reported.", 74),
                 fill=SOFT, stroke=GREY, sw=2, size=13.5, dash="8 6"))
    p.append(caption(y + 134, W, "Figure 2.5.2: AI Prediction Model Workflow"))
    return page(W, y + 164, "".join(p))


# ==========================================================================
# Figure 2.9 - Testing and validation workflow
# ==========================================================================
def fig_2_9() -> str:
    W, X, BW = 1200, 260, 640
    CX = X + BW / 2                      # 580
    p = [title(W, "Testing and Validation Workflow",
               "Proposed methods - no round has been executed as a completed validation")]

    steps = [
        "Record the configuration and software version under test",
        "Inspect the enclosure and leak-check seals, glands and hatch",
        "Calibrate sensors and compare them against a reference",
        "Bench test on a stable power supply",
        "Controlled-water test with a measured water column",
        "Communication and power tests, including outage and recovery",
        "Score the results against the criteria in Section 2.6.3",
    ]
    y = 106
    for i, s in enumerate(steps, start=1):
        wl = _wrap(s, 48)
        p.append(fnode(X, y, BW, 56, [f"{i}.  {wl[0]}"] + ["      " + t for t in wl[1:]], size=14))
        if i < len(steps):
            p.append(arrow(CX, y + 56, CX, y + 88))
        y += 88                                                # ends at 722

    dcy, dh = 792, 124                                        # diamond top 730
    lx, lw, lh = 70, 280, 76
    p.append(decision_side(CX, dcy, 340, dh, ["All criteria", "met?"], False, "No",
                           ["Return to design, calibration", "or firmware and retest"],
                           lx, lw, lh))
    p.append(bottom_tag(CX, dcy, dh, "Yes"))
    p.append(arrow(CX, dcy + dh / 2, CX, 950))
    # the No branch loops BACK to step 4 instead of rejoining
    loop_y = 370 + 28
    p.append(route([(lx + lw / 2, dcy + lh / 2), (lx + lw / 2, 880), (30, 880),
                    (30, loop_y), (X - 6, loop_y)]))
    p.append(tag(X + 96, 902, "retest from step 4", size=12.5))

    p.append(fnode(X, 950, BW, 60,
                   ["Record a dated test round and proceed to the next stage"], fill=HILITE))
    p.append(plain(CX, 1042,
                   "A conditional or fail status returns the work to the relevant stage.",
                   size=13))
    p.append(caption(1082, W, "Figure 2.6.1: Testing and Validation Workflow"))
    return page(W, 1114, "".join(p))


# ==========================================================================
# main
# ==========================================================================

FIGURES = {
    "fig-2-2-system-architecture": fig_2_2,
    "fig-2-3-hardware-block": fig_2_3,
    "fig-2-4-software-architecture": fig_2_4,
    "fig-2-5-hw-sw-integration": fig_2_5,
    "fig-2-6-system-flow": fig_2_6,
    "fig-2-7-pressure-flow": fig_2_7,
    "fig-2-8-ai-workflow": fig_2_8,
    "fig-2-9-testing-workflow": fig_2_9,
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in FIGURES.items():
        path = OUT / f"{name}.html"
        path.write_text(fn(), encoding="utf-8")
        print(f"  wrote {path.name}")
    print(f"{len(FIGURES)} figures in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


