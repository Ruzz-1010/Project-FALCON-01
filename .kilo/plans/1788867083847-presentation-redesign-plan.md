# Static Website Presentation Redesign Plan

## Goal

Redesign the FALCON-01 cinematic presentation's visual identity and CSS architecture to create a cohesive, claim-safe, maritime-documentary aesthetic that clearly communicates the **ocean → telemetry → shore processing → AI insight** narrative. The redesign resolves the current CSS inconsistency between `style.css` (token-based) and `bay-station.css` (hardcoded hex, old variables, mismatched selectors).

---

## Current State Assessment

### What works
- Ten-chapter cinematic narrative (Ocean → FALCON → Sensors → ESP32 → LoRa → Bay Station → Wave → AI → Dashboard → Connected) with consistent `SIMULATED`/`ILLUSTRATIVE` labeling
- `tokens.css` provides a structured design-token system (palette, typography, spacing, shadows)
- `style.css` is the new consolidated stylesheet using tokens throughout
- `bay-station.js` creates a 3D cutaway with LoRa RX, shared shore computer, UPS, and monitor
- `bay-story.js` defines six inspection stages (`rx → validate → sqlite → processing → ai → dashboard`)
- `coast.js` builds a fictional coastal community with proper disclaimers
- Telemetry simulation in `story.js` implements real buffer/deduplicate/replay logic
- 10 test files validate structure, state machine, CAD hash, and claim-discipline strings

### What is broken
1. **`bay-station.css` uses a legacy color system** (`var(--sea)`, `var(--gold)`, hardcoded hexes) while `style.css` uses tokens (`var(--accent)`, `var(--warn)`, `--bg-panel`)
2. **`bay-station.css` has duplicate rules** — lines 1–29 (old) and lines 31–89 (partial rewrite) define the same selectors with different values
3. **CSS selectors do not match current HTML** — `bay-station.css` targets `.copy` structure but `index.html` Chapter 05 uses `.bay-intro`, `.shore-system-rail`, `.bay-panel-top`, `.bay-selection-head`, `.bay-step-mark`, `.bay-divider-label`, `.bay-inspect-note`
4. **Multiple chapter-specific CSS files** (`opening-polish.css`, `controller-polish.css`, `home-presentation.css`, `wave-estimation.css`, `bay-station.css`) create fragmentation
5. `style.css` imports `dashboard.css` but its role is unclear

---

## Design Direction

### Theme: "From Ocean Depths to Shore Insights"

The color story represents the physical and conceptual journey:

| Phase | Chapters | Concept | Colors |
|-------|----------|---------|--------|
| Ocean | 00–03 | Deep marine environment, pressure sensing | Deep blues, teal accents |
| Crossing | 04 | Radio transmission gap | Amber warnings, pulse animation |
| Shore | 05–09 | Processing, AI insight, human interface | Warm teal, amber highlights, clean panels |

### Refined Color Palette

```css
:root {
  /* Existing tokens — keep these */
  --bg-deep:      #0a0d10;
  --bg-base:      #10151a;
  --bg-raised:    #161d24;
  --bg-panel:     #1a2229;
  --ink:          #e8edf2;
  --ink-soft:     #b8c2cc;
  --ink-muted:    #7d8894;
  --ink-faint:    #56606b;
  --line:         rgba(255, 255, 255, 0.10);
  --line-strong:  rgba(255, 255, 255, 0.18);

  /* Refined accents */
  --accent:       #4db8c4;   /* ocean data / primary — keep */
  --accent-soft:  rgba(77, 184, 196, 0.14);  /* keep */
  --accent-line:  rgba(77, 184, 196, 0.36);  /* keep */
  --warn:         #d4a056;   /* amber / processing / LoRa packets — keep */
  --warn-soft:    rgba(212, 160, 86, 0.14);  /* keep */
  --fault:        #c4665c;   /* coral / alert — keep */
  --ok:           #6aab7d;   /* green / healthy — keep */

  /* New shore-specific token for Chapter 05 highlights */
  --shore-warm:   #e8d0a8;   /* warm beige-gold for Bay Station intro highlights */

  /* Existing shadows/spacing — keep */
  --shadow-sm:    0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md:    0 8px 24px rgba(0, 0, 0, 0.35);
  --shadow-lg:    0 24px 64px rgba(0, 0, 0, 0.5);
  --radius:       3px;
  --radius-lg:    6px;
}
```

### Typography

- Keep `Inter` as the primary sans-serif — clean, documentary-appropriate
- Keep `IBM Plex Mono` for data readouts, code, and technical labels
- Maintain the existing type scale from `tokens.css` (`--t-2xs` through `--t-4xl`)
- No decorative fonts; preserve the documentary-realistic feel

### Visual Metaphor

- **Chapter 04 (Crossing)**: Use the amber `--warn` color for in-flight LoRa packets, with a dashed border to visually signal "temporary link"
- **Chapter 05 (Bay Station)**: Use `--accent` (teal) for active software stages, `--warn` (amber) for the "receiving" stage, and `--shore-warm` for intro highlights. The cutaway panel should feel like a maritime instrument panel with warm backlit indicators
- **Chapter 06–07 (Wave/AI)**: Use `--accent` for measured data, `--warn` for AI prediction trace (keep the amber distinction)
- **Chapter 08 (Dashboard)**: Present as a physical monitor (amber/green monochrome terminal look with `--accent` and `--warn` text)

---

## Implementation Plan

### Phase 1: CSS Architecture Consolidation (highest priority)

**Task 1 — Merge `bay-station.css` into `style.css`**
- Copy the Chapter 05 rules from `bay-station.css` (lines 31–148, the newer set)
- Rewrite all hardcoded colors and old variables (`var(--sea)`, `var(--gold)`) to use `tokens.css` variables (`var(--accent)`, `var(--warn)`, `--bg-panel`, `--shadow-lg`, `--radius`, etc.)
- Remove duplicate rules from `bay-station.css` lines 1–29 (the old `.coast-ready #shore` block)
- Ensure every CSS selector matches the actual class names in `index.html` Chapter 05

**Task 2 — Delete legacy chapter-specific CSS files**
- Remove `opening-polish.css`, `controller-polish.css`, `home-presentation.css`, `bay-station.css`
- Merge any remaining unique rules into `style.css` (verify nothing is lost by diffing)
- Verify no `<link>` references to deleted files remain in `index.html`

**Task 3 — Resolve `dashboard.css` import**
- Read `dashboard.css` to determine its role
- If it contains only old dashboard presentation styles, delete it and remove the `@import` from `style.css`
- If it contains active rules, migrate them into the token system

**Verification:**
- `npx vite preview` or `npm run preview` — all chapters render correctly
- No browser console errors for missing stylesheets

### Phase 2: Chapter 05 (Bay Station) Visual Refinement

**Task 4 — Rewrite Chapter 05 HTML/CSS to use the new structure**
- Current `index.html` lines 86–117 already have the correct structure — verify CSS matches
- The `bay-intro` section: use `var(--shore-warm)` for the kicker/status indicator dot, `--accent` for the h2
- The `shore-system` card: use `var(--bg-panel)` background, `var(--line)` border, `var(--shadow-lg)` shadow
- The `bay-panel` cutaway: use `var(--bg-raised)` background, `var(--line-strong)` border, `backdrop-filter: blur(10px)`
- The `shore-system-rail` data flow: animate `--accent` color along the path, use `var(--warn)` for the active stage
- The `bay-inspect-cta` button: use `var(--accent-soft)` background, `var(--accent-line)` border on hover

**Task 5 — Update `bay-station.css` selectors to match HTML**
- `.bay-intro-head .kicker` → use `var(--accent)`, `var(--tracking-kicker)`
- `.bay-status` indicator dot → use `var(--accent)` with `box-shadow: 0 0 9px var(--accent)`
- `.bay-sequence` → use `var(--line)` borders, `var(--accent)` numbers
- `.shore-system-rail` → use `var(--accent)` for icons, `var(--ink-muted)` for text
- `.bay-panel-top` → use `var(--accent)` for the kicker
- `.bay-step-mark` → use `var(--accent)` background when active
- `.bay-inspect-note` → use `var(--warn)` border-left

**Task 6 — Add `shore-system-rail` animation (currently missing)**
- In `main.js`, add animation for the rail flow (currently the HTML has the rail but JS doesn't animate it)
- Use `var(--accent)` for the static rail icons, and add a `--active` class on the current stage

**Verification:**
- Inspect Chapter 05 in browser — all elements display correctly
- Bay Station inspection opens with proper framing
- Mobile responsive at 700px breakpoint

### Phase 3: Chapter Consistency Pass

**Task 7 — Audit all chapters for token consistency**
- Chapter 00 (Ocean/Home): uses `--accent` for kicker, `--ink` for headings
- Chapter 04 (Crossing): uses `--warn` for packet animation, `--ink-muted` for status
- Chapter 06 (Wave): uses `--accent` for measured data, `--warn` for calibration warning
- Chapter 07 (AI): uses `--warn` for prediction trace, `--ink-muted` for baseline
- Chapter 08 (Dashboard): uses `--warn` for demo indicator, `--accent` for nav
- Chapter 09 (Connected): uses `--accent` for route dots

**Task 8 — Add `--shore-warm` usage for Chapter 05 distinction**
- Only Chapter 05 should use the warm beige-gold accent
- All other chapters keep the cool teal/amber/fault palette
- This visually reinforces the "arrival at shore" transition

### Phase 4: Testing & Validation

**Task 9 — Run existing test suite**
```bash
npm test
```
All 10 test files must pass. Update tests if CSS selector changes break any assertions.

**Task 10 — Build and preview**
```bash
npm run build
npm run preview
```
Verify production bundle includes all consolidated CSS correctly.

**Task 11 — Browser-based visual QA**
- Test desktop (1920×1080), tablet (768px), and mobile (375px)
- Verify all 10 chapters render correctly
- Verify Bay Station inspection works (click "Inspect", step through stages)
- Verify reduced-motion mode
- Verify WebGL fallback (`<body class="webgl-unavailable">`)

---

## Files to Modify

| File | Action | Reason |
|------|--------|--------|
| `static website presentation/style.css` | Rewrite Chapter 05 section, add `--shore-warm` token | Main consolidated stylesheet |
| `static website presentation/bay-station.css` | Delete or empty — merge into style.css | Legacy file, inconsistent selectors |
| `static website presentation/opening-polish.css` | Delete — merge into style.css | Fragmented chapter CSS |
| `static website presentation/controller-polish.css` | Delete — merge into style.css | Fragmented chapter CSS |
| `static website presentation/home-presentation.css` | Delete — merge into style.css | Fragmented chapter CSS |
| `static website presentation/tokens.css` | Add `--shore-warm` token | New shore-specific accent |
| `static website presentation/index.html` | Update `<link>` tags to remove deleted CSS files | Remove stale references |
| `static website presentation/main.js` | Add rail animation for Chapter 05 | Currently missing |
| `static website presentation/tests/bay.test.mjs` | Update if selectors change | Keep tests green |
| `static website presentation/tests/story.test.mjs` | Verify CSS import assertions still pass | Verify no regressions |

---

## Out of Scope

- Changing the Three.js 3D scene or geometry
- Modifying the telemetry simulation logic in `story.js`
- Adding new chapters or changing the narrative flow
- Implementing actual data fetching or backend integration
- Mobile app or native deployment

---

## Risks

1. **Selector mismatch**: Deleting `bay-station.css` and merging into `style.css` requires careful verification that every class in `index.html` has a matching CSS rule. Mitigation: use browser DevTools to check for unstyled elements.
2. **Test breakage**: Tests check for specific CSS import strings and claim-discipline text. Any CSS changes must preserve these strings. Mitigation: run tests after every CSS change.
3. **Responsive regression**: The current `bay-station.css` has its own media queries. Consolidating requires checking the 700px and 1000px breakpoints match `style.css`. Mitigation: test all breakpoints in browser.
