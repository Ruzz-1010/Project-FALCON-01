# FALCON AI Wave Prediction and Assistant v6.2


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

AI wave prediction is a required visible Project FALCON feature. The core monitoring path still acquires, validates, logs, displays, and alerts independently so a prediction error cannot erase live coastal readings.

The `/ai` endpoint produces a 5-, 10-, or 15-minute wave-height estimate from recent pressure-based estimated-wave history. Overview always displays the current estimate, predicted value, expected `CALM`/`MODERATE`/`ROUGH` condition, confidence indicator, sample count, model state, and live or simulated input label. With fewer than eight valid records it displays `COLLECTING` instead of inventing a prediction.

The present `wave-short-term` implementation is a transparent damped-trend research baseline. It is implemented software, but it is not yet a trained or field-validated AI model and is not an official marine forecast. The next model stage requires calibrated live data, traceable train/validation/test separation, comparison against the current baseline, MAE/RMSE/bias reporting, uncertainty checks, and versioned evaluation records. Only then may the thesis report measured AI prediction accuracy.

The FALCON Assistant is separate from AI. It is a deterministic rule-based visual status aid with `NORMAL`, `WARNING`, `ALERT`, and `OFFLINE` states. It is not a chatbot, LLM, voice interface, or autonomous controller. Its messages summarize configured station rules and never issue official safety instructions.
