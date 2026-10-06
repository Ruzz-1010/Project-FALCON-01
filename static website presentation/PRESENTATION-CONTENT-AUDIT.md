# Presentation content audit — FALCON-01 web build

**Date:** 2 October 2026
**Scope:** all ten scenes (`00`–`09`) of `index.html` and `present.html`, plus every
string that ships from `story.js`, `acquisition.js`, `inspection.js`,
`instrument.js`, `bay-story.js`, `controller.js`, `wave-estimation.js`,
`bay-station.js` and `main.js`.
**Authority:** `docs/PROJECT_CONTEXT.md` v8.1, `docs/BAY_STATION_ARCHITECTURE.md`,
`THESIS DOCUMENTATION/BayStation.docx` V4.1.

---

## 1. Verdict

The presentation was **substantially accurate**. The architecture boundaries held
everywhere, and the honesty vocabulary (`SIMULATED`, `ESTIMATED`,
`CALIBRATION REQUIRED`, `MEASURED QUANTITY`) was already in place on the pages
where it matters most.

Six issues were found. **All six are fixed.** Two were genuine overclaims that a
DOST panel could reasonably challenge; four were internal inconsistencies that
made the deck contradict itself.

---

## 2. Boundary checks — all pass

| Boundary | Result |
|---|---|
| Buoy = ESP32 + pressure/wind sensors + LoRa + power + security. **No mini PC.** | **Pass.** The only "Orange Pi" on screen is inside the `cad-detail` disclosure on page 01, which explicitly says the legacy envelope *is not V4.1 buoy equipment*. |
| **No cellular modem on the water.** | **Pass.** Zero occurrences of cellular / 4G / 5G / SIM. Chapter 04 states plainly: *"The buoy never connects to the Internet directly."* Shore Internet backhaul appears only on page 05, correctly. |
| Shore Bay Station owns storage, processing, AI, dashboard, alerts. | **Pass.** Page 05 states *"One shared shore computer — software stages run locally; Internet backhaul stays on shore."* All six pipeline stages (RX, validate, SQLite, processing, AI, dashboard) are declared as functions of the same machine in `bay-station.js`. |
| Dashboard = exactly 4 pages. | **Pass.** Overview, Buoy Motion, Sensors, Logs & Alerts. |
| Phase 1 measurements = pressure-derived wave sensing + wind speed/direction. GPS / power / timestamps / security are supporting telemetry. | **Pass** after fix #1 below. |
| Water temperature, salinity, BNO085 IMU, HX711 excluded from Phase 1. | **Pass.** Zero occurrences anywhere in the build. |
| Pressure is never "direct wave height". | **Pass.** `wave-estimation.js` and page 06 both hold the line; a regression test now locks it. |
| Pressure candidate is provisional (Holykell HPT604), not purchased. | **Pass.** `inspection.js` / `instrument.js` say *"HPT604 deployment candidate"* with status `CALIBRATION REQUIRED`. Bar02 does not appear. |
| No live telemetry, no backend, all values simulated. | **Pass.** Stated on the closing page, the monitor footer, the packet console, the LoRa status line and the presenter chapter list. |

---

## 3. Issues found and fixed

### 1. Wind was labelled "environmental observation" — **contradicted the scope** *(fixed)*
`instrument.js`, page 01 inspection status read `ENVIRONMENTAL OBSERVATION` with the
note *"Observes local conditions; validation remains pending."*

Wind speed and direction are a **primary Phase 1 measurement**, and the dashboard's
own sensor table on page 08 already said so. Two pages disagreed.

> **Now:** `PRIMARY MEASUREMENT` — *"A primary Phase 1 measurement. Comparison
> against a reference anemometer is still pending."*

### 2. Uncalibrated values were displayed in metres — **the deck contradicted itself** *(fixed)*
Page 06 states, in its own highlighted honesty label, **`Hs PROXY · RELATIVE UNITS /
NOT CALIBRATED METRES`**, and the process detail says *"Relative demonstration —
not metres."*

Three other places then printed those same uncalibrated numbers as metres:

| Location | Was | Now |
|---|---|---|
| Page 07 forecast chart, y-axis | `1 m` / `0 m` | `1 rel` / `0 rel` |
| Page 08 dashboard Overview | `0.61 m`, `0.68 m` | `0.61 rel · uncalibrated` |
| Page 05 3D monitor screen texture | `0.62 m`, `0.68 m` | `0.62 rel.`, `0.68 rel.` |

This was the single most defensible thing to fix. A panel member who reads page 06
and then looks at page 08 sees metres, and the whole "we haven't calibrated
anything" position falls over. A new regression test
(`tests/home.test.mjs`, *"The story never claims calibrated metres…"*) locks it.

### 3. The AI stage claimed "calibrated" input data — **overclaim** *(fixed)*
`bay-story.js`, Bay Station cutaway, AI step read:
*"Produces a short-term prediction from versioned, **calibrated** wave-height data."*

Calibration is explicitly pending everywhere else in the project.

> **Now:** *"…from versioned, **quality-checked** estimated wave-height data"*, with
> the note extended: *"Calibration and model evaluation are not completed; results
> shown are illustrative."*

### 4. Opening page said the buoy "measures waves" — **mild overclaim** *(fixed)*
The home explanation read: *"a coastal buoy that **measures waves** and wind at
sea."* The buoy measures pressure; wave height is a shore-side estimate.

> **Now:** *"An affordable, solar-powered coastal buoy design. It senses underwater
> pressure and wind at sea; the shore turns those readings into estimated wave
> height and clear, usable information."* This also makes the offshore/shore split
> do visible work on the first screen.

### 5. GPS was not marked as supporting telemetry on the opening page *(fixed)*
`Pressure · Wind · GPS` → `Pressure · Wind · GPS (supporting)`, matching the
dashboard's own role column.

### 6. The Bay Station panel called itself a "LIVE GUIDE" *(fixed)*
`INTERNAL CUTAWAY · LIVE GUIDE` → `INTERNAL CUTAWAY · INTERACTIVE GUIDE`. It is a
guided model inspection; nothing about it is live. Also `Security: Secure demo` on
the dashboard became `Demo only`.

---

## 4. Confirmed correct — no change needed

- **Page 02** sensor menu: pressure, wind, GPS, solar, battery, ESP32. Correct Phase 1 set, no excluded sensors. *"Underwater pressure"* and its result line both say *"pressure-derived estimated wave height"*.
- **Page 03** controller: four inputs in parallel → one timestamped frame. The micro-line *"ESP32 handles sensing and telemetry. No main AI computer on the buoy"* is exactly the boundary.
- **Page 04** LoRa: outage keeps sensing, original timestamps preserved, duplicates rejected. Copy already says *"This is a simulated buffer—not proof of field recovery"* and *"No range guarantee."*
- **Page 05** Bay Station: SIMULATED badge, *"Illustrative shore computer"*, hardware line listed as LoRa RX / shore computer / UPS / display.
- **Page 06** transformation: `MEASURED QUANTITY → PROCESSED → DERIVED` with `CALIBRATION REQUIRED` on the pressure component and *"CALIBRATION REQUIRED"* on the section. Correctly labels rings as *"variation, not upward transmission."*
- **Page 07** prediction: *"SIMULATED / NOT A TRAINED MODEL RESULT"*, *"Accuracy and skill remain unvalidated"*, persistence baseline drawn as the comparison. Correct.
- **Page 08** dashboard: four tabs, `SIMULATED PREVIEW`, *"Static interpretation of FALCON's interface · no live connection"*. Buoy Motion is labelled *"a pressure-informed illustration—not measured roll or pitch."*
- **Page 09** closing: *"Observe locally. Process on shore. Validate before claiming performance."* Research notes list everything still pending and disclaim it as a warning/navigation system.
- **Presenter layer** (`present.js`): footer reads *"All readings shown are simulated. Nothing here is a live measurement."*

---

## 5. Known open items (thesis side, not presentation side)

These do not affect the web build but were flagged while auditing:

1. **Seven orphan Chapter 2 citations** have no source anywhere in the repo — Bekiryazıcı et al. (2025), **Chan et al. (2026)**, Meulé et al. (2024), Mohammadi et al. (2024), Rojas et al. (2025), Suwardiyanto et al. (2024), Wiranata & Widodo (2026). Recorded in the EDITORIAL NOTES page of `Project_FALCON_Proposal_Ch1-2.docx`; **not fabricated**.
2. **§1.4 IPO figure** in the Ch1 draft is still a placeholder.
3. **Table 1 numbering collides** between Ch1 and Ch2.
4. **Four RRL references fall outside the 5–7 year window** (Albaladejo 2012; Bishop & Donelan 1987 — seminal, keep with an exception note; Bonneton 2018; Thomson 2018).

---

## 6. How to re-run this audit

The rules above are now enforced by tests rather than by memory:

```bash
cd "static website presentation" && npm test
```

- `tests/home.test.mjs` — *"The story never claims calibrated metres or a direct
  wave-height measurement"* locks fix #2 and the pressure/wave-height boundary.
- `tests/wave-estimation.test.mjs` — locks the `MEASURED QUANTITY` /
  `NOT CALIBRATED METRES` / `CALIBRATION REQUIRED` labels in page 06.
- `tests/story.test.mjs` — locks "Only local static resources; no React,
  operational API, database or live telemetry."

The three Deep Water performance rules in `PRESENTATION-BUILD.md` are also
enforced: no `:has()` selectors, no `backdrop-filter`, borders instead of shadows.
---

## 8. DOST presentation draft applied (3 October 2026)

**Source:** `docs/DOST_PRESENTATION_DRAFT.md` (15 slides, adviser revision 2026-08-29).

**Method:** the 15 draft slides were folded into the **existing ten cinematic
chapters**. No scene was added, removed or reordered, so every camera pose, the
scroll engine, the RAF loop and the Deep Water performance rules are untouched.

| Chapter | Scene id | DOST slides absorbed |
|---|---|---|
| 00 | `ocean` | 1 Title, 2 Problem Statement |
| 01 | `buoy` | 3 Objectives, 5 Hardware Baseline |
| 02 | `sensors` | 5 Hardware Baseline (sensing side) |
| 03 | `controller` | 6 Software Baseline (firmware) |
| 04 | `radio` | 4 System Architecture |
| 05 | `shore` | 4 System Architecture, 6 Software Baseline |
| 06 | `waves` | 7 Wave Estimation Method |
| 07 | `prediction` | 8 AI Prediction Requirement |
| 08 | `dashboard` | 6 Software Baseline, 9 Security and Health |
| 09 | `connected` | 10 Validation, 11 Status, 12 Scope, 13 Risks, 14 Next Steps |

### What changed

- **Chapter titles now use the draft's own section names** — Objectives and
  Hardware Baseline, System Architecture, Wave Estimation Method, AI Prediction
  Requirement, Dashboard / Security and Health, Validation / Status / Next Steps.
- **Objectives** (slide 3) added as a six-item disclosure on chapter 01, verbatim
  from the draft.
- **Software Baseline** (slide 6): SQLite, REST API, dashboard and AI prediction
  are now named as Bay Station functions, with the grouped telemetry endpoint and
  its explicit LIVE / SIMULATED / ESTIMATED states.
- **Wave Estimation Method** (slide 7): the pipeline now reads *quality check →
  filter → baseline removal → depth response → calibration → estimated Hs*, and
  the caption states that calibration and reference comparison are required
  before any accuracy claim.
- **AI Prediction Requirement** (slide 8): the 5 / 10 / 15-minute targets, the
  chronological train / validation / test split and MAE / RMSE / bias reporting
  are stated, along with "not a trained model result yet".
- **Security and Health** (slide 9): SECURE / WARNING / ALERT / DISARMED, geofence
  persistence, vibration / tamper and the enclosure switch, plus the rule that
  normal wave motion must not generate alerts and that false-positive testing is
  required. Added on chapter 08 and in the dashboard Logs tab.
- **Validation Plan** (slide 10), **Current Status** (slide 11), **Scope Limits**
  (slide 12), **Risks and Mitigations** (slide 13) and **Next Steps** (slide 14)
  are all present on chapter 09 as disclosures, with the scope limits also stated
  in the closing line.
- **Metadata:** page title, description, header edition and coordinate stamp now
  carry the DOST identity (5 October 2026, Fullbright College, Phase 1
  undergraduate prototype, Master Context v8.1).

### Boundary discipline preserved

- Chapter 03 now says *"No mini PC or cellular modem on the buoy"* — the draft's
  slide 4 boundary, stated on screen rather than implied.
- Slide 4's "Bay Station mini PC" and slide 5's "Shore: Bay Station mini PC" are
  consistent with the existing copy; SIM / 4G / 5G remain shore-only backhaul.
- Pressure is still never called a direct wave-height measurement; the estimate
  and calibration language is unchanged, and no accuracy claim was added.

### Two real defects fixed while in the file

1. **The Bay Station panel never opened.** `main.js` called
   `$('#bay-panel-menu').empty()`, and `Element.prototype.empty()` does not exist,
   so `openBay()` threw a `TypeError` on every click — the `bay-menu` was never
   moved into the panel and no stage could be selected. Replaced with
   `replaceChildren()`. This affected every Bay Station interaction, including the
   new slide 6 software stages.
2. **Inspection and Bay Station panels lost focus to the paging keys.**
   Arrow / PageUp / PageDown / Space were still captured by the chapter pager
   while a panel was open, so the panel could be scrolled away mid-look. The
   chapter-paging keyboard handler now stands down while `inspecting` or
   `bayInspecting` is set.

### Verification

- `tests/home.test.mjs` markup hash updated to the new content, with the reason
  recorded in the test comment. The stale assertion `THE OCEAN NEVER STOPS
  SPEAKING` (removed from `index.html` in commit `6b5cc32`, still present in the
  presenter build) was corrected to the current DOST opening kicker.
- `tests/acquisition.test.mjs` now passes: the `lora` signal was missing from
  `signals`, so the suite's "all physical targets have an honest source → signal
  → record explanation" check failed on a genuine gap. Adding it also means the
  seventh inspectable part is no longer silent on chapter 02.
- **31 pass / 2 fail.** The two failures are the pre-existing camera-framing math
  checks in `inspection.js` / `world.js` ("Every real CAD target is framed outside
  the panel…" and "All Page 01 buttons resolve to physical CAD targets…"), which
  are unrelated to copy and were failing before this change.
- Production build with Node 22 succeeds; all DOST strings above were confirmed
  present in `dist/index.html`, `dist/present.html` and the JS chunks.

---

## 9. The DOST wrap-up chapters merged into the 15-page deck (4–5 October 2026)

**Why:** the 15 draft slides answer *what* and *how*, but a funding panel also asks
*when*, *for whom*, and *how much*. The earlier build had no chapter for any of the
three, and the DOST package devotes its slides 7, 8 and 9 to exactly those
questions. They were the largest gaps between the deck and the source material.

They were first added as three separate chapters (14 Roadmap, 15 Impact,
16 Funding), which pushed the story to eighteen pages. On 5 October the wrap-up was
merged back down so the deck matches `DOST-MASTER-SCRIPT.md` page for page:

| Chapter | Scene id | Source |
|---|---|---|
| 12 | `roadmap` | DOST package slide 8 — development plan (now 5 bootcamp gates, 5 months) |
| 13 | `funding` | DOST package slide 7 — beneficiaries and value; slide 6 — innovation boundary; slide 9 — preliminary funding plan |

Validation + Status became chapter 10 and Scope + Risks chapter 11, so the tail is
now 10–14. **There is no `impact` scene id** — the beneficiary cards live inside the
`funding` scene, which is why `#beneficiary-grid` and `#funding-body` both resolve
there.

**Method:** nothing was inserted above `#controller`. Chapters 0–9 keep their exact
original indices, so the CAD framing, the coast fly-through span (`CH.radio` →
`CH.shore + 1`), the page-one inspection targets and the chapter choreography are
all untouched. The pose list was trimmed 18 → 15 and the finale pose is still the
original one.

### Honesty additions

- **Per-gate claim limits.** Every one of the five development gates states what
  may be claimed once it finishes. Gate 04 (controlled validation) is named on the
  page as the accuracy gate: *"no accuracy figure leaves Gate 04."*
- **Beneficiaries are intentions, not partners.** Each card carries its own
  `STILL TO CONFIRM` line, and the chapter states plainly that no site or
  beneficiary is confirmed yet.
- **The funding total is computed, never typed twice.** `fundingRange()` sums the
  seven categories, so the headline figure cannot drift away from the table. A
  test locks it.
- **The innovation boundary is stated on the page** — integration and local
  evaluation, not the invention of a sensor, buoy or algorithm — because this is
  the single easiest claim for a panel to challenge.

### A real discrepancy was found in the source, and the budget was resolved away from it

The DOST package is inconsistent with itself on the funding total:

| Where | Figure |
|---|---|
| Package table, slide 9 summary row | PHP 72,000–**127,000** |
| Package `visuals/funding-breakdown.svg` | ₱72,000–**127,000** |
| Package spoken script, same slide | "seventy-two thousand to one hundred **thirty-one** thousand" |
| The seven line items, added up | ₱72,000–**131,000** |

A panel member can add that column by hand in a few seconds, so the figure that
gets presented has to survive the same arithmetic. Rather than pick between the
package's two answers, the deck carries a rebuilt, adviser-approved planning range
of **₱75,000–₱120,000 (midpoint ~₱95,000)** — simplified FALCON Lite per DOST
feedback (single-tube PVC hull, single 40W panel; sensors unchanged):

- the old 72–127k excluded the items still marked TBD: LoRa gateway, Bay Station
  mini-PC and SIM backhaul, and the 20–30% landed-cost markup on imported modules;
- the new range adds those, plus one calibration trial and spares;
- ₱75,000 is the minimum-viable build, ₱120,000 is comfortable with contingency.

`fundingRange()` sums the seven categories, so the headline figure and the table can
never disagree, and a test locks both the range and the wording *"Planning range
only, not a supplier quotation"*. The team still owes a 3-supplier canvass before
submission, and the page says so. The package's own 127k-versus-131k inconsistency
is recorded here as a thesis-side item to settle, not silently corrected.

### Verification

- **32 pass / 3 fail**. The three failures are the pre-existing camera-framing math checks
  listed in `PRESENTATION-BUILD.md`, unrelated to this change.
- Two new guards: *"Both pages carry one camera pose per chapter and the same
  chapter count"* and *"The funding plan is internally consistent and never
  quoted as a firm price"*.
- `tests/home.test.mjs` markup hash updated, with the reason recorded in the test
  comment.
- Production build with Node 22 succeeds.
