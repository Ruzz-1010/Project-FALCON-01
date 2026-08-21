#!/usr/bin/env python3
"""Generate recognizable offline sample-part models for KiCad 3D Viewer."""
from pathlib import Path

OUT = Path(__file__).with_name("models")
OUT.mkdir(exist_ok=True)
U = 2.54
GREEN, BLUE, BLACK = (0.03, .30, .16), (0.03, .28, .48), (.035, .035, .04)
WHITE, SILVER, GOLD = (.88, .87, .78), (.62, .66, .68), (.78, .52, .08)


def box(size, at, color, shiny=.2):
    sx, sy, sz = (v / U for v in size)
    x, y, z = (v / U for v in at)
    r, g, b = color
    return f'''Transform {{ translation {x:.5f} {y:.5f} {z + sz/2:.5f} children [
 Shape {{ appearance Appearance {{ material Material {{ diffuseColor {r} {g} {b}
 specularColor {shiny} {shiny} {shiny} shininess .35 }} }}
 geometry Box {{ size {sx:.5f} {sy:.5f} {sz:.5f} }} }} ] }}'''


def write(name, shapes):
    (OUT / f"{name}.wrl").write_text(
        "#VRML V2.0 utf8\nGroup { children [\n" + "\n".join(shapes) + "\n] }\n",
        encoding="utf-8")


def pin_row(count, y, height=5.5):
    shapes = [box(((count-1)*2.54+2.2, 2.2, 2.5), (0, y, 1.6), BLACK)]
    for i in range(count):
        shapes.append(box((.55, .55, height), ((i-(count-1)/2)*2.54, y, 1.6), GOLD, .5))
    return shapes


def pin_column(count, x, height=5.5):
    shapes = [box((2.2, (count-1)*2.54+2.2, 2.5), (x, 0, 1.6), BLACK)]
    for i in range(count):
        shapes.append(box((.55, .55, height), (x, (i-(count-1)/2)*2.54, 1.6), GOLD, .5))
    return shapes


# Recognizable module samples: PCB, main package/antenna/connector, and headers.
write("esp32_devkitc", [box((27.9, 48.2, 1.6), (0, 0, 0), GREEN),
 box((18, 25.5, 2.4), (0, 6, 1.6), SILVER, .6),
 box((18, 6, .7), (0, 21, 1.6), (.72, .62, .30)),
 box((8, 6.5, 3), (0, -23, 1.6), SILVER, .7)] +
 pin_column(19, -12.7) + pin_column(19, 12.7))

write("bno085", [box((25.4, 22.86, 1.6), (0, 0, 0), BLUE),
 box((4.5, 4.5, 1), (0, 0, 1.6), BLACK),
 box((6.5, 4, 3), (-8.2, 7.5, 1.6), WHITE), box((6.5, 4, 3), (8.2, 7.5, 1.6), WHITE)] +
 pin_row(6, -8.89) + pin_row(6, 8.89))

write("gps", [box((25.4, 34.29, 1.6), (0, 0, 0), BLUE),
 box((15.2, 15.2, 4), (0, 6, 1.6), (.92, .90, .82), .35),
 box((10, 9, 2), (0, -8, 1.6), SILVER, .6),
 box((7.5, 5, 3), (8, -14, 1.6), BLACK)] + pin_row(9, -15))

write("ina260", [box((22.86, 22.86, 1.6), (0, 0, 0), GREEN),
 box((5, 5, 1.2), (0, 1, 1.6), BLACK),
 box((10, 7, 6), (0, 7, 1.6), (.08, .30, .62)),
 box((6.5, 4, 3), (-7, -7.5, 1.6), WHITE)] + pin_row(8, -9))

write("ads1115", [box((25.4, 17.78, 1.6), (0, 0, 0), GREEN),
 box((4, 4, 1), (0, 0, 1.6), BLACK),
 box((6.5, 4, 3), (-8, 5.8, 1.6), WHITE), box((6.5, 4, 3), (8, 5.8, 1.6), WHITE)] +
 pin_row(6, -6.35) + pin_row(6, 6.35))

write("module_generic", [box((10.16, 10.16, 1.6), (0, 0, 0), (.22, .30, .34)),
 box((6, 6, 3), (0, 0, 1.6), BLACK)])


def jst(name, width, pins):
    shapes = [box((width, 4.25, 5.8), (0, -2.125, 0), WHITE)]
    for i in range(pins):
        shapes.append(box((.45, 3.2, .35), ((i-(pins-1)/2)*1.25, -4.2, 0), SILVER, .6))
    write(name, shapes)


jst("jst_gh_3", 7, 3)
jst("jst_gh_4", 8.25, 4)
write("jst_vh_2", [box((9.8, 9.7, 9.5), (0, 1.15, 0), WHITE),
 box((1.1, 1.1, 11), (-1.98, 0, 0), SILVER, .6), box((1.1, 1.1, 11), (1.98, 0, 0), SILVER, .6)])
write("fan_header", [box((10.4, 5, 3), (0, 0, 0), BLACK)] +
 [box((.65, .65, 8), ((i-1.5)*2.54, 0, 0), GOLD, .5) for i in range(4)])

write("resistor_0603", [box((1.6, .8, .45), (0, 0, 0), (.12, .10, .08)),
 box((.35, .82, .5), (-.63, 0, 0), SILVER, .6), box((.35, .82, .5), (.63, 0, 0), SILVER, .6)])
write("sot23", [box((3, 1.4, 1.1), (0, 0, 0), BLACK)] +
 [box((.45, 1, .2), pos, SILVER, .6) for pos in ((-1, .95, 0), (1, .95, 0), (0, -.95, 0))])
write("sot25", [box((3, 1.7, 1.3), (0, 0, 0), BLACK)] +
 [box((.42, 1, .2), pos, SILVER, .6) for pos in ((-.95, 1.1, 0), (0, 1.1, 0), (.95, 1.1, 0), (-.95, -1.1, 0), (.95, -1.1, 0))])
write("testpoint", [box((2.4, 2.4, .5), (0, 0, 0), GOLD, .7), box((1, 1, 2.5), (0, 0, .5), SILVER, .6)])

print(f"Generated 14 detailed sample-part VRML models in {OUT}")
