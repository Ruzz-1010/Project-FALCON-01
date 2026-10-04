# FALCON-01 Session Journal — 2026-10-04

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
