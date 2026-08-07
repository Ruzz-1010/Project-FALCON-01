"""Lightweight trend forecasting for presentation-mode telemetry."""

import math
from datetime import datetime
from typing import Any


FORECAST_FIELDS = {
    "waveLevel": {"label": "Wave height", "unit": "m", "bounds": (0.0, 15.0), "decimals": 2},
    "windSpeed": {"label": "Wind speed", "unit": "km/h", "bounds": (0.0, 250.0), "decimals": 1},
    "waterLevel": {"label": "Water level", "unit": "m", "bounds": (0.0, 20.0), "decimals": 2},
    "temperature": {"label": "Water temperature", "unit": "°C", "bounds": (-5.0, 55.0), "decimals": 1},
    "battery": {"label": "Battery reserve", "unit": "%", "bounds": (0.0, 100.0), "decimals": 1},
}


def _timestamp(record: dict[str, Any]) -> float:
    return datetime.fromisoformat(record["recordedAt"]).timestamp()


def _linear_projection(points: list[tuple[float, float]], target_time: float, bounds: tuple[float, float]) -> tuple[float, int]:
    if not points:
        raise ValueError("No valid samples")
    if len(points) < 2:
        return points[-1][1], 35
    origin = points[0][0]
    xs = [timestamp - origin for timestamp, _ in points]
    ys = [value for _, value in points]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = 0.0 if denominator == 0 else sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator
    horizon_seconds = max(0.0, target_time - points[-1][0])
    damping = 1.0 / (1.0 + horizon_seconds / 300.0)
    projected = ys[-1] + slope * horizon_seconds * damping
    projected = min(bounds[1], max(bounds[0], projected))
    residuals = [y - (mean_y + slope * (x - mean_x)) for x, y in zip(xs, ys)]
    volatility = math.sqrt(sum(value * value for value in residuals) / len(residuals))
    scale = max(abs(mean_y), 1.0)
    confidence = round(max(35.0, min(94.0, 94.0 - volatility / scale * 90.0 - horizon_seconds / 90.0)))
    return projected, confidence


def build_forecast(records: list[dict[str, Any]], horizons: tuple[int, ...] = (5, 15, 30)) -> dict[str, Any]:
    ordered = sorted(records, key=_timestamp)
    if not ordered:
        return {"status": "COLLECTING", "sampleCount": 0, "horizons": {}}
    latest_time = _timestamp(ordered[-1])
    result: dict[str, Any] = {}
    for minutes in horizons:
        predictions: dict[str, Any] = {}
        target_time = latest_time + minutes * 60
        for field, metadata in FORECAST_FIELDS.items():
            points = [(_timestamp(item), float(item[field])) for item in ordered if isinstance(item.get(field), (int, float))]
            if not points:
                continue
            value, confidence = _linear_projection(points, target_time, metadata["bounds"])
            predictions[field] = {
                "label": metadata["label"], "value": round(value, metadata["decimals"]),
                "unit": metadata["unit"], "confidence": confidence,
            }
        result[str(minutes)] = predictions
    return {"status": "READY" if len(ordered) >= 10 else "WARMING_UP", "sampleCount": len(ordered), "model": "damped-linear-trend-v1", "horizons": result}


def evaluate_forecast(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Run a rolling one-step backtest over recent stored samples."""
    ordered = sorted(records, key=_timestamp)
    if len(ordered) < 8:
        return {"status": "COLLECTING", "sampleCount": len(ordered), "overallScore": None, "metrics": {}, "comparisons": []}

    evaluations: dict[str, list[dict[str, Any]]] = {field: [] for field in FORECAST_FIELDS}
    first_target = max(6, len(ordered) - 30)
    for target_index in range(first_target, len(ordered)):
        training = ordered[max(0, target_index - 20):target_index]
        target = ordered[target_index]
        target_time = _timestamp(target)
        for field, metadata in FORECAST_FIELDS.items():
            actual = target.get(field)
            points = [(_timestamp(item), float(item[field])) for item in training if isinstance(item.get(field), (int, float))]
            if not isinstance(actual, (int, float)) or len(points) < 2:
                continue
            predicted, confidence = _linear_projection(points, target_time, metadata["bounds"])
            previous = points[-1][1]
            predicted_direction = 0 if predicted == previous else (1 if predicted > previous else -1)
            actual_direction = 0 if actual == previous else (1 if actual > previous else -1)
            evaluations[field].append({
                "recordedAt": target["recordedAt"], "predicted": round(predicted, metadata["decimals"]),
                "actual": round(float(actual), metadata["decimals"]),
                "error": round(abs(predicted - float(actual)), metadata["decimals"] + 1),
                "directionCorrect": predicted_direction == actual_direction, "confidence": confidence,
            })

    metrics: dict[str, Any] = {}
    scores: list[float] = []
    for field, rows in evaluations.items():
        if not rows:
            continue
        metadata = FORECAST_FIELDS[field]
        mae = sum(row["error"] for row in rows) / len(rows)
        direction_accuracy = sum(row["directionCorrect"] for row in rows) / len(rows) * 100
        actual_values = [row["actual"] for row in rows]
        observed_span = max(max(actual_values) - min(actual_values), abs(sum(actual_values) / len(actual_values)) * 0.05, 0.01)
        error_score = max(0.0, 100.0 - mae / observed_span * 100.0)
        score = error_score * 0.55 + direction_accuracy * 0.45
        scores.append(score)
        metrics[field] = {
            "label": metadata["label"], "unit": metadata["unit"], "mae": round(mae, metadata["decimals"] + 1),
            "directionAccuracy": round(direction_accuracy), "score": round(score), "evaluatedSamples": len(rows),
        }

    wave_comparisons = evaluations.get("waveLevel", [])[-20:]
    return {
        "status": "READY" if metrics else "COLLECTING", "sampleCount": len(ordered),
        "overallScore": round(sum(scores) / len(scores)) if scores else None,
        "metrics": metrics, "comparisons": wave_comparisons,
        "method": "rolling one-step backtest",
    }
