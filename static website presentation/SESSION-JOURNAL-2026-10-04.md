# FALCON-01 Session Journal — 2026-10-04


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Full chronological log of this conversation (08 explanation-first + 09 live
edge dashboard). Raw chat has no export button — this file is the save point.
For verbatim text, copy/paste from the chat window.

---

## 1. User request (Taglish, original)

> "sa static website presentation alisin mna yung simulated prediction mas mag
> fucos ka sa explination kase yun yung mahalaga sa 08, then sa 09 yung current
> dahsboard ko ay nasa dashboarrd next dun mo kunin yung referece"

Translation: in the static website presentation, remove the simulated
prediction and focus on the explanation because that is what matters in 08;
for 09, the current dashboard is in dashboard-next — take the reference there.

## 2. Investigation

- Read `static website presentation/` (`index.html`, `present.html`, `main.js`,
  `story.js`, `present.js`, tests, master script, cue card) plus
  `dashboard-next/src/` (`App.tsx`, `SensorsPage`, `MotionPage`, `GpsPage`,
  `ActivityHub`, `LogsPage`, `AlertsPage`, `SettingsPage`, `api.ts`, `types.ts`).
- Found 08 = `#prediction` chapter with `Run prediction` button + `#forecast`
  SVG chart; 09 = `#dashboard` chapter with 4 static mock tabs.

## 3. Change set A — 08 explanation-first, 09 six tabs (done, then superseded)

- 08: deleted `forecast-legend` + `#forecast` SVG + `prediction-bottom`; added a
  second `predict-steps` explainer (BAKIT PERSISTENCE? / CHRONOLOGICAL? /
  MAE-RMSE-BIAS? / STATUS NGAYON?) + honesty line. Same edit in both HTML files.
- 09: 4 tabs → 6 tabs (Overview, Sensors, Buoy Motion, GPS, Logs & Alerts,
  Settings) with dashboard-next-based copy; `main.js` re-rendered per tab.
- Docs: master script 08 (no demo), 09 (six pages), cue card, README.
- Tests: `story.test.mjs` data-tab 4→6; `home.test.mjs` hash recomputed.
- Result: 32 pass / 3 fail (pre-existing), build passed.

## 4. User: "ang layu man sa dashboard ko" (still far from my dashboard)

- Compared static mock vs real dashboard-next: light tilted box vs dark app,
  invented values vs real edge fields. Rebuilt 09 content from the edge
  reference with real field names + simulator snapshot values, restyled monitor
  to dark (removed tilt, cyan `#56d7df` accents).

## 5. User: "ay nasa edge pla" (it's in edge pala)

- Confirmed: `edge/static/dashboard/` = production build of dashboard-next,
  served by `edge/falcon_edge/service.py` at `http://127.0.0.1:8765/`.
- Verified live simulator snapshot via direct runtime run: waveHeight 0.55 m
  SIMULATED, pressure-calibration-v1, raw 115.36 / filtered 115.35 /
  baseline 114.9 kPa, depth 1.5 m, CALIBRATION REQUIRED, quality 88%, wind
  11.1 NE, battery 86.7% CHARGING (12.7 V / 0.34 A), solar 41.5 W CHARGING
  (18.7 V / 2.22 A), GPS 9.7421°N 118.7353°E 3D fix 12 SAT ±1.8 m EXCELLENT,
  anchor 2.4 m drift SECURE 10 m geofence, enclosure 34.0 °C, 11/11 sensors,
  model wave-short-term v1.0.0-demo, horizons 5/10/15.
- No headless browser in this environment (no chromium/playwright/puppeteer),
  so no screenshots could be taken — replication was done from source + live
  API shapes instead.

## 6. User: "subrang layo talaga" (still really far)

- Started rebuilding the 09 shell as an app miniature (sidebar + topbar in
  `index.html`); interrupted before completion — shell replaced by the live
  embed below instead. `present.html` never received the sidebar shell.

## 7. User: "pwede ba gamitin na lng natin nang live yung edge dashboard ko?? the e apply sya sa presentation ko??"

Decision: YES — chapter 09 now embeds the real edge service via iframe.

- Both HTML files: 09 = live block (`#edge-frame` with NO hard-coded src in
  markup, `#edge-status`, `#edge-dot`, `#edge-open`, `#edge-retry`,
  `#edge-fallback` static snapshot with identical edge field names).
- `main.js`: iframe src set from JS (`?edge=` override, default
  `http://127.0.0.1:8765/`); iframe load = ONLINE, 6 s silence = OFFLINE
  fallback. No fetch/XHR so the static-resources test stays green. Deleted the
  mock tab renderer (`overviewMarkup`/`renderDashboard`/data-tab listeners) and
  trimmed the `story.js` import.
- `dashboard.css`: dark monitor + live bar/dot/frame/fallback styles (mobile
  rules preserved).
- `present.js`: PLAIN[9] = live edge wording.
- Docs: master script 09 rewritten as live demo (incl. terminal command +
  Retry fallback), cue card row 9 + pre-flight check, README 09 paragraph.
- Tests: `story.test.mjs` asserts live-embed IDs in both pages and zero
  `data-tab`; `home.test.mjs` hash recomputed to
  `0087dc63…88d48a` with reason comments.
- Result: 32 pass / 3 fail (same 3 pre-existing: acquisition regex + 2
  camera-framing), build passed, `git diff --check` clean.

## 8. User: "so dapt parang need din naka run yung edge para gumana yung sa page 09 kaya ba yun??"

Answer: yes. Run before presenting:

```bash
cd edge && python3 -m falcon_edge.service
# dashboard at http://127.0.0.1:8765/
```

- Same machine: 09 shows the live dashboard automatically.
- Projector on another machine: append `?edge=http://<laptop-ip>:8765`.
- Edge offline: static snapshot + start instructions + Retry — chapter never
  blank. No commit/push was requested, so changes remain uncommitted in the
  working tree.

## 9. User: "okey save this convo"

- This file written as the save point.

---

## 10. Content polish for 6 Oct DOST proposal (same day, continued)

- 09: presenter plumbing removed from stage (`IF THE LIVE VIEW IS OFFLINE`
  details with `python3 -m falcon_edge.service` / `?edge=` URLs deleted);
  replaced with panel-facing `BUILT AND RUNNING ALREADY`; snapshot fallback
  softened (no internal `edge/data/falcon.db` path); footer = "same interface
  the Bay Station operator uses". Both HTML files.
- 02: spec-dump → buoy/shore split + "no mini PC or cellular on the buoy".
- 10: Implemented list leads with live edge service + dashboard.
- 14: internal `PROTOTYPE_REDESIGN_BASELINE.md` ref → plain language.
- `home.test.mjs` hash → `23082b8a…` with dated reason. 32/35 (3 pre-existing),
  build passed.

## 11. User: "paayus ako sa 08 hindi na kase maintindihan yung context"

- 08 `predict-steps` rewritten Taglish-jargon → plain English 4-step flow
  (WHERE DATA COMES FROM → HOW IT PREDICTS → SAFETY LIMITS → HOW IT IS
  JUDGED); second BAKIT evaluation grid deleted. Same honesty labels.
- Master script 08 + `present.js` PLAIN[8] updated to match.
- `home.test.mjs` hash → `1911804a…`. `home.test.mjs` 5/5 green (full suite
  kept timing out across two server restarts — sandbox harness issue, GLB
  model test hangs; unrelated to edits).

## 12. Cover card before the hero (user: title + researchers + school first)

- New first screen inside `#ocean` (NOT a new chapter — 15-count, poses and
  paging untouched): `DOST PROJECT PROPOSAL · 6 OCTOBER 2026`, title, team
  (Correa / Bacaltos / Caballero / Enriquez + roles), BS IT Fullbright +
  Sir Jam / Sir Jeff, `Start the presentation ↓` → eased glide one screen
  down to hero. Both HTML files + `cards-modern.css` + `main.js` handler.
- FALCON acronym added (official, from
  `THESIS DOCUMENTATION/DOST_IDEA_PRESENTATION_PACKAGE.md:78`):
  **F**ullbright College's **A**I-powered **L**ive **C**oastal **O**bservation
  **N**etwork.
- Cover later redesigned to split editorial: title left, gold divider,
  team right, no box (text-shadow readability). Acronym = one inline line.

## 13. Regression fixes from the cover

- Hero invisible after cover: `home-progress` math didn't account for the
  extra screen (`style.css:21` opacity + `.home-departed`). Fix `main.js`:
  `coverH` measured once, subtracted in the progress formula. Simulated
  0→1.0 progress table verified; hero opacity 1.0 at hero top.
- Buoy covered by shades ch00–03: ch02 atmosphere was dark-RIGHT (stale,
  pre-dates buoy move to right third) → flipped to dark-left; ch00/01/02
  spotlight right, ch03 (buoy left, copy right) spotlight left. Hook
  extended `main.js:263` `CH.buoy` → `CH.sensors` (no test impact).
- Buoy further right on ch00: `home.js` aims −0.70/−0.68/−0.66 →
  −2.0/−1.98/−1.65. Third knot capped at −1.65 (brute-force verified max
  keeping exact ch0→ch1 handoff for `home.test.mjs:8`). Cover box slimmed
  760px → 580px (later removed in redesign). `home` 5/5, `home-orbit` 3/3,
  `motion` 3/3 green.

## 14. User: "save this convo" (again)

- This file appended as the save point. Open items: eyeball buoy position
  on projector ("sobra/balik" vs "more right"); 3rd mentor name;
  `npm run build` on presenter's machine; open `present.html?big=1`;
  run `cd edge && python3 -m falcon_edge.service` for live 09.

## 15. UI/UX polish pass via ui-ux-pro-max skill (2026-10-09)

- Skill loaded; ran `ux` domain search (projector readability) +
  `--design-system` for "FALCON-01 academic" (result: Minimalism/Swiss,
  Atkinson/Crimson type pairing — webfont skipped, offline projector risk;
  kept system stack).
- Audit: focus-visible present, buttons 44px, body 1.65 line-height,
  funding tabular-nums present, tables have hover. Gaps fixed, CSS-only in
  `cards-modern.css` (loads last, both pages; zero markup/JS/camera risk):
  `text-wrap:balance/pretty` (no projector orphans), gold summary markers,
  chapter ticks 32px→44px hit area (48px coarse), `p-big` micro/table/h2/
  funding-total/sj-head size bumps for weak projectors.
- Caught own typo live: `var(--gold}` + double `}}` broke `npm run build`
  (lightningcss); fixed, braces balanced, build passes. Removed one
  duplicate cover `@media` line.
- Validation: build passes, `home`+`motion`+`controller` 10/10,
  `git diff --check` clean. 3 pre-existing failures untouched
  (acquisition regex + 2 camera-framing).

## 16. Budget floor raised 90k→110k (2026-10-09, presenter-confirmed)

- Asked "11000-15000?" → clarified to **₱110,000–₱150,000** (literal 11-15k
  would not cover the BOM and would sink panel credibility).
- Category minimums rescaled 18/15/14/15/7/12/9k → 22/19/17/19/8/14/11k;
  ceiling 150k kept; midpoint now ~₱130,000.
- Touched: `story.js` + comments, both HTML funding blocks, `story.test`
  (`₱110–150k`, non-installed `₱25–38k`), test comments, master script
  (6 spots incl. 7 category lines), cue card, content audit, home hash →
  `9fff1934…`.
- Share pack: Slide-Script.md + CLEAN pptx patched (16 spots + heading);
  Mirror pptx + first summary pptx are gone from Documents (keep CLEAN only).
  `/tmp` wiped by a restart mid-task — rebuilt venv, republished `gh-pages`.
- Validation: build passes, home/motion/controller 10/10, bay 2/2,
  diff clean. Site redeployed with new budget.
