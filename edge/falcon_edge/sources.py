"""Telemetry sources for development and ESP32 deployment."""

import json
import math
import random
import time
import threading
from typing import Any
from urllib.request import Request, urlopen


def parse_telemetry_line(line: str) -> dict[str, Any]:
    """Validate one newline-delimited FALCON telemetry frame."""
    frame = json.loads(line)
    if frame.get("protocol") != "falcon.telemetry" or frame.get("version") != 1:
        raise ValueError("Unsupported FALCON telemetry frame")
    if not isinstance(frame.get("sequence"), int) or not isinstance(frame.get("measurements"), dict):
        raise ValueError("Malformed FALCON telemetry frame")
    payload = dict(frame["measurements"])
    payload.update({"sequence": frame["sequence"], "uptime": int(frame.get("uptimeMs", 0)) // 1000,
                    "monitoring": bool(frame.get("monitoring", True)), "sensorStatus": frame.get("sensors", {}),
                    "telemetryVersion": frame["version"], "dataSource": frame.get("source", "esp32")})
    return payload


class SerialJsonSource:
    """Read versioned newline-JSON telemetry from ESP32 USB/UART."""

    name = "esp32-serial"

    def __init__(self, port: str, baud: int = 115200, timeout_seconds: float = 3.0):
        try:
            import serial  # type: ignore
        except ImportError as error:
            raise RuntimeError("Serial source requires: python -m pip install pyserial") from error
        self._serial = serial.Serial(port, baudrate=baud, timeout=timeout_seconds)

    def read(self) -> dict[str, Any]:
        while True:
            raw = self._serial.readline()
            if not raw:
                raise TimeoutError("No ESP32 telemetry frame received")
            line = raw.decode("utf-8", errors="replace").strip()
            if line.startswith("{"):
                return parse_telemetry_line(line)


class SimulatorSource:
    name = "simulator"
    scenarios = ("normal", "rough_sea", "low_battery", "overheating", "sensor_fault", "tamper_alert", "geofence_alert")

    def __init__(self, seed: int = 101):
        self._random = random.Random(seed)
        self._started_at = time.monotonic()
        self._last_read_at = self._started_at
        self._rough_mix = 0.0
        self._low_battery_mix = 0.0
        self._overheat_mix = 0.0
        self._battery_level = 86.7
        self._internal_temperature = 33.8
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
        self._low_battery_mix += ((1.0 if scenario == "low_battery" else 0.0) - self._low_battery_mix) * transition_rate
        self._overheat_mix += ((1.0 if scenario == "overheating" else 0.0) - self._overheat_mix) * transition_rate
        base_wave = 0.48 + slow * 0.07 + abs(swell) * 0.12 + chop * 0.018 + self._random.uniform(-0.012, 0.012)
        base_wind = 10.8 + slow * 1.7 + swell * 0.55 + self._random.uniform(-0.18, 0.18)
        rough_wave = 3.0 + abs(swell) * 0.72 + chop * 0.12
        rough_wind = 31.0 + abs(slow) * 7.0 + swell * 1.2
        wave = base_wave + (rough_wave - base_wave) * self._rough_mix
        wind_speed = base_wind + (rough_wind - base_wind) * self._rough_mix
        solar_irradiance = 0.92 + slow * 0.045 + math.sin(elapsed / 95.0 + .4) * .025
        solar_voltage = 18.35 + solar_irradiance * .42
        solar_current = 2.02 + solar_irradiance * .22
        normal_battery = 86.7 + math.sin(elapsed / 360.0) * .18
        battery_target = 22.0 if scenario == "low_battery" else normal_battery
        battery_rate = 1.5 if battery_target < self._battery_level else .18
        battery_step = max(-battery_rate * delta, min(battery_rate * delta, battery_target - self._battery_level))
        self._battery_level += battery_step
        battery = self._battery_level
        normal_internal = 33.8 + slow * .55 + abs(fast) * .18
        internal_target = 58.5 + slow * 1.2 if scenario == "overheating" else normal_internal
        thermal_rate = .72 if internal_target > self._internal_temperature else .28
        thermal_step = max(-thermal_rate * delta, min(thermal_rate * delta, internal_target - self._internal_temperature))
        self._internal_temperature += thermal_step
        internal_temperature = self._internal_temperature
        fan_demand = max(0.0, min(1.0, (internal_temperature - 32.0) / 25.0))
        intake_rpm = 1120 + fan_demand * 1710 + abs(chop) * 38
        exhaust_rpm = 1240 + fan_demand * 1880 + abs(chop) * 44
        gps_angle = elapsed / 31.0
        geofence_offset = 15.0 if scenario == "geofence_alert" else 0.0
        north_m = math.sin(gps_angle) * 2.55 + geofence_offset
        east_m = math.cos(gps_angle * .91) * 2.35
        latitude = 9.7421 + north_m / 111_320.0
        longitude = 118.7353 + east_m / (111_320.0 * math.cos(math.radians(9.7421)))
        anchor_distance = math.hypot(north_m, east_m)
        heading_degrees = (42.0 + slow * 2.1 + math.sin(elapsed / 58.0) * .8) % 360
        compass = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
        wind_heading = (48.0 + slow * 8.0 + math.sin(elapsed / 73.0) * 4.0) % 360
        payload = {
            "system": "ONLINE",
            "clients": 1,
            "uptime": round(elapsed),
            "monitoring": True,
            "battery": round(max(0.0, battery), 1),
            "temperature": round(28.4 + slow * 0.3, 2),
            "waveLevel": round(wave, 2),
            "seaCondition": "CALM" if wave < 0.6 else "MODERATE" if wave < 2.5 else "ROUGH",
            "gps": "3D FIX · 12 SAT",
            "solar": "STANDBY" if self._low_battery_mix > .55 else "CHARGING",
            "security": "ALERT" if scenario in ("tamper_alert", "geofence_alert") else "SECURE",
            "windSpeed": round(wind_speed, 1),
            "windDirection": compass[round(wind_heading / 45.0) % 8],
            "waterPressure": round(114.9 + wave * 0.72 + swell * 0.16 + self._random.uniform(-0.025, 0.025), 2),
            "filteredPressure": round(114.9 + wave * 0.72 + swell * 0.12, 2),
            "pressureBaseline": 114.90,
            "pressureCalibration": "CALIBRATION REQUIRED",
            "waterDepth": round(1.48 + swell * .04, 2),
            "waterTemperature": round(28.1 + slow * .28, 2),
            "salinity": round(32.4 + slow * .35, 1),
            "salinityState": "ESTIMATED · CALIBRATION REQUIRED",
            "vibrationDetected": scenario == "tamper_alert",
            "enclosureOpen": scenario == "tamper_alert",
            "buzzerActive": scenario in ("tamper_alert", "geofence_alert"),
            # Puerto Princesa coastal demo reference with a smooth mooring swing.
            # Replace this reference with the surveyed coordinate for field use.
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "satellites": round(11.5 + math.sin(elapsed / 67.0) * .7),
            "anchorDistance": round(anchor_distance, 1),
            "surfaceSpeed": round(0.08 + self._rough_mix * .22 + abs(math.sin(gps_angle)) * .03, 2),
            "heading": round(heading_degrees, 1),
            "batteryVoltage": round(11.85 + battery / 100.0 * .98, 2),
            "batteryCurrent": round(.34 - self._low_battery_mix * .78 + slow * .04, 2),
            "solarVoltage": round(solar_voltage, 1),
            "chargingCurrent": round(solar_current * (1.0 - self._low_battery_mix * .92), 2),
            "internalTemperature": round(internal_temperature, 1),
            "batteryTemperature": round(30.8 + (internal_temperature - 33.8) * .16 + slow * .25, 1),
            "intakeFanRpm": round(intake_rpm),
            "exhaustFanRpm": round(exhaust_rpm),
            "storageUsage": 29,
            "memoryUsage": round(42 + fast * 2),
            "cpuLoad": round(18 + abs(fast) * 7),
        }
        if scenario == "sensor_fault":
            payload["waveLevel"] = None
            payload["seaCondition"] = "UNKNOWN"
        payload["scenario"] = scenario
        payload["scenarioTransition"] = round(max(self._rough_mix, self._low_battery_mix, self._overheat_mix), 3)
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
