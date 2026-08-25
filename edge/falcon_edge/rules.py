"""Validation and deterministic alerts for approved Phase 1 sensors."""

from dataclasses import dataclass
from typing import Any


SENSOR_RANGES = {
    "battery": (0.0, 100.0), "temperature": (-5.0, 55.0),
    "waveLevel": (0.0, 15.0), "waterPressure": (80.0, 500.0),
    "windSpeed": (0.0, 250.0), "internalTemperature": (-10.0, 85.0),
    "waterTemperature": (-5.0, 45.0), "salinity": (0.0, 50.0),
}
OPTIONAL_SENSOR_FIELDS = {"waterTemperature", "salinity"}


@dataclass(frozen=True)
class Alert:
    code: str
    severity: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "severity": self.severity, "message": self.message}


def validate_telemetry(data: dict[str, Any]) -> list[Alert]:
    alerts: list[Alert] = []
    for name, (minimum, maximum) in SENSOR_RANGES.items():
        value = data.get(name)
        if value is None and name in OPTIONAL_SENSOR_FIELDS:
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            alerts.append(Alert(f"{name.upper()}_INVALID", "warning", f"{name} reading is missing or invalid"))
        elif not minimum <= float(value) <= maximum:
            alerts.append(Alert(f"{name.upper()}_RANGE", "critical", f"{name} reading is outside its physical range"))
    return alerts


def evaluate_safety_rules(data: dict[str, Any]) -> list[Alert]:
    alerts: list[Alert] = []
    battery, internal = data.get("battery"), data.get("internalTemperature")
    wave = data.get("waveLevel")
    anchor_distance = data.get("anchorDistance")
    if isinstance(battery, (int, float)):
        if battery <= 15: alerts.append(Alert("BATTERY_CRITICAL", "critical", "Battery reserve is at or below 15%"))
        elif battery <= 30: alerts.append(Alert("BATTERY_LOW", "warning", "Battery reserve is at or below 30%"))
    if isinstance(internal, (int, float)):
        if internal >= 60: alerts.append(Alert("INTERNAL_TEMP_CRITICAL", "critical", "Internal temperature is at or above 60 degrees C"))
        elif internal >= 50: alerts.append(Alert("INTERNAL_TEMP_HIGH", "warning", "Internal temperature is at or above 50 degrees C"))
    if isinstance(wave, (int, float)) and wave >= 2.5:
        alerts.append(Alert("WAVE_HIGH", "warning", "Wave height is at or above 2.5 m"))
    if data.get("geofenceViolation") or ("geofenceViolation" not in data and isinstance(anchor_distance, (int, float)) and anchor_distance >= 10):
        alerts.append(Alert("GEOFENCE_ALERT", "critical", "Buoy position remained outside the configured 10 m geofence"))
    if data.get("vibrationDetected") or data.get("enclosureOpen"):
        alerts.append(Alert("TAMPER_ALERT", "critical", "Persistent vibration or enclosure access was detected"))
    return alerts


def analyze(data: dict[str, Any]) -> list[Alert]:
    unique = {alert.code: alert for alert in validate_telemetry(data) + evaluate_safety_rules(data)}
    return list(unique.values())
