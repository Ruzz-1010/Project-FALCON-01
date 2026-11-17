# FALCON-01 — Catamaran build sheet for Onshape (revision 4)

Status: **design aid, first pass.** Not a fabrication drawing. Every number
below is a starting point to be replaced by measured component data.

Revision 2 (2026-11-08) enlarges the hull to carry the final component list in
`THESIS DOCUMENTATION/FALCON Sensor Approval List for Panel.docx`: 6× 3 W panel
(3S2P), 12.8 V LiFePO4, ESP32 + ADS1115 + INA260 + LTE, and a **seabed anchor
carrying the 4–20 mA pressure transmitter**. Revision 3 hollows the enclosure
and carries the internal fit-out: **4 × 10 Ah packs (40 Ah / 512 Wh)**, BMS,
fuse, MPPT, electronics tray and the logger boards. Revision 4 (2026-11-09)
moves to **12-inch hulls (Ø324 × 2200 mm uPVC pipe)**, stretches the deck to
**1700 × 1320 mm** and switches it to a **6 mm moulded GRP sandwich**.

Source of the numbers: `falcon_catamaran.py` + `params.json` in this folder.
Re-run the script after any change and compare the hydrostatics.

## Design waterline (the reference everything is measured from)

| Quantity | Revisions 1–3 | **Revision 4** |
| --- | --- | --- |
| Pontoons | 2 × Ø220 × 1500 → Ø260 × 1800 mm | **2 × Ø324 × 2200 mm (12-inch)** |
| Beam (c/c) | 840 → 950 mm | **950 mm** |
| Deck | 1100 × 1000 × 3 → 1300 × 1120 × 3 mm | **1700 × 1320 × 6 mm GRP** |
| Battery bank | 12.8 V 10 Ah → 40 Ah (4 × 10 Ah) | **unchanged** |
| All-up mass (estimate) | 30.4 → 57.4 kg | **122.6 kg** |
| Displacement capacity, fully immersed | 111.2 → 186.5 kg | **353.6 kg** |
| Draft | 68.7 → 88.5 mm | **120.5 mm** |
| Freeboard above waterline | 151.3 → 171.5 mm | **203.5 mm** |
| Submerged | 31.2 → 34.1 % | **37.2 %** |
| Reserve buoyancy | 72.7 → 69.2 % | **65.3 %** |
| Waterplane area | 0.593 → 0.859 m² | **1.331 m²** |
| BM | 3.60 → 3.54 m | **2.60 m** |
| KB / KG | 0.040/0.242 → 0.052/0.366 m | **0.070 / 0.283 m** |
| GM (small angle) | 3.39 → 3.22 m | **2.39 m** |
| Roll period (crude estimate) | 0.46 → 0.53 s | **0.62 s** |

What changed in the revision 4 mass budget: the two hulls are now 12-inch uPVC
pressure pipe, **71.7 kg** (16.3 kg/m × 4.4 m), and the deck is a 1700 × 1320 ×
6 mm moulded GRP sandwich at **12.0 kg**. Beams and saddles grow with the span
to **6.0 kg**. Everything else is carried over from revision 3: enclosure 4.8,
battery 4.5, boards 1.2, MPPT 0.5, panels 2.6, mast and sensors 2.8, misc 1.5,
trim ballast 3.0, mooring vertical load 12.0 kg.

What changed in revision 3: the enclosure is counted as its own item (4.8 kg
with its top cover, instead of a 2.0 kg placeholder that hid the electronics),
the single 10 Ah battery became **four 10 Ah packs (4.5 kg with BMS and
fuse)**, and the boards, tray, terminal blocks and controller add another
1.7 kg.

What changed in revision 2: the deck grew (6.0 → 10.0 kg), the pontoons grew
(6.4 → 9.5 kg), the frame went to two full-width cross beams (3.5 → 5.0 kg),
3 kg of trim ballast was added low in the pontoon bilge, and **12.0 kg of
mooring vertical load** (anchor + rope, taut worst case) is counted as buoy
load. The transmitter itself hangs on the anchor, so only the line tension is
carried by the buoy.

Two things this still reveals, and they matter for the panel:

1. **The platform is still stiff, but it is a real roll now.** GM 2.39 m at
   122.6 kg gives a 0.62 s period — quick, but no longer the half-second snap of
   revision 3. The 12-inch hulls and the heavier deck did most of the work. To
   calm it further, move mass lower (ballast in the pontoon bilge) or reduce the
   waterplane.
2. **203 mm of freeboard on a 324 mm hull** is a lot of windage, and 12 kg of
   GRP deck sits high up. Wind will push the platform more than the mooring
   geometry suggests.

Both are first-pass numbers, but they are the right conversation to have
before cutting material.

## Coordinate convention

Model in **millimetres**, with **Y up**.

- `X` = longitudinal along the hulls (bow +X, stern −X)
- `Z` = transverse (port −Z, starboard +Z)
- `Y = 0` = **waterline**
- Keel at `Y = −120`, hull top at `Y = +204`, seabed reference at `Y = −2000`

## Part Studio 1 — `PONTOON`

1. **Sketch** on the **Right** plane.
2. Circle, diameter **324 mm**, centre at `Y = 0`, `Z = −475`.
3. **Extrude** → symmetric → **1876 mm**.
4. **Fillet** the two circular end edges, radius **162 mm** → capsule,
   total length **2200 mm**.
5. **Mirror** the part about the **Top** plane → second pontoon at `Z = +475`.

Result: 2 × Ø324 × 2200 capsule, centres 950 mm apart, 71.7 kg as 12-inch uPVC
pipe. The capsule shape is a fairing assumption; a real pipe is a straight
cylinder with flat caps. Keep the capsule for the float study, and model flat
caps when you cut material — the difference is about 3.5 % of hull volume.

## Part Studio 2 — `DECK`

1. Create a plane offset **339 mm** above the Top plane (deck underside).
2. **Sketch** rectangle **1700 mm (X) × 1320 mm (Z)**, centred on the origin.
3. **Extrude** **6 mm** upward. Material: moulded **GRP sandwich** — 2 mm
   laminate / 12 mm PVC foam core / 2 mm laminate fairing to 6 mm nominal, with
   two ribs under the tube footprint. Gelcoat on top, flow-coat underneath.
4. **Slots** — sketch on the deck top face:
   - rounded slot **90 mm (X) × 78 mm (Z)**, corner radius **14 mm**
   - **Linear pattern**: pitch **128 mm** in X, **124 mm** in Z
   - leave **80 mm** solid edge margin and a solid strip **±80 mm** around
     `X = ±544` (the cross beams), plus a clear disc of **Ø480 mm** around the
     enclosure (pod flange and mast/GPS/antenna load path), and clear pads for
     the mast foot (`X = −500`), GPS post (`X = −380`, `Z = +300`) and antenna
     whip (`X = +520`, `Z = −480`)
5. **Extrude → Remove → Through all** the slot sketch.

The deck is the part that changed most in revision 4. At 1700 × 1320 mm, a 3 mm
sheet would oil-can underfoot between the beams; that is why it is a 6 mm
sandwich with ribs, not a flat plate.

## Part Studio 3 — `FRAME`

All members: **6061-T6** or **316 stainless**, protected.

| Part | Size | Position |
| --- | --- | --- |
| Cross beam ×2 | 90 × 55 × 1210 mm | `X = ±544`, `Z = 0`, under deck |
| Pontoon saddle ×4 | 160 × 80 × 190 mm | `X = ±544`, `Z = ±475`, on hull top |
| Pod flange ×4 | 40 × 40 × 5 mm | under pod, on deck |

`±544` is 32 % of the deck length, the same proportion revision 3 used. The
beams must overhang the saddle centres by ~105 mm each side, hence 1210 mm, not
the 1110 mm of the shorter deck. Saddle height is set by the gap between hull
top (`Y = 204`) and beam underside (`Y = 284`) — 80 mm.

## Part Studio 4 — `POD`, mast and solar array

| Part | Size | Position |
| --- | --- | --- |
| Dry enclosure (round), hollow | Ø420 × 360 mm, 8 mm wall | centred on deck top, `Y = 345 → 705` |
| Enclosure bulkhead | Ø408 × 10 mm | `Y = 345 → 355` |
| Foot flange | Ø480 × 26 mm | `Y = 345 → 371` |
| Enclosure top cover | Ø420 × 5 mm | `Y = 705 → 710` |
| Bolted top hatch | Ø396 × 22 mm | `Y = 710 → 732` |
| Solar cell ×6 (3S2P) | 150 × 10 × 150 mm | 3 columns × 2 rows, 12 mm gaps |
| Array envelope | 474 × 312 mm | frame at `Y = 830`, tilt **−10°** |
| Panel rails | 30 × 30 mm | around the array, tilted with it |
| Panel posts ×2 | 30 × 30 mm | collar up to the frame |
| Mast | Ø36 × 620 mm | `X = −500`, `Z = 0`, from deck top (aft) |
| Wind sensor head | Ø52 × 65 mm | on mast top (`Y ≈ 900`) |
| GNSS puck | Ø100 × 30 mm | deck, `X = −380`, `Z = +300` |
| LTE antenna | Ø18 × 350 mm | deck, `X = +520`, `Z = −480` |
| Beacon | Ø60 × 90 mm | mast head, `Y ≈ 965` |

## Part Studio 4b — `INTERNALS` (inside the Ø404 cavity)

Everything below sits on the bulkhead and must stay inside a **202 mm radius**.

| Part | Size | Position |
| --- | --- | --- |
| Battery pack ×4 | 150 × 65 × 100 mm | `X = ±85`, `Z = ±60`, bottom at `Y = 360` |
| BMS | 120 × 20 × 40 mm | `Z = −120`, on top of the packs |
| Main fuse block | 60 × 30 × 40 mm | `X = +150`, on top of the packs |
| MPPT charge controller | 110 × 30 × 70 mm | `Z = +120`, on top of the packs |
| Electronics tray | Ø280 × 6 mm | `Y ≈ 467` |
| ESP32 board | 70 × 12 × 55 mm | tray top, `X = −60`, `Z = +60` |
| ADS1115 board | 30 × 8 × 22 mm | tray top, `Z = +95` |
| INA260 board | 25 × 8 × 18 mm | tray top, `Z = +95` |
| LTE modem board | 90 × 12 × 60 mm | tray top, `X = +65`, `Z = −50` |
| SD logger board | 45 × 8 × 35 mm | tray top, `X = −40`, `Z = −95` |
| Terminal block | 60 × 25 × 30 mm | tray top, `X = +105`, `Z = +60` |
| Desiccant box | 70 mm cube | tray top, `X = −100`, `Z = −70` |
| Cable gland ×2 | Ø24 × 34 mm | through the top hatch, `X = ±100` |

Battery wiring: 4 packs in parallel (4S BMS inside each pack) to a bus at the
terminal block, then main fuse → MPPT → load. Keep the packs low in the tube:
they are 4.5 kg of the highest-density mass in the buoy and lowering them is
the cheapest way to calm the roll.

## Part Studio 5 — `ANCHOR` (seabed reference)

The pressure transmitter is **not** suspended from the buoy. It is fixed to the
anchor on the seabed, exactly as the approval list requires.

| Part | Size | Position |
| --- | --- | --- |
| Concrete anchor block | 360 × 200 × 260 mm (L × H × W) | top face at `Y = −2000`, `X = 0` |
| Lifting eye | Ø70 × 60 mm | on block top |
| Transmitter riser post | Ø50 × 200 mm | block top, `Z = +100` |
| SS316 transmitter | Ø76 × 200 mm | on the riser, `Z = +100` |
| Transmitter cable | Ø10 mm | from transmitter head up to the deck underside |
| Mooring line | Ø18 mm | deck bridle down to the anchor eye, `X = 0` |
| Bridle plate | 200 × 20 × 200 mm | deck **underside**, `X = 0` |

`Y = −2000` is a **schematic** depth. Set it to the real site depth (with scope)
before the mooring is sized.

## Assembly

1. Insert every Part Studio as a part.
2. **Group** the parts that never move relative to each other.
3. Mate the pontoon sub-assembly to the frame with **Fastened** mates.
4. Keep the anchor as a separate sub-assembly joined only by the mooring line —
   it must be free to sit on the seabed while the buoy heaves.
5. Add a **Mate connector** at the bow bridle for the mooring.

## Export

| Purpose | Format | Where |
| --- | --- | --- |
| 3D print / fabricator quote | **STL** (fine, mm) | Part right-click → Export |
| CNC / machine shop | **STEP** | Part right-click → Export |
| Dashboard digital twin | **GLB** | Export STL → convert in Blender |

## Before you trust any of it

- Replace every mass in `params.json` with a measured value.
- Confirm the mooring vertical load; it is currently a 12 kg worst-case guess.
- Do a loaded flotation test in a tank, then in seawater.
- Do a heel/righting test with secured ballast.
- Confirm the deck frame in torsion — the catamaran's weak point is the
  cross-beam joints, not the floats.

## Onshape Free plan warning

Free-plan documents are **public by default** — anyone with the link can open
and copy them. If this thesis is not meant to be public before defense, either
keep the real geometry in a private document, or accept that it is visible.
