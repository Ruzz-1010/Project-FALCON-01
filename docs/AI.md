# Project FALCON AI Specification v4.0

## Authority and Scope

Authority: PROJECT_CONTEXT.md v4.0.

Status: presentation prototype implemented; physical-data model planned.

The Phase 1 AI has exactly two responsibilities:

1. predict wave height 5–15 minutes ahead; and
2. classify sea condition as Calm, Moderate, or Rough.

No other AI feature is approved for Phase 1.

## Explicit Exclusions

The AI shall not predict:

- weather;
- typhoons;
- storms;
- ocean currents;
- fish activity;
- maintenance;
- water quality;
- or navigation actions.

The system shall not use self-learning production behavior, cloud AI, multiple operational models, camera AI, or computer vision in Phase 1.

## Current Implementation Status

The repository currently includes a damped linear trend presentation forecast and rolling backtest over simulated/local telemetry.

This implementation demonstrates data flow and UI behavior.

It is not the final field-validated model.

Current multi-sensor prediction cards and 30-minute horizon are legacy presentation features requiring simplification to the v4 scope.

## Approved Inputs

Primary inputs:

- recent calibrated wave-height estimates;
- water-pressure features;
- BNO085 motion features;
- pitch;
- roll;
- and data-quality indicators.

Optional validated context:

- wind speed;
- and wind direction.

Operational measurements such as GPS, battery, solar, and internal temperature are not prediction targets.

## Input Quality Gate

Inference shall require:

- valid current wave estimate;
- sufficient recent history;
- acceptable timestamp continuity;
- acceptable pressure-sensor state;
- acceptable IMU state;
- and a supported horizon.

Failed requirements shall produce an unavailable result with a reason.

## Prediction Horizons

Approved horizons:

- 5 minutes;
- and 15 minutes.

Intermediate horizons may be used only when documented and approved.

Thirty-minute prediction is not a Phase 1 research output.

## Candidate Model Process

1. establish a persistence baseline;
2. establish a simple trend/statistical baseline;
3. collect physical time-ordered data;
4. define synchronized input windows;
5. engineer documented wave/motion features;
6. compare candidate lightweight methods;
7. select one operational model;
8. freeze a versioned artifact;
9. validate by horizon;
10. deploy to the Orange Pi Zero 3;
11. monitor inference quality;
12. and retain prediction history.

## Model Selection Principles

- explainable enough for research review;
- lightweight enough for the Orange Pi Zero 3;
- deterministic preprocessing;
- robust missing-data behavior;
- measurable improvement over baseline;
- and reproducible training/evaluation.

## Time-Series Data Rules

- preserve chronological order;
- separate training and test periods in time;
- avoid future leakage;
- record calibration versions;
- record deployment conditions;
- preserve raw evidence;
- and identify simulator data separately.

## Output Schema

Every successful prediction shall expose:

- generatedAt;
- targetAt;
- horizonMinutes;
- currentWaveHeight;
- predictedWaveHeight;
- unit;
- change;
- direction;
- confidence;
- seaCondition;
- model;
- modelVersion;
- sampleCount;
- and status.

Unavailable output shall expose:

- status;
- unavailableReason;
- missing or invalid inputs;
- and last valid prediction timestamp when appropriate.

## Confidence

Confidence must have a documented calculation.

It shall not be described as probability unless calibrated as probability.

Possible contributors include:

- input completeness;
- recent validation error;
- model residuals;
- horizon length;
- and current signal quality.

The dashboard shall show confidence beside the predicted value.

## Sea-Condition Classification

Approved classes:

- Calm;
- Moderate;
- Rough.

Thresholds shall be based on approved references or validation data.

Thresholds shall be configuration-controlled.

Hysteresis should prevent rapid class switching.

Unavailable is an error state, not a fourth sea-condition class.

## Validation Metrics

Required regression metrics:

- mean absolute error;
- root mean squared error when appropriate;
- bias;
- valid-prediction coverage;
- and inference time.

Optional supporting metric:

- direction accuracy.

Required classification metrics:

- class accuracy;
- per-class precision/recall when sample count supports it;
- confusion matrix;
- and boundary/hysteresis behavior.

Results shall be reported separately for 5 and 15 minutes.

Dashboard v5 may calculate and display a 10-minute presentation point within the approved 5–15 minute range. Formal field evaluation and durable audit baselines remain separated at 5 and 15 minutes.

## Backtesting

Backtesting shall:

- use only data available before each target time;
- compare prediction with later actual measurement;
- record error and model version;
- retain sample count;
- and distinguish physical from simulated data.

## Deployment

The model runs on the Orange Pi Zero 3.

The ESP32 provides validated telemetry to the Orange Pi Zero 3 primarily through UART; validated local Wi-Fi may be used as an alternate transport.

The AI service publishes through `GET /ai`.

The dashboard consumes the API result.

The AI shall not directly control buoy hardware.

## Model Versioning

Every deployed artifact shall record:

- model name;
- semantic or controlled version;
- training dataset identifier;
- feature schema version;
- calibration requirements;
- training code revision;
- evaluation report;
- and deployment date.

## Safety and Communication

The prediction is advisory research output.

It is not an official weather or maritime warning.

It shall not replace government advisories.

Current and predicted wave values must be displayed separately.

Simulated predictions must be labeled.

Presentation-model performance must not be reported as field accuracy.

## Dashboard Explainability

For every ready presentation prediction, the dashboard exposes:

- number and duration of valid recent wave samples;
- detected wave-height trend in meters per minute;
- raw mathematical projection;
- damping factor;
- maximum allowed short-horizon change and whether it was applied;
- residual signal volatility used by the confidence indicator;
- selected prediction horizon;
- and exact Calm, Moderate, and Rough thresholds.

The implemented presentation model fits a damped linear trend to recent wave-height history. That history is the intended output of pressure-and-IMU wave estimation. It is not represented as a trained field model. Physical trials must provide synchronized pressure and IMU data before the final model is trained and validated.

## Acceptance Criteria

- one operational model selected;
- persistence baseline documented;
- physical time-ordered test data used;
- 5-minute metrics reported;
- 15-minute metrics reported;
- invalid-input behavior passes;
- confidence definition approved;
- three-class thresholds approved;
- output schema passes API tests;
- and research limitations documented.

## Future Expansion

Weather, current, storm, maintenance, water-quality, vision, cloud, and multi-model AI remain Future Expansion and require separate research approval.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 4.0 | 2026-08-09 | Created focused wave-prediction and three-class sea-condition AI specification. |
