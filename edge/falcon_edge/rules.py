"""Sensor validation and deterministic safety rules."""

from dataclasses import dataclass
from typing import Any


SENSOR_RANGES = {
    "battery": (0.0, 100.0),
    "temperature": (-5.0, 55.0),
    "tilt": (0.0, 90.0),
    "waveLevel": (0.0, 15.0),
}


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
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            alerts.append(Alert(f"{name.upper()}_INVALID", "warning", f"{name} reading is missing or invalid"))
        elif not minimum <= float(value) <= maximum:
            alerts.append(Alert(f"{name.upper()}_RANGE", "critical", f"{name} reading is outside its physical range"))
    return alerts


def evaluate_safety_rules(data: dict[str, Any]) -> list[Alert]:
    alerts: list[Alert] = []
    battery = data.get("battery")
    temperature = data.get("temperature")
    tilt = data.get("tilt")
    wave = data.get("waveLevel")

    if isinstance(battery, (int, float)):
        if battery <= 15:
            alerts.append(Alert("BATTERY_CRITICAL", "critical", "Battery reserve is at or below 15%"))
        elif battery <= 30:
            alerts.append(Alert("BATTERY_LOW", "warning", "Battery reserve is at or below 30%"))
    if isinstance(temperature, (int, float)) and temperature >= 40:
        alerts.append(Alert("WATER_TEMP_HIGH", "warning", "Water temperature is at or above 40°C"))
    if isinstance(tilt, (int, float)):
        if tilt >= 35:
            alerts.append(Alert("TILT_CRITICAL", "critical", "Station tilt is at or above 35°"))
        elif tilt >= 20:
            alerts.append(Alert("TILT_HIGH", "warning", "Station tilt is at or above 20°"))
    if isinstance(wave, (int, float)) and wave >= 2.5:
        alerts.append(Alert("WAVE_HIGH", "warning", "Wave activity is at or above 2.5 m"))
    return alerts


def analyze(data: dict[str, Any]) -> list[Alert]:
    unique: dict[str, Alert] = {}
    for alert in validate_telemetry(data) + evaluate_safety_rules(data):
        unique[alert.code] = alert
    return list(unique.values())
