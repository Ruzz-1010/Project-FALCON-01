#!/usr/bin/env python3
"""Generate lightweight offline VRML component envelopes for KiCad 3D Viewer."""

from pathlib import Path


OUT = Path(__file__).with_name("models")
OUT.mkdir(exist_ok=True)


def box_model(name: str, size_mm: tuple[float, float, float], color: tuple[float, float, float]) -> None:
    # KiCad's legacy VRML convention uses 0.1 inch (2.54 mm) model units.
    sx, sy, sz = (value / 2.54 for value in size_mm)
    r, g, b = color
    content = f'''#VRML V2.0 utf8
Transform {{
  translation 0 0 {sz / 2:.6f}
  children [
    Shape {{
      appearance Appearance {{
        material Material {{ diffuseColor {r} {g} {b} specularColor 0.18 0.18 0.18 shininess 0.25 }}
      }}
      geometry Box {{ size {sx:.6f} {sy:.6f} {sz:.6f} }}
    }}
  ]
}}
'''
    (OUT / f"{name}.wrl").write_text(content, encoding="utf-8")


MODELS = {
    "esp32_devkitc": ((27.9, 48.2, 5.8), (0.05, 0.28, 0.18)),
    "bno085": ((25.4, 22.86, 4.6), (0.10, 0.32, 0.42)),
    "gps": ((25.4, 34.29, 6.5), (0.12, 0.38, 0.22)),
    "ina260": ((22.86, 22.86, 7.0), (0.12, 0.38, 0.22)),
    "ads1115": ((25.4, 17.78, 4.6), (0.12, 0.38, 0.22)),
    "module_generic": ((10.16, 10.16, 6.0), (0.28, 0.34, 0.38)),
    "jst_gh_3": ((7.0, 4.25, 7.3), (0.88, 0.86, 0.72)),
    "jst_gh_4": ((8.25, 4.25, 7.3), (0.88, 0.86, 0.72)),
    "jst_vh_2": ((9.8, 9.7, 11.0), (0.92, 0.90, 0.78)),
    "fan_header": ((10.4, 5.0, 8.0), (0.12, 0.12, 0.12)),
    "resistor_0603": ((1.6, 0.8, 0.55), (0.18, 0.18, 0.16)),
    "sot23": ((3.0, 1.4, 1.1), (0.08, 0.08, 0.08)),
    "sot25": ((3.0, 1.7, 1.3), (0.08, 0.08, 0.08)),
    "testpoint": ((2.4, 2.4, 1.0), (0.72, 0.55, 0.12)),
}

for model_name, (dimensions, model_color) in MODELS.items():
    box_model(model_name, dimensions, model_color)

print(f"Generated {len(MODELS)} VRML models in {OUT}")

