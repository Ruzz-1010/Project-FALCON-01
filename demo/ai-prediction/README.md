# FALCON-01 — AI wave forecast demo

Interactive demo for the `wave-short-term` estimator used by the edge service
(`edge/falcon_edge/forecast.py`).

**Pages**

- `index.html` — the demo. Simulates a buoy that reports every **2 minutes**, forecasts the wave
  height **15 minutes ahead**, and then checks whether the forecast was right when the time came.
- `calc.html` — the full calculation, step by step, with the numbers from the live simulated feed.
- `model.js` — the JavaScript port of the estimator.

**What the demo shows (the short version)**

1. Buoy reading now (wave height in metres, one reading every 2 min).
2. Forecast for the next 15 minutes (sea condition: calm / moderate / rough, plus confidence).
3. Chart: measured readings, the forecast the model made earlier, and the actual reading that
   arrived — the gap between forecast and actual is the error.

**Demo caveats**

- The feed is simulated; no real buoy is connected.
- The model is a transparent research baseline (damped linear trend), **not** a trained or field-validated AI.
- The error table is measured against the same simulated feed — it shows the mechanism, not real sea accuracy.
- The deployed edge service samples every 2 s with a 120-reading window; this demo uses the field
  reporting cadence (2 min / reading, 30-reading window) so the numbers stay readable.

Live page: https://ruzz-1010.github.io/Project-FALCON-01/ai-demo/
Full calculation: https://ruzz-1010.github.io/Project-FALCON-01/ai-demo/calc.html
