"""Focused short-horizon wave forecasting for Project FALCON v4.0."""

import math
from datetime import datetime, timedelta
from typing import Any


SUPPORTED_HORIZONS = (5, 10, 15)
MODEL_NAME = "wave-short-term"
MODEL_VERSION = "1.0.0-demo"


def _timestamp(record: dict[str, Any]) -> float:
    return datetime.fromisoformat(record["recordedAt"]).timestamp()


def _wave(record: dict[str, Any]) -> float | None:
    value = record.get("waveLevel")
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def classify_sea_condition(wave_height: float) -> str:
    if wave_height < 0.6:
        return "CALM"
    if wave_height < 2.5:
        return "MODERATE"
    return "ROUGH"


def _project(points: list[tuple[float, float]], horizon_minutes: int) -> tuple[float, int, dict[str, Any]]:
    origin = points[0][0]
    xs = [timestamp - origin for timestamp, _ in points]
    ys = [value for _, value in points]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = 0.0 if denominator == 0 else sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator
    horizon_seconds = horizon_minutes * 60
    damping = 1.0 / (1.0 + horizon_seconds / 300.0)
    raw_projection = ys[-1] + slope * horizon_seconds * damping
    # A short presentation window must not turn a few seconds of noise into an
    # implausible collapse or spike. Field limits will be learned from trials.
    maximum_change = max(0.08, ys[-1] * 0.35) * (horizon_minutes / 15.0) ** 0.7
    projected = min(ys[-1] + maximum_change, max(ys[-1] - maximum_change, raw_projection))
    projected = max(0.0, min(15.0, projected))
    residuals = [y - (mean_y + slope * (x - mean_x)) for x, y in zip(xs, ys)]
    volatility = math.sqrt(sum(value * value for value in residuals) / len(residuals))
    confidence = round(max(35.0, min(94.0, 94.0 - volatility / max(mean_y, 0.1) * 60.0 - horizon_minutes * 0.8)))
    details = {
        "validSamples": len(points),
        "sampleWindowSeconds": round(points[-1][0] - points[0][0], 1),
        "trendMetersPerMinute": round(slope * 60.0, 4),
        "rawProjection": round(raw_projection, 3),
        "maximumAllowedChange": round(maximum_change, 3),
        "limitApplied": abs(projected - raw_projection) > 0.0005,
        "residualVolatility": round(volatility, 4),
        "dampingFactor": round(damping, 3),
    }
    return projected, confidence, details


def build_wave_prediction(records: list[dict[str, Any]], horizon_minutes: int = 15) -> dict[str, Any]:
    if horizon_minutes not in SUPPORTED_HORIZONS:
        raise ValueError("Unsupported horizon; use 5, 10, or 15 minutes")
    ordered = sorted(records, key=_timestamp)
    points = [(_timestamp(item), value) for item in ordered if (value := _wave(item)) is not None]
    generated = datetime.fromtimestamp(points[-1][0] if points else datetime.now().timestamp()).astimezone()
    source = str(ordered[-1].get("source", "sensor")) if ordered else "sensor"
    base = {
        "generatedAt": generated.isoformat(), "targetAt": None, "horizonMinutes": horizon_minutes,
        "currentWaveHeight": points[-1][1] if points else None, "predictedWaveHeight": None,
        "unit": "m", "change": None, "direction": None, "confidence": None,
        "confidenceMeaning": "model quality indicator", "seaCondition": None,
        "model": MODEL_NAME, "modelVersion": MODEL_VERSION, "sampleCount": len(points),
        "status": "UNAVAILABLE", "dataSource": source, "unavailableReason": "INSUFFICIENT_HISTORY",
    }
    if len(points) < 8:
        return base
    predicted, confidence, details = _project(points[-120:], horizon_minutes)
    current = points[-1][1]
    predicted = round(predicted, 2)
    change = round(predicted - current, 2)
    base.update({
        "targetAt": (generated + timedelta(minutes=horizon_minutes)).isoformat(),
        "currentWaveHeight": round(current, 2), "predictedWaveHeight": predicted,
        "change": change, "direction": "up" if change > 0 else "down" if change < 0 else "stable",
        "confidence": confidence, "seaCondition": classify_sea_condition(predicted),
        "status": "READY", "unavailableReason": None,
        "explanation": {
            "method": "damped linear trend over recent wave-height history",
            "input": "wave-height estimates derived from pressure and IMU telemetry",
            "steps": ["validate wave samples", "fit recent linear trend", "project to selected horizon",
                      "dampen long-horizon movement", "apply short-horizon change limit", "classify sea condition"],
            "details": details,
            "seaConditionThresholds": {"calmBelowMeters": 0.6, "moderateBelowMeters": 2.5, "roughAtOrAboveMeters": 2.5},
        },
    })
    return base


def build_forecast(records: list[dict[str, Any]], horizons: tuple[int, ...] = SUPPORTED_HORIZONS) -> dict[str, Any]:
    """Compatibility envelope used by the presentation route."""
    predictions = {str(horizon): build_wave_prediction(records, horizon) for horizon in horizons}
    sample_count = max((item["sampleCount"] for item in predictions.values()), default=0)
    return {"status": "READY" if sample_count >= 8 else "COLLECTING", "sampleCount": sample_count,
            "model": MODEL_NAME, "horizons": predictions}


def evaluate_forecast(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Small wave-only one-step backtest retained for transparent demo validation."""
    ordered = sorted(records, key=_timestamp)
    rows: list[dict[str, Any]] = []
    for index in range(max(8, len(ordered) - 30), len(ordered)):
        actual = _wave(ordered[index])
        training = ordered[max(0, index - 20):index]
        points = [(_timestamp(item), value) for item in training if (value := _wave(item)) is not None]
        if actual is None or len(points) < 2:
            continue
        elapsed_minutes = max(0.01, (_timestamp(ordered[index]) - points[-1][0]) / 60)
        predicted, confidence, _ = _project(points, min(15, max(5, round(elapsed_minutes))))
        rows.append({"recordedAt": ordered[index]["recordedAt"], "predicted": round(predicted, 2),
                     "actual": round(actual, 2), "error": round(abs(predicted - actual), 3), "confidence": confidence})
    if not rows:
        return {"status": "COLLECTING", "sampleCount": len(ordered), "overallScore": None,
                "metrics": {}, "comparisons": {}}
    mae = sum(row["error"] for row in rows) / len(rows)
    score = round(max(0.0, 100.0 - mae / 0.5 * 100.0))
    metric = {"label": "Wave height", "unit": "m", "mae": round(mae, 3), "score": score,
              "evaluatedSamples": len(rows)}
    return {"status": "READY", "sampleCount": len(ordered), "overallScore": score,
            "metrics": {"waveLevel": metric}, "comparisons": {"waveLevel": rows},
            "method": "wave-only rolling backtest"}
