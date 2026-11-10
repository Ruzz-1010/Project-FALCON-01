# FALCON-01 — short-term wave prediction demo

Interactive browser demo for the `wave-short-term` estimator used by the edge
service (`edge/falcon_edge/forecast.py`).

It is a **demo of the mechanism**, not a field result:

- the sensor feed is simulated (same wave curve as the edge simulator);
- you can inject a manual reading, or run calm / rough / squall / drop scenarios;
- the prediction, sea-condition class, confidence and prediction-vs-actual error
  table are all computed live from that simulated feed;
- the error numbers therefore show that the pipeline works end to end — they are
  **not** measured accuracy at sea.

The JavaScript is a faithful port of `_project()`, `_forecast_series()` and
`classify_sea_condition()`: damped linear trend over the last 120 samples
(4 min at 2 s), change limit `max(0.08, 0.35 × last) × (h/15)^0.7`, confidence
from residual volatility, and the CALM / MODERATE / ROUGH thresholds at
0.6 m and 2.5 m.

Live page: <https://ruzz-1010.github.io/Project-FALCON-01/ai-demo/>

The model is a transparent research baseline. It has no trained weights and is
not field-validated; it must not be presented as a trained AI model or used for
navigation or safety decisions.
