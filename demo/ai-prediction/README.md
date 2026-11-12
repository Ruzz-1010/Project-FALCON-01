# FALCON-01 — AI wave forecast dashboard

Interactive demo for the `wave-short-term` estimator used by the edge service
(`edge/falcon_edge/forecast.py`).

**Pages**

- `index.html` — the demo dashboard. You type the **lowest and highest water level** of a
  2-minute buoy window and send the pair. The reading is the paper's pressure-derived estimate
  **H = max(η) − min(η)**. After 8 sent readings the model forecasts H **15 minutes ahead**;
  later readings show whether the forecast was right.
- `calc.html` — the full calculation, step by step, using exactly the pairs sent on the demo page.
  It does not simulate or auto-run.
- `model.js` — the JavaScript port of the estimator.
- `app.js` — dashboard drawing, score table, and manual-input wiring.
- `calc.js` — read-only calculation page logic.

**Important behaviour**

- **Nothing moves until you send a pair.** There is no timer, playback, or auto-generated feed.
- Each 2-minute record is only a minimum and a maximum. The wave height used by the model is
  `H = max − min`, following the pressure-to-wave procedure in the research proposal.
- The forecast unlocks after 8 readings (the model needs a short history).
- The score table compares each forecast with the first reading at or after its 15-minute target.

**Demo caveats**

- The inputs are simulated; no real buoy is connected.
- The model is a transparent research baseline (damped linear trend), **not** a trained or field-validated AI.
- The error table is measured against the same simulated inputs — it shows the mechanism, not real sea accuracy.
- The deployed edge service samples every 2 s with a 120-reading window; this demo uses the field
  reporting cadence (2 min / reading, 30-reading window) so the numbers stay readable.

Live page: https://ruzz-1010.github.io/Project-FALCON-01/ai-demo/
Full calculation: https://ruzz-1010.github.io/Project-FALCON-01/ai-demo/calc.html
