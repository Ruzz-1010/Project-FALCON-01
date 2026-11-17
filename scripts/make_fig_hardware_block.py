#!/usr/bin/env python3
"""Generate Figure 2.7 - Hardware Block Diagram of Project FALCON.

Honesty rule for this figure
----------------------------
Only the ESP32 controller platform has been confirmed for procurement.  Every
other block (pressure sensor, wind set, GPS board, LTE module, solar panel,
charge controller, battery, warning light, enclosure and mooring) is still a
candidate.  The drawing therefore marks the ESP32 with a solid border and a
CONFIRMED badge, and draws everything else with a dashed border plus a legend.
Nothing here is presented as built, installed or field-validated.

Output
------
  THESIS DOCUMENTATION/figs/fig-2-7-hardware-block.svg
  THESIS DOCUMENTATION/figs/fig-2-7-hardware-block.png

The caption is NOT drawn inside the image: the DOCX already carries the
paragraph "Figure 2.7. Project FALCON Hardware Block Diagram" underneath it.
"""

from __future__ import annotations

import html
import math
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "THESIS DOCUMENTATION" / "figs"

W, H = 1240, 906
INK = "#000000"
LINE = "#000000"
GREY = "#333333"
WHITE = "#ffffff"
SOFT = "#ffffff"
HILITE = "#ffffff"
FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"

CHECKS: list[tuple[str, float, float]] = []   # (label, needed, available)
RECTS: list[tuple[str, float, float, float, float]] = []


# ---------------------------------------------------------------- primitives
def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _tw(s: str, size: float) -> float:
    """Rough text width in px for a bold-ish sans face."""
    wide = sum(1 for c in s if c in "mwMW@%")
    return (len(s) + wide * 0.55) * size * 0.56


def text_block(cx, cy, lines, size=14, bold=False, fill=INK, lh=None, check=None):
    lines = list(lines)
    lh = lh or (size * 1.34)
    total = lh * len(lines)
    y0 = cy - total / 2 + lh * 0.74
    weight = "bold" if bold else "normal"
    if check:
        CHECKS.append((check, max(_tw(t, size) for t in lines), 0.0))
    out = [f'<text x="{cx:.1f}" y="{y0:.1f}" font-family="{esc(FONT)}" '
           f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
           f'text-anchor="middle">']
    for i, ln in enumerate(lines):
        out.append(f'<tspan x="{cx:.1f}" dy="{0 if i == 0 else lh:.1f}">{esc(ln)}</tspan>')
    out.append("</text>")
    return "".join(out)


def box(x, y, w, h, lines, fill=WHITE, stroke=LINE, sw=1.8, rx=7, size=14,
        bold=False, dash=None, textfill=INK, label=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    RECTS.append((label or f"box@{x:.0f},{y:.0f}", x, y, w, h))
    s = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
         f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>']
    s.append(text_block(x + w / 2, y + h / 2, lines, size=size, bold=bold,
                        fill=textfill, check=label))
    if label:
        need = CHECKS[-1][1]
        CHECKS[-1] = (label, need, w - 20)
    return "".join(s)


def panel(x, y, w, h, heading, dashed=True, fill=SOFT, hd=34):
    """Titled container. Returns (svg, inner_x, inner_y, inner_w, inner_h)."""
    d = ' stroke-dasharray="9 6"' if dashed else ""
    s = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
         f'rx="10" fill="{fill}" stroke="{LINE}" stroke-width="2"{d}/>']
    s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{hd}" '
             f'rx="10" fill="{WHITE}" stroke="{LINE}" stroke-width="2"{d}/>')
    s.append(f'<rect x="{x:.1f}" y="{y + hd - 10:.1f}" width="{w:.1f}" '
             f'height="10" fill="{WHITE}"/>')
    s.append(text_block(x + w / 2, y + hd / 2, [heading], size=13.5, bold=True,
                        check=f"heading:{heading}"))
    if CHECKS:
        lbl, need, _ = CHECKS[-1]
        CHECKS[-1] = (lbl, need, w - 16)
    return "".join(s), (x + 16, y + hd + 12, w - 32, h - hd - 24)


def column_chips(inner, chips, gap=10, size=13):
    ix, iy, iw, ih = inner
    n = len(chips)
    ch = (ih - gap * (n - 1)) / n
    out = []
    for i, c in enumerate(chips):
        y = iy + i * (ch + gap)
        out.append(box(ix, y, iw, ch, c, size=size, label=f"chip:{c[0]}"))
    return "".join(out)


def row_chips(inner, chips, gap=14, size=13):
    ix, iy, iw, ih = inner
    n = len(chips)
    cw = (iw - gap * (n - 1)) / n
    out = []
    for i, c in enumerate(chips):
        x = ix + i * (cw + gap)
        out.append(box(x, iy, cw, ih, c, size=size, label=f"chip:{c[0]}"))
    return "".join(out)


def _head(x, y, ang_deg, color=LINE, size=11):
    a = math.radians(ang_deg)
    bx = x - size * math.cos(a)
    by = y - size * math.sin(a)
    px = -math.sin(a) * (size * 0.44)
    py = math.cos(a) * (size * 0.44)
    return (f'<polygon points="{x:.1f},{y:.1f} {bx + px:.1f},{by + py:.1f} '
            f'{bx - px:.1f},{by - py:.1f}" fill="{WHITE}" stroke="{color}" '
            f'stroke-width="1.6" stroke-linejoin="round"/>')


def arrow(x1, y1, x2, y2, label=None, size=11.5, lx=None, ly=None,
          anchor="middle", sw=1.7):
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    s = [f'<path d="M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}" fill="none" '
         f'stroke="{LINE}" stroke-width="{sw}" stroke-linecap="round"/>',
         _head(x2, y2, ang)]
    if label:
        mx = lx if lx is not None else (x1 + x2) / 2
        my = ly if ly is not None else (y1 + y2) / 2
        wlab = _tw(label, size) + 10
        if anchor == "middle":
            rx = mx - wlab / 2
        else:
            rx = mx - 5
        s.append(f'<rect x="{rx:.1f}" y="{my - size * 0.82:.1f}" '
                 f'width="{wlab:.1f}" height="{size * 1.64:.1f}" fill="{WHITE}"/>')
        s.append(f'<text x="{mx:.1f}" y="{my + size * 0.36:.1f}" '
                 f'font-family="{esc(FONT)}" font-size="{size}" fill="{GREY}" '
                 f'text-anchor="{anchor}">{esc(label)}</text>')
    return "".join(s)


def route(points, label=None, size=11.5, lx=None, ly=None, anchor="middle"):
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
    (ax, ay), (px, py) = points[-1], points[-2]
    ang = math.degrees(math.atan2(ay - py, ax - px))
    s = [f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.7" '
         f'stroke-linecap="round" stroke-linejoin="round"/>', _head(ax, ay, ang)]
    if label:
        wlab = _tw(label, size) + 10
        s.append(f'<rect x="{lx - wlab / 2:.1f}" y="{ly - size * 0.82:.1f}" '
                 f'width="{wlab:.1f}" height="{size * 1.64:.1f}" fill="{WHITE}"/>')
        s.append(f'<text x="{lx:.1f}" y="{ly + size * 0.36:.1f}" '
                 f'font-family="{esc(FONT)}" font-size="{size}" fill="{GREY}" '
                 f'text-anchor="{anchor}">{esc(label)}</text>')
    return "".join(s)


def plain(x, y, text, size=13, bold=False, anchor="middle", fill=GREY):
    w = "bold" if bold else "normal"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{esc(FONT)}" '
            f'font-size="{size}" font-weight="{w}" fill="{fill}" '
            f'text-anchor="{anchor}">{esc(text)}</text>')


# ---------------------------------------------------------------- the figure
def figure() -> str:
    p: list[str] = []

    # title
    p.append(plain(W / 2, 42, "Proposed Hardware Block Diagram of Project FALCON",
                   size=21, bold=True, fill=INK))
    p.append(plain(W / 2, 68,
                   "Only the ESP32 controller is confirmed for procurement; "
                   "all other blocks are proposed or candidate components",
                   size=13.5))

    # legend
    p.append(f'<rect x="404" y="88" width="34" height="18" rx="4" fill="{WHITE}" '
             f'stroke="{LINE}" stroke-width="2"/>')
    p.append(plain(448, 102, "Confirmed for build", size=12.5, anchor="start",
                   fill=INK))
    p.append(f'<rect x="672" y="88" width="34" height="18" rx="4" fill="{WHITE}" '
             f'stroke="{LINE}" stroke-width="2" stroke-dasharray="9 6"/>')
    p.append(plain(716, 102, "Proposed / candidate", size=12.5, anchor="start",
                   fill=INK))

    # ---- sensing block (left column)
    s, inner = panel(30, 150, 300, 310, "Sensing Block (proposed)")
    p.append(s)
    p.append(column_chips(inner, [
        ["Submerged pressure", "sensor (4–20 mA)"],
        ["Anemometer and", "wind vane"],
        ["GPS receiver", "(NEO-6M class)"],
        ["Power monitor", "(INA219 / INA260)"],
    ], gap=9, size=12.5))

    # ---- ESP32 controller (centre, confirmed)
    ex, ey, ew, eh = 390, 250, 320, 190
    p.append(box(ex, ey, ew, eh,
                 ["ESP32", "CONTROLLER",
                  "sampling · calibration",
                  "local record storage",
                  "2-minute summary packet"],
                 fill=HILITE, sw=2.8, size=14.5, label="esp32"))
    CHECKS[-1] = ("esp32", CHECKS[-1][1], ew - 20)
    # CONFIRMED badge on the top edge
    bw = _tw("CONFIRMED", 12) + 26
    p.append(f'<rect x="{ex + ew / 2 - bw / 2:.1f}" y="{ey - 13:.1f}" '
             f'width="{bw:.1f}" height="26" rx="13" fill="{INK}"/>')
    p.append(f'<text x="{ex + ew / 2:.1f}" y="{ey + 5:.1f}" '
             f'font-family="{esc(FONT)}" font-size="12" font-weight="bold" '
             f'fill="{WHITE}" text-anchor="middle">CONFIRMED</text>')

    # ---- communication block (right, top)
    s, inner = panel(800, 150, 380, 170, "Communication Block (proposed)")
    p.append(s)
    p.append(column_chips(inner, [
        ["Wi-Fi path", "(lab / near-shore)"],
        ["LTE module", "(field trial)"],
    ], gap=10, size=12.5))

    # ---- cloud platform (right, below comms)
    s, inner = panel(800, 350, 380, 140, "Cloud Platform (proposed)")
    p.append(s)
    p.append(row_chips(inner, [
        ["Server, database", "and web dashboard", "store · predict · display"],
    ], size=12.5))

    # ---- power block (centre, below ESP32)
    s, inner = panel(390, 500, 320, 190, "Power Block (proposed)")
    p.append(s)
    p.append(column_chips(inner, [
        ["Solar panel", "(10–30 W)"],
        ["Charge controller", "(LiFePO4)"],
        ["Battery", "(LiFePO4 with BMS)"],
    ], gap=9, size=12.5))

    # ---- marine warning light (left, below sensing)
    p.append(box(30, 560, 300, 110,
                 ["Marine warning light", "(proposed)",
                  "alert state from the ESP32"],
                 dash="9 6", size=12.5, label="warning light"))

    # ---- physical integration band (bottom, full width)
    s, inner = panel(30, 720, 1150, 110,
                     "Physical integration (proposed, not a fabrication drawing)")
    p.append(s)
    p.append(row_chips(inner, [
        ["Sealed enclosure, glands", "and pressure-tube routing"],
        ["Float body and ballast", "(compact can buoy)"],
        ["Mooring line, swivel", "and anchor assembly"],
    ], size=12.5))

    # ---- arrows
    p.append(arrow(334, 330, 386, 330, "readings", lx=360, ly=313, size=11))
    p.append(arrow(714, 300, 796, 300, "summary", lx=755, ly=283, size=11))
    p.append(arrow(990, 324, 990, 346, "upload", lx=1000, ly=336,
                   anchor="start", size=11))
    p.append(arrow(550, 496, 550, 444, "regulated DC", lx=562, ly=470,
                   anchor="start", size=11))
    p.append(route([(420, 442), (420, 486), (180, 486), (180, 556)],
                   "alert state", lx=300, ly=487, size=11))

    # ---- note
    p.append(plain(W / 2, 866,
                   "Component choices follow the revised build list; every "
                   "candidate item still has to pass the validation gates "
                   "described in Section 2.2.5.",
                   size=12))
    return "".join(p)


def build_svg() -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}">'
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="{WHITE}"/>'
            f'{figure()}</svg>')


def render(svg_path: Path, png_path: Path) -> str:
    """Render the SVG to PNG with whatever rasteriser this machine has."""
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-w", str(W * 2), "-o", str(png_path),
                        str(svg_path)], check=True)
        return "rsvg-convert"
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path),
                         output_width=W * 2, output_height=H * 2,
                         background_color="white")
        return "cairosvg"
    except Exception:
        pass
    if shutil.which("convert"):
        subprocess.run(["convert", "-density", "192", "-background", "white",
                        "-flatten", str(svg_path), str(png_path)], check=True)
        return "convert"
    return "none"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    svg = build_svg()
    svg_path = OUT / "fig-2-7-hardware-block.svg"
    svg_path.write_text(svg, encoding="utf-8")
    print(f"wrote {svg_path.relative_to(ROOT)} ({len(svg)} bytes)")

    png_path = OUT / "fig-2-7-hardware-block.png"
    tool = render(svg_path, png_path)
    if tool == "none":
        print("no rasteriser found; SVG written only")
    else:
        print(f"rendered with {tool}: {png_path.relative_to(ROOT)} "
              f"({png_path.stat().st_size} bytes)")

    # boxes must not overlap
    over = 0
    for i in range(len(RECTS)):
        n1, x1, y1, w1, h1 = RECTS[i]
        for j in range(i + 1, len(RECTS)):
            n2, x2, y2, w2, h2 = RECTS[j]
            if (x1 < x2 + w2 and x2 < x1 + w1 and
                    y1 < y2 + h2 and y2 < y1 + h1):
                over += 1
                print(f"  ! overlap: {n1} vs {n2}")
    print(f"overlap check: {len(RECTS)} rectangles, {over} overlapping")

    bad = 0
    for label, need, avail in CHECKS:
        if not avail:
            continue
        if need > avail:
            bad += 1
            print(f"  ! text too wide in {label}: needs {need:.0f}px, has {avail:.0f}px")
    print(f"geometry check: {len(CHECKS)} boxes, {bad} with overflowing text")
    return 0 if (bad == 0 and over == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
