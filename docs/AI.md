# Optional AI and FALCON Assistant v6.1

AI is not required for the Phase 1 monitoring baseline. The core system must acquire, validate, log, display, and alert without a trained model.

The current `/ai` output is a clearly labeled optional research/presentation model using estimated wave history. It is not field-trained, not an official forecast, and must remain hidden by default. Any later AI evaluation requires calibrated live data, traceable train/test separation, baseline comparison, error metrics, model/version records, and failure isolation.

The FALCON Assistant is separate from AI. It is a deterministic rule-based visual status aid with `NORMAL`, `WARNING`, `ALERT`, and `OFFLINE` states. It is not a chatbot, LLM, voice interface, or autonomous controller. Its messages summarize configured station rules and never issue official safety instructions.
