# FALCON-01 — material selection for buoyancy

Status: **design aid, first pass.** Indicative prices only — get local quotes
before buying. Nothing here has been built or tested.

Buoyancy does not come from the material. It comes from the **sealed volume**
the hull pushes out of the water: 1 litre of displacement = 1.025 kg of lift in
seawater. The material only decides how much of that lift you spend on the hull
itself, and how long the hull survives sun, salt and impact.

Current design: 2 × Ø260 × 1800 mm capsule hulls = **182 L → 186.5 kg** of
displacement. Realistic all-up mass with the parts list is **≈ 68 kg**, so the
platform floats at about **36 % submerged** with roughly **2.7× margin**. The
material question is therefore about durability and weight, not about whether
it floats.

## 1. Hull material options

| Option | Density | Mass, both hulls (6 mm) | Pros | Cons | Indicative cost |
| --- | --- | --- | --- | --- | --- |
| **HDPE, welded sheet** | 0.95 | ≈ 20 kg with bulkheads | Cheap, tough, no corrosion, weldable, repairable, UV-stable in black | Low stiffness — needs internal bulkheads; thermal expansion; cannot glue, must weld | PHP 6–10k |
| HDPE, rotomolded | 0.95 | ≈ 17 kg | One seamless part, best finish, mass production | Needs a steel mould (PHP 60–150k) — not worth it for one unit | PHP 60k+ tooling |
| GRP over PVC/PU foam core | 1.6–1.8 | ≈ 14 kg | Stiff, light, smooth, repairable | Labour, skill, polyester can blister (use vinyl ester), styrene smell | PHP 15–25k |
| Aluminium 5083-H116, welded | 2.66 | ≈ 20 kg at 4 mm | Stiff, strong, recyclable | Welding skill, galvanic corrosion at stainless fasteners, needs coating | PHP 18–30k |
| 316L stainless | 8.0 | ≈ 45 kg | Very strong, no coating | Heavy (eats 45 kg of your 186 kg), expensive | PHP 60k+ |
| PVC pressure pipe, capped | 1.4 | 25–35 kg | Off-the-shelf, fast | Heavy per litre, brittle in UV, hard to seal caps reliably | PHP 5–8k |
| Steel drum | 7.8 | 40 kg+ | Free/cheap | Rusts through in months, not acceptable | — |

**Recommendation for the thesis prototype: HDPE sheet, 6 mm, welded, with three
internal bulkheads and closed-cell PU foam fill.** It is the only route that a
local fabrication shop can do without a mould, it survives being dragged over
concrete, and a crack can be re-welded with a hot-air gun on site.

For a lighter hull at the same volume, GRP over a 25 mm PVC foam core is the
next step up, but only if you have a laminator you trust.

## 2. Foam fill (unsinkability)

Fill both hulls with **closed-cell PU foam, 40 kg/m³**:

- mass penalty: **≈ 7 kg** for 182 L
- if a hull is holed, the foam still displaces **≈ 179 kg** of water, so the
  buoy stays afloat instead of sinking

Do **not** use open-cell foam, packing peanuts or EPS beads — they absorb water
and lose buoyancy within weeks. Foam must be poured as a 2-part closed-cell kit,
or cut from closed-cell XPS board and sealed in.

## 3. Bill of materials (whole buoy)

### Hulls
| Item | Spec | Qty |
| --- | --- | --- |
| HDPE sheet | 6 mm, UV-stabilised black, 1220 × 2440 mm | 2 sheets |
| HDPE welding rod | Ø3–4 mm, same grade | ≈ 1 kg |
| Internal bulkhead | 6 mm HDPE, Ø260 disc | 6 (3 per hull) |
| Closed-cell PU foam | 2-part, 40 kg/m³ | ≈ 200 L kit |
| Hull seam tape / extruded weld | HDPE | as needed |

### Deck and frame
| Item | Spec | Qty |
| --- | --- | --- |
| Deck plate | 6061-T6, 3 mm, perforated, 1300 × 1120 | 1 |
| Cross beams | 6061-T6 angle 40 × 40 × 3 | 2 × 1110 mm |
| Saddles / brackets | 6061-T6 plate 6 mm | 4 |
| Fasteners | A4-316 M8/M10 bolts, nyloc, washers | ≈ 40 sets |
| Isolation washers | Nylon, between aluminium and stainless | 40 |

### Enclosure and electrical
| Item | Spec | Qty |
| --- | --- | --- |
| Enclosure tube | Ø420 × 360, 8 mm GRP or HDPE | 1 |
| Top cover + hatch | 5 mm cover, 22 mm hatch, EPDM O-ring | 1 set |
| Cable glands | PG9 / PG11 nylon, IP68 | 2 |
| Sealant | Sika 291i or 3M 5200 | 2 tubes |
| Battery | 12.8 V 10 Ah LiFePO4 pack | 4 |
| BMS / fuse / MPPT | 4S 40 A BMS, 30 A fuse, 10 A MPPT | 1 set |

### Solar
| Item | Spec | Qty |
| --- | --- | --- |
| Solar cells | 3 W, 150 × 150 mm (or 5 W) | 6 |
| Frame / rails | 6061-T6 angle 30 × 30 × 2 | ≈ 4 m |
| Cover | 3 mm polycarbonate or tempered glass | 1 |
| Encapsulation | EVA + PET backsheet | — |

### Mooring and anchor
| Item | Spec | Qty |
| --- | --- | --- |
| Mooring line | Nylon 3-strand Ø18 mm (shock absorbing) | 1.5 × depth + scope |
| Chain | Hot-dip galvanised 8 mm | 3–5 m |
| Shackles | 316 A4, 10 mm | 3 |
| Thimble + swivel | 316 | 1 set |
| Anchor | 45 kg concrete block with cast-in 316 eye, or 25 kg Danforth | 1 |
| Transmitter riser | 316 tube Ø50 × 200 | 1 |

### Protection
| Item | Spec | Qty |
| --- | --- | --- |
| Aluminium coating | Chromate-free conversion + 2-part epoxy | 1 kit |
| Antifouling (optional) | Copper-free, for aluminium | 1 L |
| Zinc anodes (if aluminium hull) | 2 × 0.5 kg | 2 |

## 4. Material rules that matter in seawater

1. **HDPE must be UV-stabilised (black, carbon black).** Natural HDPE turns
   chalky and cracks within two years in Philippine sun.
2. **Never bolt aluminium directly to stainless in the splash zone.** Use nylon
   isolating washers and a sealing compound, or the aluminium becomes the anode.
3. **No open-cell foam, no plywood in permanent immersion.** Both absorb water
   and turn into dead weight.
4. **Weld HDPE, do not glue it.** Solvent adhesives do not hold on PE; a hot-air
   welder with HDPE rod does.
5. **Keep stainless fittings small.** 316 is 8× the density of water; every
   bracket is payload.
6. **Foam-fill the hulls.** 7 kg of foam removes the single failure mode that
   sinks the whole thesis.

## 5. If you want more buoyancy

Capsule hull, capacity = 2 × hull volume × 1025 kg/m³:

| Hull | Volume/hull | Capacity | HDPE 6 mm, both | Note |
| --- | --- | --- | --- | --- |
| Ø260 × 1800 (current) | 91.0 L | 186.5 kg | 16.8 kg | 2.7× margin |
| Ø315 × 1800 | 132.1 L | 270.8 kg | 20.3 kg | Same length, more freeboard |
| Ø260 × 2200 | 112.2 L | 230.0 kg | 20.5 kg | Longer deck needed |
| Ø315 × 2200 | 163.3 L | 334.7 kg | 24.8 kg | Heavy-duty version |
| Ø355 × 2200 | 206.0 L | 422.4 kg | 28.0 kg | Overkill for 68 kg |

The shell mass grows slower than the volume, so a bigger diameter is the
cheapest way to gain margin. But more freeboard also means more windage — see
the roll/wind notes in `README.md`.

## 6. Mass correction to the current model

`params.json` budgets **9.5 kg** for the two pontoons. A 6 mm HDPE shell for
this shape is **16.8 kg** before bulkheads and welds; realistic is **≈ 20 kg**.
If you build it that way, the all-up mass goes from 57.4 to **≈ 68 kg**, draft
from 88.5 to **≈ 100 mm**, freeboard to **≈ 160 mm**. Still comfortable
(36 % submerged) but the model should be updated before the numbers are quoted.

## 7. Why the 6-inch PVC test sank

A sealed 6-inch uPVC pipe **cannot** sink on its own — it lifts more than it
weighs. If a test sank, one of three things happened:

1. **It was not sealed.** Open ends, a cap that popped, or a bad solvent joint.
   One litre of water inside cancels one litre of lift.
2. **It was overloaded.** Two 1.8 m lengths of 6-inch pipe only carry ≈ 82 kg
   total. The buoy with the full parts list is ≈ 68 kg *plus* the pipe ≈ 17 kg,
   so the pair is already at its limit.
3. **It was too short.** Capacity scales with length, and lift per metre scales
   with diameter squared.

Lift per metre of sealed pipe (1.025 kg per litre):

| Pipe | L per metre | Lift per metre | Pipe mass | Net lift per metre |
| --- | --- | --- | --- | --- |
| 4" (114 mm) | 10.3 | 10.5 kg | 2.9 kg | 7.7 kg |
| 6" (168 mm) | 22.2 | 22.8 kg | 4.7 kg | 18.1 kg |
| 8" (219 mm) | 37.7 | 38.6 kg | 7.6 kg | 31.0 kg |
| 10" (273 mm) | 58.5 | 60.0 kg | 11.6 kg | 48.4 kg |
| 12" (324 mm) | 82.4 | 84.5 kg | 16.3 kg | 68.1 kg |

Two hulls × 1.8 m:

| Pipe | Capacity | Verdict for a 68 kg buoy |
| --- | --- | --- |
| 6" | 82 kg | ✗ sits almost submerged |
| 8" | 139 kg | ⚠ works, 49 % submerged |
| 10" | 216 kg | ✓ comfortable — this is the current Ø260 design |
| 12" | 304 kg | ✓ lots of margin, more windage |

The current Ø260 mm hull is essentially a 10-inch pipe, which is why the model
floats at ~36 % submerged.

If you still want to test with PVC: use **pressure-rated PN10 pipe** (not thin
sewer pipe), solvent-cement the caps *and* add a mechanical back-up (stainless
screw + sealant), paint it for UV, and foam-fill it. Thin-walled sewer pipe
cracks at the cap under wave shock.

## 8. Before buying anything

1. Get quotes for HDPE sheet, welding rod and foam in your city.
2. Build one hull first, fill it with water and weigh it to confirm 91 L.
3. Do a loaded flotation test in a tank, then in seawater.
4. Heel test with the ballast secured.
5. Check the frame in torsion with the mooring load at the bridle.
