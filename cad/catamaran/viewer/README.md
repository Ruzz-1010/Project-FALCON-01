# FALCON-01 — live 3-D buoy (design preview)

Browser viewer for the proposed FALCON-01 catamaran buoy. It is a **design
preview only**, not a fabrication drawing and not a validated buoy.

- `index.html` — three.js viewer (turntable, waves, heeling, live mooring lines,
  wind vane, cup anemometer, flashing marine light)
- `anim_*.stl` — the same STEP geometry split into colour groups used by the
  viewer (pontoon, deck, tube, gps, anchor, metal, whip, panel, rotor, vane,
  lens)
- `falcon_catamaran.step` — the full 91-part STEP export of the layout

Live page: <https://ruzz-1010.github.io/Project-FALCON-01/design/>

Colour scheme: white GRP deck, international-orange pontoons with a white
reflective boot stripe and dark antifouling below the waterline, navy solar
cells, light-grey electronics tube, aluminium hardware, yellow wind vane and an
amber marine light.

The Onshape document holds the same geometry; STEP carries no colour data, so
the palette above lives only in the viewer.

## Regenerating

The CAD builder and splitter are not part of this preview folder. Geometry was
produced with build123d and exported per material group; parameters are in the
project CAD notes.
