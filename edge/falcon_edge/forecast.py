"""Focused short-horizon wave forecasting for Project FALCON v4.0."""

import math
import time
from datetime import datetime, timedelta
from typing import Any


SUPPORTED_HORIZONS = (15,)
MODEL_NAME = "wave-short-term"
MODEL_VERSION = "1.1.0-demo"
SUMMARY_WINDOW_SECONDS = 120


def _timestamp(record: dict[str, Any]) -> float:
    return datetime.fromisoformat(record["recordedAt"]).timestamp()


def _wave(record: dict[str, Any]) -> float | None:
    value = record.get("waveLevel")
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def summarize_wave_records(records: list[dict[str, Any]],
                           window_seconds: int = SUMMARY_WINDOW_SECONDS) -> list[tuple[float, float]]:
    """Return completed two-minute wave-height summaries for forecasting.

    The edge service stores raw simulator or sensor telemetry more frequently
    than the reporting interval.  Forecasting must not treat every raw frame as
    a separate two-minute observation.  Inputs that are already spaced at least
    one minute apart are treated as completed summary packets; faster streams
    are averaged into complete, epoch-aligned two-minute windows.
    """
    ordered = sorted(((_timestamp(item), value) for item in records
                      if (value := _wave(item)) is not None), key=lambda item: item[0])
    if len(ordered) < 2:
        return ordered

    intervals = [ordered[index][0] - ordered[index - 1][0] for index in range(1, len(ordered))
                 if ordered[index][0] > ordered[index - 1][0]]
    median_interval = sorted(intervals)[len(intervals) // 2] if intervals else float(window_seconds)
    if median_interval >= window_seconds / 2:
        return ordered

    buckets: dict[int, list[tuple[float, float]]] = {}
    for timestamp, value in ordered:
        bucket = math.floor(timestamp / window_seconds)
        buckets.setdefault(bucket, []).append((timestamp, value))

    expected_samples = max(2, round(window_seconds / max(median_interval, 0.001)))
    minimum_samples = max(2, math.floor(expected_samples * 0.75))
    summaries: list[tuple[float, float]] = []
    for bucket in sorted(buckets):
        samples = buckets[bucket]
        if len(samples) < minimum_samples:
            continue
        bucket_end = (bucket + 1) * window_seconds
        summaries.append((bucket_end, sum(value for _, value in samples) / len(samples)))
    return summaries


def classify_sea_condition(wave_height: float) -> str:
    if wave_height < 0.6:
        return "CALM"
    if wave_height < 2.5:
        return "MODERATE"
    return "ROUGH"


def _project(points: list[tuple[float, float]], horizon_minutes: float) -> tuple[float, int, dict[str, Any]]:
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


def _forecast_series(points: list[tuple[float, float]], horizon_minutes: int, endpoint: float,
                     confidence: int, generated: datetime) -> list[dict[str, Any]]:
    """Project each displayed lead time with the same transparent baseline."""
    current = round(points[-1][1], 2)
    _, _, endpoint_details = _project(points, horizon_minutes)
    volatility = endpoint_details["residualVolatility"]
    steps = max(10, horizon_minutes * 2)
    series: list[dict[str, Any]] = []
    for index in range(steps + 1):
        progress = index / steps
        lead_minutes = progress * horizon_minutes
        predicted = current if index == 0 else _project(points, lead_minutes)[0]
        uncertainty = max(0.025, volatility * (0.7 + progress) + (100 - confidence) / 1000.0)
        if index == steps:
            predicted = endpoint
        series.append({
            "minutesAhead": round(progress * horizon_minutes, 2),
            "at": (generated + timedelta(minutes=progress * horizon_minutes)).isoformat(),
            "predictedWaveHeight": round(predicted, 3),
            "lowerBound": round(max(0.0, predicted - uncertainty), 3),
            "upperBound": round(predicted + uncertainty, 3),
        })
    return series


def _historical_prediction_series(points: list[tuple[float, float]]) -> list[dict[str, Any]]:
    """Rolling one-step estimates covering the dashboard's 60-sample window.

    Each estimate uses only earlier samples. The initial eight samples remain
    a warm-up period, not fabricated prediction history.
    """
    rows: list[dict[str, Any]] = []
    start = max(8, len(points) - 60)
    for index in range(start, len(points)):
        training = points[max(0, index - 20):index]
        origin = training[0][0]
        xs = [timestamp - origin for timestamp, _ in training]
        ys = [value for _, value in training]
        mean_x, mean_y = sum(xs) / len(xs), sum(ys) / len(ys)
        denominator = sum((x - mean_x) ** 2 for x in xs)
        slope = 0.0 if denominator == 0 else sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator
        elapsed = max(0.0, points[index][0] - training[-1][0])
        raw = training[-1][1] + slope * elapsed
        maximum_step = max(0.03, training[-1][1] * 0.08)
        predicted = min(training[-1][1] + maximum_step, max(training[-1][1] - maximum_step, raw))
        rows.append({"at": datetime.fromtimestamp(points[index][0]).astimezone().isoformat(),
                     "predictedWaveHeight": round(max(0.0, predicted), 3)})
    return rows


def build_wave_prediction(records: list[dict[str, Any]], horizon_minutes: int = 15) -> dict[str, Any]:
    inference_started = time.perf_counter()
    if horizon_minutes not in SUPPORTED_HORIZONS:
        raise ValueError("Unsupported horizon; Project FALCON uses a fixed 15-minute research horizon")
    ordered = sorted(records, key=_timestamp)
    points = summarize_wave_records(ordered)
    generated = datetime.fromtimestamp(points[-1][0] if points else datetime.now().timestamp()).astimezone()
    source = str(ordered[-1].get("source", "sensor")) if ordered else "sensor"
    base = {
        "generatedAt": generated.isoformat(), "targetAt": None, "horizonMinutes": horizon_minutes,
        "currentWaveHeight": points[-1][1] if points else None, "predictedWaveHeight": None,
        "unit": "m", "change": None, "direction": None, "confidence": None,
        "confidenceMeaning": "heuristic stability score; not validated forecast accuracy", "seaCondition": None,
        "model": MODEL_NAME, "modelVersion": MODEL_VERSION, "sampleCount": len(points),
        "rawSampleCount": sum(1 for item in ordered if _wave(item) is not None),
        "summaryWindowSeconds": SUMMARY_WINDOW_SECONDS,
        "lastTrainingDate": None, "inferenceTimeMs": None,
        "status": "UNAVAILABLE", "dataSource": source, "unavailableReason": "INSUFFICIENT_HISTORY",
        "forecastSeries": [],
        "historicalPredictionSeries": [],
    }
    if len(points) < 8:
        base["inferenceTimeMs"] = round((time.perf_counter() - inference_started) * 1000, 3)
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
        "forecastSeries": _forecast_series(points[-120:], horizon_minutes, predicted, confidence, generated),
        "historicalPredictionSeries": _historical_prediction_series(points),
        "explanation": {
            "method": "damped linear trend over recent wave-height history",
            "input": "completed two-minute pressure-derived wave-height summaries",
            "steps": ["validate wave samples", "fit recent linear trend", "project to selected horizon",
                      "dampen long-horizon movement", "apply short-horizon change limit", "classify sea condition"],
            "details": details,
            "seaConditionThresholds": {"calmBelowMeters": 0.6, "moderateBelowMeters": 2.5, "roughAtOrAboveMeters": 2.5},
        },
    })
    base["inferenceTimeMs"] = round((time.perf_counter() - inference_started) * 1000, 3)
    return base


def build_forecast(records: list[dict[str, Any]], horizons: tuple[int, ...] = SUPPORTED_HORIZONS) -> dict[str, Any]:
    """Compatibility envelope used by the presentation route."""
    predictions = {str(horizon): build_wave_prediction(records, horizon) for horizon in horizons}
    sample_count = max((item["sampleCount"] for item in predictions.values()), default=0)
    return {"status": "READY" if sample_count >= 8 else "COLLECTING", "sampleCount": sample_count,
            "model": MODEL_NAME, "horizons": predictions}


def evaluate_forecast(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Chronological 15-minute backtest against later two-minute summaries."""
    points = summarize_wave_records(records)
    rows: list[dict[str, Any]] = []
    for origin_index in range(7, len(points)):
        training = points[max(0, origin_index - 29):origin_index + 1]
        target_time = training[-1][0] + 15 * 60
        actual_row = next(((timestamp, value) for timestamp, value in points[origin_index + 1:]
                           if timestamp >= target_time), None)
        if actual_row is None:
            break
        actual_time, actual = actual_row
        predicted, stability, _ = _project(training, 15)
        persistence = training[-1][1]
        error = predicted - actual
        rows.append({
            "generatedAt": datetime.fromtimestamp(training[-1][0]).astimezone().isoformat(),
            "targetAt": datetime.fromtimestamp(target_time).astimezone().isoformat(),
            "actualAt": datetime.fromtimestamp(actual_time).astimezone().isoformat(),
            "predicted": round(predicted, 3), "persistence": round(persistence, 3),
            "actual": round(actual, 3), "error": round(error, 3),
            "absoluteError": round(abs(error), 3), "stabilityScore": stability,
        })
    if not rows:
        return {"status": "COLLECTING", "sampleCount": len(points), "overallScore": None,
                "metrics": {}, "comparisons": {}}
    mae = sum(row["absoluteError"] for row in rows) / len(rows)
    rmse = math.sqrt(sum(row["error"] ** 2 for row in rows) / len(rows))
    bias = sum(row["error"] for row in rows) / len(rows)
    persistence_mae = sum(abs(row["persistence"] - row["actual"]) for row in rows) / len(rows)
    skill = None if persistence_mae == 0 else 1.0 - mae / persistence_mae
    score = round(max(0.0, 100.0 - mae / 0.5 * 100.0))
    metric = {"label": "15-minute wave-height estimate", "unit": "m", "mae": round(mae, 3),
              "rmse": round(rmse, 3), "bias": round(bias, 3),
              "persistenceMae": round(persistence_mae, 3),
              "skillVersusPersistence": None if skill is None else round(skill, 3),
              "score": score, "evaluatedSamples": len(rows)}
    return {"status": "READY", "sampleCount": len(points), "overallScore": score,
            "metrics": {"waveLevel": metric}, "comparisons": {"waveLevel": rows},
            "method": "chronological 15-minute rolling-origin backtest on two-minute summaries"}
