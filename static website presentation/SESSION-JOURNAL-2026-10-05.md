# FALCON-01 Session Journal — 2026-10-03 → 2026-10-05

Full chronological log of this conversation (planning + build). Raw chat has no
export button — this file + SESSION-NOTES-2026-10-05.md (technical recap) are
the save points. For verbatim text, copy/paste from the chat window.

---

## PART 1 — PLANNING (read-only phase)

### 1. Goal setting
User: polish the static website presentation into an interactive, presentable
thesis project proposal for a DOST funding proposal; use thesis docs + docx for
validated content; address everything missing; then clean up unnecessary files.

### 2. Budget Q&A — "90k to 150k, enough for current scope?"
Analysis from `docs/HARDWARE_BOM.md` (PHP 61.71/USD raw) + `POWER_CALCULATIONS.md`:
- Known core (~11–12k) + supporting (~4k) + power (~16–37k) = ~38–68k landed
- TBD big tickets: LoRa gateway 5–15k · mini-PC + SIM 15–30k · hull 15–28k ·
  mooring 7–14k · calibration/trials 10–20k · transport/contingency 9–18k
- Verdict: YES, 90–150k fits. 90k = minimum-viable (risky), 115k = defensible
  midpoint to present, 150k = comfortable with spares + 2nd trial.
- Old DOST package said 72–127k but excluded TBDs and markup — superseded.

### 3. Timeline Q&A — adviser says 4–5 months "kung bibigyan ng pansin"
- `docs/ROADMAP.md` = 5 gates, no durations; old DOST package = 8–12 mo (padded).
- Verdict: 5 months / 20 weeks credible IF scope frozen + procurement Week 1 +
  parallel permits. 4 months = stretch goal.
- 5-gate Gantt agreed: M1 freeze+procure · M2 bench · M3 calibrate+software ·
  M4 controlled validation (Gate 04 = accuracy gate) · M5 coastal trial + thesis.

### 4. Bootcamp + OJT plan (user's idea)
- One dorm, full focus after OJT/school. Plan: DOST as OJT host, half-thesis
  half-OJT (AM OJT / PM thesis / Sat build day / Sun docs).
- Framing for DOST: constraint turned into alignment ("thesis habang OJT sa inyo").
- 5-point ask list prepared for the DOST meeting (accept as OJT project, 50/50
  split, mentor + bench/site access, trial support, co-own data).

### 5. Mentors
- Confirmed: Sir Jam (papers), Sir Jeff (hardware). 3rd (SW/AI or DOST) — sourcing.
- Slide shows 3rd as "TBD · sourcing" with desired profile (honest, not blank).

### 6. Team roles (locked after clarifications)
- Jhon Ruzzel Correa — Hardware + Power + LoRa firmware
- Mayla Bacaltos + Gina Caballero — Thesis papers (hati)
- Gwyn Isabel Enriquez — Edge + AI + Dashboard

### 7. 15-page structure (user: "gawin mong 15 page", keep 3D buoy inspect + Bay Station + smooth animation)
Agreed outline: Hero → Problem → Objectives → Buoy → Inspect → Sensors+Power →
ESP32 → LIVE LINK (new merged buoy↔Bay) → Bay cutaway → Wave lab → AI →
Dashboard+Validation → Budget → Timeline+Gantt+Team → Risks+Ask+QR.
Smooth spec: eased scroll tween + lerp cameras, no snap cuts, reduced-motion
fallback, 200ms key debounce, `?big=1` projector mode.

---

## PART 2 — BUILD

### 8. Site broke (files wiped from disk)
`static website presentation/` sources were missing from the working tree
(only dist/ remained). Recovered via `git checkout -- "static website presentation/"`,
then re-applied everything below.

### 9. 18 → true 15 pages (user: "still 18 pages")
Merged: Validation+Status → ch.10 · Scope+Risks → ch.11 · Impact+Funding → ch.13.
Roadmap+Team → ch.12 · Close → ch.14. Chapters 0–9 untouched (CAD choreography
safe). Poses trimmed 18→15, finale framing kept.

### 10. Content upgrades
- Budget 72–131k → 90–150k (mid ~115k), LoRa/mini-PC/SIM now budgeted
- Roadmap 8–12 mo → 5 bootcamp gates with team grid + weekly rhythm
- 6-step Live Link strip (SENSE→FRAME→CROSS→BUFFER→SHORE RX→INSIGHT)

### 11. Layout fixes (user complaints)
a. "Buoy tumabi sa text, lapad space sa right" → camera aim shifted right twice
   (0.7 → −0.2 → −0.9), buoy now sits in right third. Pending user confirm on screen.
b. "Text d mabasa" → fading dark panels behind all 3D-chapter text columns.
c. "Mga box hindi maganda" → labs were UNSTYLED floating text; gave all content
   boxes one plate look + dark tables + pill chips.
d. "Page 05 d mabasa" (twice) → root cause: deliberate `background:none` HUD rule
   + .45rem dim labels over bright 3D village. Fixed with solid plate + all
   micro-labels enlarged ~25% and brightened. USER CONFIRMED OK.

### 12. Validation (final)
- `npm test`: 32 pass / 3 fail — fails are pre-existing (acquisition regex + 2
  camera-framing math, untouched files, noted in PRESENTATION-BUILD.md)
- `npm run build`: passes · `git diff --check`: clean · dist verified
- Deleted: superseded changelog + vite cache. dist/ kept (tests + preview need it).

### 13. Open items for tomorrow
- Confirm page-02 buoy position on a real screen (say "more right" / "balik konti" / "sakto na")
- 3rd mentor name + OJT hours → 1-line swap in `story.js` execution block
- Projector + phone visual QA before defense
- Commit? User has NOT yet approved committing — ASK before git commit/push.

## How to continue tomorrow
Just open this chat again and say "tuloy natin" + what you want (ex: "ayos 02",
"commit na", "dry-run defense Q&A"). This journal + the recap file carry the context.
