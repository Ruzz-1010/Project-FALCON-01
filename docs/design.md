# Project FALCON-01 — Design

This file defines the operator dashboard, public dashboard, and physical design
baseline. Updated 2026-11-07. Historical mockups and old CAD renders are
reference only and live in `docs-archive/`.

## 1. Design principles

1. **One primary reading.** Wave height is the headline. Everything else is
   supporting context.
2. **Truth before polish.** Measured, estimated, simulated, stale, and
   unavailable states are visually and verbally distinct.
3. **Measured data dominates.** A forecast tail must never make the measured
   session look like a footnote.
4. **Plain language first.** Technical detail is available, but the first screen
   answers: how is the water, is the buoy safe, is there power?
5. **Calm surface.** Light background, white cards, restrained color, generous
   spacing. Red is reserved for AI estimates and genuine problems.

## 2. Information architecture

Primary navigation:

| Item | Scope |
| --- | --- |
| Overview | Wave, sea condition, AI estimate, chart, wind/pressure/battery/solar |
| Sensors | Grouped sensor readings and states |
| GPS & safety | Fix, position, drift, geofence |
| Alerts & records | Alerts, logs, history, export |
| Settings | Header action, not a sidebar item |

The dashboard is an operator console, not a marketing site. No hero banners,
illustrations, or decorative animation that delays reading data.

The separate `public-dashboard/` is a read-only map, not another operator
console. It shows only station condition, wind, reporting state, and update time.

## 3. Layout

### Desktop (≥ 1180 px)

```text
┌──────────────┬──────────────────────────────────────────────┐
│ navy sidebar │ top bar: title + live-data pill + actions    │
│ brand        ├──────────────────────────────────────────────┤
│ navigation   │ plain status strip (water / safety / power)  │
│              ├───────────────┬───────────┬──────────────────┤
│              │ wave hero     │ sea card  │ AI estimate card │
│              ├───────────────┴───────────┴──────────────────┤
│              │ measured vs AI chart                         │
│              ├──────────┬──────────┬──────────┬─────────────┤
│              │ wind     │ pressure │ battery  │ solar       │
│              ├──────────┴──────────┴──────────┴─────────────┤
│              │ location / enclosure / drift / updated       │
│ online       │ tip lines                                    │
└──────────────┴──────────────────────────────────────────────┘
```

- Sidebar: 272 px expanded, 84 px collapsed, navy gradient.
- Content max width is fluid; cards keep readable line lengths.
- Main content sits directly on the page background, not inside another card.

### Tablet (~ 640–1179 px)

- Hero group stacks into two columns, then one.
- Reading cards become a 2 × 2 grid.
- Sidebar collapses to icon rail below 1000 px.
- Chart keeps at least 320 px of plot width.

### Phone (≤ 639 px)

- Single column.
- Sidebar becomes an off-canvas drawer.
- Top bar hides secondary metadata, keeps title and data-state pill.
- Reading cards stack one per row.
- Footer strip wraps into two columns.
- Chart hides the floating tooltip below 560 px; the latest value remains in
  the hero and the `now` label remains visible.

Verified widths: 1600, 1280, 780, 638, and 390 px.

## 4. Components

### Sidebar

- Navy gradient (`#0a2f40` → `#061b27`), white brand, muted blue-gray labels.
- Active item: translucent cyan fill, cyan icon tile, white text.
- Footer shows service/online state; it must reflect real connectivity.

### Top bar

- Page title on the left, no duplicated in-page `<h1>`.
- Data-state pill on the right: `LIVE` / `SIMULATED` / `STALE` / `OFFLINE`.
- Bell opens Alerts & records; gear opens Settings.
- Sticky behavior must not cover anchors or the mobile drawer.

### Plain status strip

Three compact cells: **Water**, **Safety**, **Power**. Each shows one sentence
or one value. This is orientation, not a second dashboard. On phones it stacks.

### Wave hero

- Left block: navy gradient card, label, very large value with unit, method
  caption (pressure source), and calibration state.
- Center: sea-condition card, pale green, human-readable band.
- Right: AI estimate card, pale blue, value, 15-minute horizon, model name, and About
  explanation.
- Hero values use tabular numerals and do not animate on every poll.

### Chart

- Title names both series: measured wave height and research estimate.
- Measured history: solid blue, filled area, drawn above the AI layer so it
  stays visible during overlap.
- AI estimate: solid red; past AI re-estimates may overlap history.
- Forecast: red line plus soft confidence band.
- Forecast lane is compressed to at most ~24 % of plot width (max ~190 px), so
  a 15-minute projection cannot dwarf a short measured session.
- Future ticks are relative (`+5 min`); history ticks use local clock time.
- Vertical `now` divider with label.
- End label shows predicted value and horizon (`AI in 15 min`).
- Tooltip stays inside the plot, opens left of the now point by default, and is
  suppressed on very narrow charts.
- Footnote states session source, auto-scale, and when the forecast is
  compressed.
- Exactly two legend entries; no duplicate pseudo-element captions.

### Reading cards

Four cards: wind, water pressure, battery, solar. Each has icon tile, label,
large value, note, and state. Cards are white with a thin border and a soft
shadow. Values wrap rather than clip at narrow widths.

### Footer strip and tips

- Footer: geofence location, enclosure temperature, drift, last update.
- Tips explain what the page is for and that presentation values come from the
  simulator when applicable. Tips are not status claims.

## 5. Color

| Token | Value | Use |
| --- | --- | --- |
| `--falcon-bg` | `#f2f6f9` | Page background |
| `--falcon-card` | `#ffffff` | Cards, header |
| `--falcon-ink` | `#0f2b3a` | Primary text |
| `--falcon-ink-soft` | `#5d7484` | Secondary text |
| `--falcon-line` | `#e7eef3` | Borders and dividers |
| `--falcon-blue` | `#2f6fd0` | Measured series |
| `--falcon-red` | `#d92d20` | AI estimate and forecast band |
| `--falcon-teal` | `#0f9fa6` | Brand accent, active navigation |
| `--falcon-green` | `#1a8b5f` | Online / safe |
| `--falcon-amber` | `#b8791b` | Caution / charging |
| Sidebar gradient | `#0a2f40` → `#061b27` | Navigation shell |
| Hero gradient | `#0d3348` → `#175770` | Primary wave card |

Rules:

- Red is not used for measured data or ordinary emphasis.
- Status color is always paired with a text label, never color alone.
- Avoid pure black (`#000`) and pure gray backgrounds; use the ink and line
  tokens.
- Do not introduce a second accent hue without updating this table.

## 6. Typography and spacing

- System sans-serif stack; no external font request.
- Page title: 28–32 px, 700 weight.
- Hero value: 56–72 px depending on width, tabular numerals, 760 weight.
- Card value: ~31 px desktop, smaller on phones.
- Labels: 12–13 px, 650–700 weight.
- Body/notes: 13–15 px, 1.45–1.6 line height.
- Spacing scale: 4, 8, 12, 16, 20, 24, 32 px.
- Radius: 16 px hero, 14 px cards, 10–12 px buttons and chips.
- Shadows are soft and low contrast; no hard drop shadows.

## 7. Motion and interaction

- 150–220 ms transitions for hover, drawer, and theme changes.
- Respect `prefers-reduced-motion: reduce`: disable transforms and looping
  animation.
- Polling updates text in place; do not flash or re-animate the whole card.
- Focus rings must be visible on navy and white surfaces.
- Chart hover/focus updates one tooltip; keyboard arrows move the selected
  measured point.

## 8. Copy rules

- Measured: “Measured”, “reading”, “sensor”.
- Derived: “Estimated wave height”, always with the pressure method nearby.
- AI: “Research estimate”, “model output”, “AI in 15 min”. Never “forecast” as
  an official product, never “prediction” without the AI qualifier.
- Missing: “Unavailable”, with a reason if known. Never show `0` for missing.
- Simulator: “Presentation simulator” or “Demo data”. Never imply field data.
- No claim of deployment, calibration, or accuracy without a dated test record.

## 9. Public dashboard

- Constrain the map to Palawan and prevent zooming out to unrelated regions.
- Use small, legible station markers and a persistent header.
- Demonstration stations: Puerto Princesa, Dumaran, Roxas, and San Vicente.
- A selected-station card shows name, location, simulated/live state,
  pressure-derived condition, wave estimate, wind, and update time.
- Wave motion may illustrate a condition but must remain subtle, realistic,
  reduced-motion compatible, and secondary to exact values.
- Public copy must say test/simulated until hardware endpoints exist and direct
  users to official PAGASA/local advisories for safety decisions.

## 10. Physical design baseline

- Compact single-tube can buoy; low center of gravity.
- Sealed electronics bay above the waterline; serviceable lid.
- Pressure transmitter fixed to an independent seabed/mooring reference, not
  suspended at constant distance below the floating hull.
- Small top section for GPS, antennas, and beacon; no tall mast.
- Six proposed panels arranged around the buoy to limit shading/spray; final
  geometry and 3S2P wiring depend on verified panel/controller ratings.
- The 12.8 V 8 Ah battery and ballast remain low and centered; their placement
  is documented and stability is checked before field use.
- External fasteners and materials selected for saltwater exposure, but
  corrosion resistance is not claimed until tested.

## 11. Non-goals

- Recreating the old large Bay Station enclosure.
- Decorative 3D dashboards or gauges that obscure exact values.
- Dark-mode-first design; light mode is canonical, dark mode must preserve
  contrast and series colors.
