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
        self._last_read_at = self._started_at
        self._rough_mix = 0.0
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
        now = time.monotonic()
        elapsed = now - self._started_at
        delta = max(0.0, min(5.0, now - self._last_read_at))
        self._last_read_at = now
        slow = math.sin(elapsed / 42.0)
        swell = math.sin(elapsed / 7.8)
        chop = math.sin(elapsed / 2.6 + 1.1)
        fast = math.sin(elapsed / 5.0)
        scenario = self.scenario
        target_rough_mix = 1.0 if scenario == "rough_sea" else 0.0
        transition_rate = 1.0 - math.exp(-delta / 11.0)
        self._rough_mix += (target_rough_mix - self._rough_mix) * transition_rate
        base_wave = 0.48 + slow * 0.07 + abs(swell) * 0.12 + chop * 0.018 + self._random.uniform(-0.012, 0.012)
        base_wind = 10.8 + slow * 1.7 + swell * 0.55 + self._random.uniform(-0.18, 0.18)
        base_roll = swell * (1.15 + base_wave * 0.8) + chop * 0.35
        base_pitch = math.sin(elapsed / 8.6 + .8) * (0.75 + base_wave * 0.55) + chop * 0.18
        rough_wave = 3.0 + abs(swell) * 0.72 + chop * 0.12
        rough_wind = 31.0 + abs(slow) * 7.0 + swell * 1.2
        rough_roll = swell * 11.5 + chop * 2.1
        rough_pitch = math.sin(elapsed / 8.6 + .8) * 7.5 + chop * 1.2
        wave = base_wave + (rough_wave - base_wave) * self._rough_mix
        wind_speed = base_wind + (rough_wind - base_wind) * self._rough_mix
        roll = base_roll + (rough_roll - base_roll) * self._rough_mix
        pitch = base_pitch + (rough_pitch - base_pitch) * self._rough_mix
        payload = {
            "system": "ONLINE",
            "clients": 1,
            "uptime": round(elapsed),
            "monitoring": True,
            "battery": round(max(0.0, 87.0 - elapsed / 7200.0), 1),
            "temperature": round(28.4 + slow * 0.3, 2),
            "tilt": round(math.sqrt(roll * roll + pitch * pitch), 2),
            "waveLevel": round(wave, 2),
            "seaCondition": "CALM" if wave < 0.6 else "MODERATE" if wave < 2.5 else "ROUGH",
            "gps": "3D FIX · 12 SAT",
            "solar": "CHARGING",
            "security": "ARMED",
            "windSpeed": round(wind_speed, 1),
            "windDirection": "NE",
            "waterPressure": round(114.9 + wave * 0.72 + swell * 0.16 + self._random.uniform(-0.025, 0.025), 2),
            # Puerto Princesa coastal demo reference with a smooth mooring swing.
            # Replace this reference with the surveyed coordinate for field use.
            "latitude": round(9.7421 + math.sin(elapsed / 29.0) * 0.000022, 6),
            "longitude": round(118.7353 + math.cos(elapsed / 33.0) * 0.000024, 6),
            "satellites": 12,
            "anchorDistance": round(3.4 + fast * 0.25, 1),
            "surfaceSpeed": round(0.12 + abs(fast) * 0.03, 2),
            "roll": round(roll, 2),
            "pitch": round(pitch, 2),
            "yaw": round(41.6 + slow * 1.4 + chop * .22, 1),
            "batteryVoltage": round(12.7 - elapsed / 100000.0, 2),
            "batteryCurrent": -0.82,
            "solarVoltage": round(18.4 + slow * 0.5, 1),
            "chargingCurrent": round(2.16 + slow * 0.18, 2),
            "internalTemperature": round(34.2 + slow * 0.7, 1),
            "batteryTemperature": round(31.4 + slow * 0.35, 1),
            "intakeFanRpm": round(1280 + slow * 90 + abs(chop) * 45),
            "exhaustFanRpm": round(1420 + slow * 110 + abs(chop) * 55),
            "storageUsage": 29,
            "memoryUsage": round(42 + fast * 2),
            "cpuLoad": round(18 + abs(fast) * 7),
        }
        if scenario == "low_battery":
            payload.update({"battery": 22.0, "solar": "STANDBY"})
        elif scenario == "overheating":
            payload.update({"internalTemperature": round(58 + slow * 2, 1),
                            "intakeFanRpm": round(2860 + abs(chop) * 120),
                            "exhaustFanRpm": round(3120 + abs(chop) * 140)})
        elif scenario == "sensor_fault":
            payload["waveLevel"] = None
            payload["seaCondition"] = "UNKNOWN"
        payload["scenario"] = scenario
        payload["scenarioTransition"] = round(self._rough_mix, 3)
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
