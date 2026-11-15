# FALCON-01 — wave forecast dashboard

Interactive demo for the `wave-short-term` estimator used by the edge service
(`edge/falcon_edge/forecast.py`).

**Pages**

- `index.html` — the demo dashboard. It explains the idea in three steps, then you type the
  **lowest and highest water level** of a 2-minute buoy window and add the pair. The reading is
  **H_est = max(η) − min(η) = highest − lowest**, the paper's pressure-derived estimate. After
  8 readings the model forecasts H **15 minutes ahead**; later readings show whether it was right.
- `calc.html` — the full calculation, step by step, using exactly the pairs you add on the demo page.
  It shows the paper's pressure → height formula first, then the damped-trend forecast. It does not
  simulate or auto-run.
- `model.js` — the JavaScript port of the estimator.
- `app.js` — dashboard drawing, score table, and manual-input wiring.
- `calc.js` — read-only calculation page logic.

**Important behaviour**

- **Nothing moves until you add a pair.** There is no timer, playback, or auto-generated feed.
- Each 2-minute record is only a lowest and highest water level. The wave height used by the
  model is `H_est = highest − lowest`, following the paper's pressure-derived procedure
  (`ΔPᵢ = Pᵢ − P_base`, `ηᵢ = ΔPᵢ / (ρg)`, `H_est = max(ηᵢ) − min(ηᵢ)`).
- The forecast unlocks after 8 readings (the model needs a short history).
- The score table compares each forecast with the first reading at or after its 15-minute target.

**Demo caveats**

- The inputs are entered manually; no real buoy is connected.
- The forecast is the paper's transparent **damped linear-trend baseline**, the comparison method —
  **not** the trained or field-validated AI model.
- `H_est` is a pressure-derived estimate; the paper explicitly does not call it significant wave height.
- The error table is measured against the same manual inputs — it shows the mechanism, not real sea accuracy.
- The deployed edge service samples every 2 s with a 120-reading window; this demo uses the field
  reporting cadence (2 min / reading, 30-reading window) so the numbers stay readable.

Live page: https://ruzz-1010.github.io/Project-FALCON-01/ai-demo/
Full calculation: https://ruzz-1010.github.io/Project-FALCON-01/ai-demo/calc.html
