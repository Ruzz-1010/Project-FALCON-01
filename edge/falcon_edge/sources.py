"""Telemetry sources for development and ESP32 deployment."""

import json
import math
import random
import time
import threading
from typing import Any
from urllib.request import Request, urlopen


class SimulatorSource:
    name = "simulator"
    scenarios = ("normal", "rough_sea", "low_battery", "overheating", "sensor_fault")

    def __init__(self, seed: int = 101):
        self._random = random.Random(seed)
        self._started_at = time.monotonic()
        self._scenario = "normal"
        self._lock = threading.Lock()

    @property
    def scenario(self) -> str:
        with self._lock:
            return self._scenario

    def set_scenario(self, scenario: str) -> None:
        if scenario not in self.scenarios:
            raise ValueError("Unknown simulator scenario")
        with self._lock:
            self._scenario = scenario

    def read(self) -> dict[str, Any]:
        elapsed = time.monotonic() - self._started_at
        slow = math.sin(elapsed / 18.0)
        fast = math.sin(elapsed / 5.0)
        wave = 0.38 + abs(fast) * 0.14 + self._random.uniform(-0.025, 0.025)
        payload = {
            "system": "ONLINE",
            "clients": 1,
            "uptime": round(elapsed),
            "monitoring": True,
            "battery": round(max(0.0, 87.0 - elapsed / 7200.0), 1),
            "temperature": round(28.4 + slow * 0.3, 2),
            "tilt": round(1.7 + fast * 0.55, 2),
            "waveLevel": round(wave, 2),
            "seaCondition": "CALM" if wave < 0.6 else "MODERATE",
            "gps": "3D FIX · 12 SAT",
            "solar": "CHARGING",
            "security": "ARMED",
            "windSpeed": round(8.6 + slow * 1.2 + self._random.uniform(-0.2, 0.2), 1),
            "windDirection": "NE",
            "waterLevel": round(1.42 + math.sin(elapsed / 55.0) * 0.04, 2),
            "salinity": round(33.8 + math.sin(elapsed / 40.0) * 0.15, 1),
            "airTemperature": round(30.1 + slow * 0.4, 1),
            "humidity": round(78 + slow * 2, 1),
            "pressure": round(1009 + math.sin(elapsed / 70.0) * 1.4, 1),
            "latitude": 16.6687,
            "longitude": 120.3240,
            "satellites": 12,
            "anchorDistance": round(3.4 + fast * 0.25, 1),
            "surfaceSpeed": round(0.12 + abs(fast) * 0.03, 2),
            "roll": round(1.8 + fast * 0.4, 1),
            "pitch": round(0.9 + slow * 0.3, 1),
            "yaw": round(41.6 + fast * 1.2, 1),
            "batteryVoltage": round(12.7 - elapsed / 100000.0, 2),
            "batteryCurrent": -0.82,
            "solarVoltage": round(18.4 + slow * 0.5, 1),
            "chargingCurrent": round(2.16 + slow * 0.18, 2),
            "enclosureTemperature": round(34.2 + slow * 0.7, 1),
            "batteryTemperature": round(31.7 + slow * 0.4, 1),
            "intakeFanRpm": round(1240 + fast * 60),
            "exhaustFanRpm": round(1180 + fast * 55),
            "storageUsage": 29,
            "memoryUsage": round(42 + fast * 2),
            "cpuLoad": round(18 + abs(fast) * 7),
        }
        scenario = self.scenario
        if scenario == "rough_sea":
            payload.update({"tilt": round(24 + fast * 5, 2), "waveLevel": round(3.1 + abs(fast), 2), "windSpeed": round(32 + abs(fast) * 8, 1), "seaCondition": "ROUGH"})
        elif scenario == "low_battery":
            payload.update({"battery": 22.0, "solar": "STANDBY"})
        elif scenario == "overheating":
            payload.update({"temperature": round(42.2 + slow, 2), "enclosureTemperature": round(58 + slow * 2, 1), "batteryTemperature": round(46 + slow, 1), "intakeFanRpm": 2200, "exhaustFanRpm": 2100})
        elif scenario == "sensor_fault":
            payload["waveLevel"] = None
            payload["seaCondition"] = "UNKNOWN"
        payload["scenario"] = scenario
        return payload


class Esp32Source:
    name = "esp32"

    def __init__(self, base_url: str, timeout_seconds: float = 2.0):
        self.url = f"{base_url.rstrip('/')}/api/status"
        self.timeout_seconds = timeout_seconds

    def read(self) -> dict[str, Any]:
        request = Request(self.url, headers={"Accept": "application/json", "User-Agent": "falcon-edge/0.1"})
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
