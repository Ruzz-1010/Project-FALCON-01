"""Collector loop and local HTTP API for FALCON edge monitoring."""

import argparse
import json
import signal
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .rules import analyze
from .forecast import build_forecast, build_wave_prediction, evaluate_forecast
from .sources import Esp32Source, SimulatorSource
from .storage import TelemetryStore


class EdgeRuntime:
    def __init__(self, source: Any, store: TelemetryStore, interval: float):
        self.source = source
        self.store = store
        self.interval = max(0.5, interval)
        self.latest: dict[str, Any] = {}
        self.last_error: str | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last_prediction_save = 0.0

    def collect_once(self) -> dict[str, Any]:
        payload = self.source.read()
        alerts = [alert.as_dict() for alert in analyze(payload)]
        recorded_at = datetime.now(timezone.utc).isoformat()
        telemetry_id = self.store.save(recorded_at, self.source.name, payload, alerts)
        snapshot = {"id": telemetry_id, "recordedAt": recorded_at, "source": self.source.name, "data": payload, "alerts": alerts}
        with self._lock:
            self.latest = snapshot
            self.last_error = None
        now = time.monotonic()
        if now - self._last_prediction_save >= 30.0:
            history = self.store.recent(120)
            # The established audit table persists the approved 5/15-minute
            # rows. The v5 presentation can calculate 10 minutes on demand
            # without destructively rebuilding existing field databases.
            for horizon in (5, 15):
                self.store.save_prediction(telemetry_id, build_wave_prediction(history, horizon))
            self._last_prediction_save = now
        return snapshot

    def run(self) -> None:
        while not self._stop.is_set():
            started = time.monotonic()
            try:
                self.collect_once()
            except Exception as error:
                with self._lock:
                    self.last_error = str(error)
            remaining = max(0.0, self.interval - (time.monotonic() - started))
            self._stop.wait(remaining)

    def stop(self) -> None:
        self._stop.set()

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {"service": "ONLINE", "version": "0.1.0", "lastError": self.last_error, "latest": self.latest}

    def v4_status(self) -> dict[str, Any]:
        with self._lock:
            latest = self.latest
            error = self.last_error
        data = latest.get("data", {})
        alerts = latest.get("alerts", [])
        source = latest.get("source", getattr(self.source, "name", "unknown"))
        online = bool(latest) and error is None
        expected = 8
        sensor_fault = data.get("scenario") == "sensor_fault"
        recent = sorted(self.forecast_records(60), key=lambda item: item["recordedAt"])
        sensor_history = [{"recordedAt": item["recordedAt"], "windSpeed": item.get("windSpeed"),
                           "internalTemperature": item.get("internalTemperature", item.get("enclosureTemperature"))}
                          for item in recent]
        return {"system": "ONLINE" if online else "DEGRADED", "monitoring": bool(data.get("monitoring", online)),
                "uptimeSeconds": int(data.get("uptime", 0)), "esp32": "SIMULATED" if source == "simulator" else ("ONLINE" if online else "OFFLINE"),
                "miniPc": "ONLINE", "uart": "SIMULATED" if source == "simulator" else ("CONNECTED" if online else "DISCONNECTED"),
                "api": "ONLINE", "sensorsOnline": expected - (1 if sensor_fault else 0), "sensorsExpected": expected,
                "lastUpdate": latest.get("recordedAt"), "dataSource": source, "activeAlertCount": len(alerts),
                "alerts": alerts, "windSpeed": data.get("windSpeed"), "windDirection": data.get("windDirection"),
                "internalTemperature": data.get("internalTemperature", data.get("enclosureTemperature")),
                "intakeFanRpm": data.get("intakeFanRpm"), "exhaustFanRpm": data.get("exhaustFanRpm"),
                "cpuUsage": data.get("cpuLoad"), "memoryUsage": data.get("memoryUsage"),
                "storageUsage": data.get("storageUsage"), "wifiSignalDbm": -42,
                "sensorHistory": sensor_history, "version": "4.0", "dashboardVersion": "5.0", "lastError": error}

    def wave(self) -> dict[str, Any]:
        with self._lock:
            latest = self.latest
        data = latest.get("data", {})
        value = data.get("waveLevel")
        valid = isinstance(value, (int, float)) and not isinstance(value, bool)
        recent = sorted(self.forecast_records(60), key=lambda item: item["recordedAt"])
        wave_history = [{"recordedAt": item["recordedAt"], "waveHeight": item.get("waveLevel"),
                         "waterPressure": item.get("waterPressure"), "roll": item.get("roll"), "pitch": item.get("pitch")}
                        for item in recent]
        return {"recordedAt": latest.get("recordedAt"), "waveHeight": value if valid else None,
                "waveHeightUnit": "m", "waveHeightState": "SIMULATED" if latest.get("source") == "simulator" else "ESTIMATED",
                "estimationMethod": "presentation-simulator" if latest.get("source") == "simulator" else "pressure-imu-v1",
                "pressure": data.get("waterPressure"), "pressureUnit": "kPa", "pitch": data.get("pitch"),
                "roll": data.get("roll"), "yaw": data.get("yaw"), "angleUnit": "deg",
                "waveMotion": data.get("tilt"), "quality": 0.88 if valid else 0.0,
                "history": wave_history, "valid": valid}

    def gps(self) -> dict[str, Any]:
        with self._lock:
            latest = self.latest
        data = latest.get("data", {})
        valid = isinstance(data.get("latitude"), (int, float)) and isinstance(data.get("longitude"), (int, float))
        return {"recordedAt": latest.get("recordedAt"), "latitude": data.get("latitude"), "longitude": data.get("longitude"),
                "fix": "3D" if valid else "NONE", "satellites": data.get("satellites", 0), "horizontalAccuracyMeters": 1.8 if valid else None,
                "referenceLatitude": 9.7421, "referenceLongitude": 118.7353,
                "deploymentName": "Puerto Princesa City, Palawan Coast",
                "deploymentReferenceState": "DEMO_REFERENCE",
                "anchorDistanceMeters": data.get("anchorDistance"),
                "driftStatus": "SECURE" if valid and float(data.get("anchorDistance", 999)) < 10 else "WARNING",
                "headingDegrees": data.get("yaw"), "surfaceSpeedKnots": data.get("surfaceSpeed"),
                "signalQuality": "EXCELLENT" if valid and data.get("satellites", 0) >= 10 else "LIMITED", "valid": valid}

    def battery(self) -> dict[str, Any]:
        with self._lock:
            latest = self.latest
        data = latest.get("data", {})
        percentage = data.get("battery")
        valid = isinstance(percentage, (int, float))
        status = "CRITICAL" if valid and percentage <= 15 else "LOW" if valid and percentage <= 30 else "NORMAL"
        recent = sorted(self.forecast_records(60), key=lambda item: item["recordedAt"])
        battery_history = [{"recordedAt": item["recordedAt"], "percentage": item.get("battery"),
                            "voltage": item.get("batteryVoltage")} for item in recent]
        return {"recordedAt": latest.get("recordedAt"), "voltage": data.get("batteryVoltage"), "voltageUnit": "V",
                "current": data.get("batteryCurrent"), "currentUnit": "A", "percentage": percentage,
                "direction": "CHARGING" if float(data.get("batteryCurrent", 0)) > 0 else "DISCHARGING", "status": status,
                "temperature": data.get("batteryTemperature"), "temperatureUnit": "deg C",
                "estimatedRuntimeHours": round(float(percentage) / 7.5, 1) if valid else None,
                "powerConsumptionWatts": round(abs(float(data.get("batteryVoltage", 0)) * float(data.get("batteryCurrent", 0))), 1),
                "history": battery_history, "valid": valid}

    def solar(self) -> dict[str, Any]:
        with self._lock:
            latest = self.latest
        data = latest.get("data", {})
        voltage, current = data.get("solarVoltage"), data.get("chargingCurrent")
        valid = isinstance(voltage, (int, float)) and isinstance(current, (int, float))
        charging = valid and current > 0
        return {"recordedAt": latest.get("recordedAt"), "voltage": voltage, "voltageUnit": "V", "current": current,
                "currentUnit": "A", "power": round(voltage * current, 1) if valid else None, "powerUnit": "W",
                "charging": charging, "status": "CHARGING" if charging else "STANDBY", "valid": valid}

    def scenario_status(self) -> dict[str, Any]:
        if not isinstance(self.source, SimulatorSource):
            return {"available": False, "active": None, "scenarios": []}
        return {"available": True, "active": self.source.scenario, "scenarios": list(self.source.scenarios)}

    def set_scenario(self, scenario: str) -> dict[str, Any]:
        if not isinstance(self.source, SimulatorSource):
            raise RuntimeError("Scenarios are only available with the simulator source")
        self.source.set_scenario(scenario)
        self.collect_once()
        result = self.scenario_status()
        result["appliedAt"] = datetime.now(timezone.utc).isoformat()
        # Simulator scenarios transition continuously, so the existing valid
        # history remains usable immediately after the control is applied.
        result["aiState"] = "READY"
        return result

    def forecast_records(self, limit: int = 120) -> list[dict[str, Any]]:
        records = self.store.recent(limit)
        if not isinstance(self.source, SimulatorSource):
            return records
        segment: list[dict[str, Any]] = []
        newer_wave: float | None = None
        for record in records:
            wave = record.get("waveLevel")
            if isinstance(wave, (int, float)) and newer_wave is not None and abs(float(wave) - newer_wave) > 0.85:
                # Keep protection against legacy abrupt scenario changes and
                # corrupted spikes. Current scenarios blend smoothly, so a
                # scenario label boundary alone must not discard AI history.
                break
            segment.append(record)
            if isinstance(wave, (int, float)):
                newer_wave = float(wave)
        # A stale duplicate service used to be able to write a second sample
        # between the configured two-second samples. Keep one coherent
        # simulator stream so charts and forecasts cannot alternate between
        # two independent phases while legacy rows age out of the database.
        coherent: list[dict[str, Any]] = []
        newest_kept: datetime | None = None
        minimum_gap = self.interval * 0.75
        for record in segment:
            recorded_at = datetime.fromisoformat(record["recordedAt"])
            if newest_kept is None or (newest_kept - recorded_at).total_seconds() >= minimum_gap:
                coherent.append(record)
                newest_kept = recorded_at
        return coherent


def make_handler(runtime: EdgeRuntime, store: TelemetryStore):
    dashboard_directory = Path(__file__).parents[2] / "data"
    static_assets = {
        "/": ("index.html", "text/html; charset=utf-8"),
        "/index.html": ("index.html", "text/html; charset=utf-8"),
        "/style.css": ("style.css", "text/css; charset=utf-8"),
        "/app.js": ("app.js", "application/javascript; charset=utf-8"),
        "/model-viewer.js": ("model-viewer.js", "application/javascript; charset=utf-8"),
        "/falcon-logo.jpg": ("falcon-logo.jpg", "image/jpeg"),
        "/ocean-dashboard-bg.png": ("ocean-dashboard-bg.png", "image/png"),
        "/favicon.ico": ("falcon-logo.jpg", "image/jpeg"),
        "/vendor/three.module.min.js": ("vendor/three.module.min.js", "application/javascript; charset=utf-8"),
        "/vendor/three.core.min.js": ("vendor/three.core.min.js", "application/javascript; charset=utf-8"),
        "/vendor/GLTFLoader.js": ("vendor/GLTFLoader.js", "application/javascript; charset=utf-8"),
        "/vendor/leaflet.css": ("vendor/leaflet.css", "text/css; charset=utf-8"),
        "/vendor/leaflet.js": ("vendor/leaflet.js", "application/javascript; charset=utf-8"),
        "/vendor/lucide.min.js": ("vendor/lucide.min.js", "application/javascript; charset=utf-8"),
        "/utils/BufferGeometryUtils.js": ("utils/BufferGeometryUtils.js", "application/javascript; charset=utf-8"),
        "/models/FALCON-01.glb": ("models/FALCON-01.glb", "model/gltf-binary"),
    }

    class ApiHandler(BaseHTTPRequestHandler):
        def _write_body(self, body: bytes) -> None:
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                # Browsers routinely cancel stale asset/API requests during reloads.
                return

        def _send(self, status: int, payload: Any) -> None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.end_headers()
            self._write_body(body)

        def _send_asset(self, file_name: str, content_type: str) -> None:
            path = dashboard_directory / file_name
            try:
                body = path.read_bytes()
            except OSError:
                self._send(503, {"error": "DASHBOARD_ASSET_UNAVAILABLE"})
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self._write_body(body)

        def do_OPTIONS(self) -> None:
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.end_headers()

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in static_assets:
                self._send_asset(*static_assets[parsed.path])
            elif parsed.path == "/health":
                self._send(200, runtime.status())
            elif parsed.path == "/status":
                self._send(200, runtime.v4_status())
            elif parsed.path == "/wave":
                wave = runtime.wave()
                self._send(200 if wave["valid"] else 503, wave)
            elif parsed.path == "/gps":
                gps = runtime.gps()
                self._send(200 if gps["valid"] else 503, gps)
            elif parsed.path == "/battery":
                battery = runtime.battery()
                self._send(200 if battery["valid"] else 503, battery)
            elif parsed.path == "/solar":
                solar = runtime.solar()
                self._send(200 if solar["valid"] else 503, solar)
            elif parsed.path in ("/ai", "/prediction"):
                try:
                    horizon = int(parse_qs(parsed.query).get("horizon", ["15"])[0])
                    prediction = build_wave_prediction(runtime.forecast_records(), horizon)
                    prediction["scenario"] = runtime.source.scenario if isinstance(runtime.source, SimulatorSource) else None
                    self._send(200, prediction)
                except ValueError as error:
                    self._send(400, {"error": {"code": "INVALID_HORIZON", "message": str(error)}})
            elif parsed.path == "/logs":
                raw_limit = parse_qs(parsed.query).get("limit", ["60"])[0]
                try:
                    limit = max(1, min(200, int(raw_limit)))
                    self._send(200, {"telemetry": store.recent(limit), "predictions": store.recent_predictions(limit),
                                     "alerts": store.recent_alerts(limit), "events": store.recent_events(limit)})
                except ValueError:
                    self._send(400, {"error": {"code": "INVALID_LIMIT", "message": "limit must be an integer"}})
            elif parsed.path == "/api/latest":
                latest = runtime.status()["latest"]
                self._send(200 if latest else 503, latest or {"error": "NO_TELEMETRY"})
            elif parsed.path == "/api/history":
                raw_limit = parse_qs(parsed.query).get("limit", ["50"])[0]
                try:
                    self._send(200, {"items": store.recent(int(raw_limit))})
                except ValueError:
                    self._send(400, {"error": "INVALID_LIMIT"})
            elif parsed.path == "/api/alerts":
                raw_limit = parse_qs(parsed.query).get("limit", ["50"])[0]
                try:
                    self._send(200, {"items": store.recent_alerts(int(raw_limit))})
                except ValueError:
                    self._send(400, {"error": "INVALID_LIMIT"})
            elif parsed.path == "/api/scenario":
                self._send(200, runtime.scenario_status())
            elif parsed.path == "/api/forecast":
                self._send(200, build_forecast(runtime.forecast_records()))
            elif parsed.path == "/api/forecast/validation":
                self._send(200, evaluate_forecast(runtime.forecast_records()))
            else:
                self._send(404, {"error": "NOT_FOUND"})

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            if path not in ("/api/scenario", "/restart", "/calibrate"):
                self._send(404, {"error": "NOT_FOUND"})
                return
            try:
                length = min(int(self.headers.get("Content-Length", "0")), 4096)
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                if path == "/api/scenario":
                    self._send(200, runtime.set_scenario(str(payload.get("scenario", ""))))
                elif path == "/restart":
                    target = str(payload.get("target", "esp32"))
                    if target not in ("esp32", "service", "mini-pc"):
                        raise ValueError("Unsupported restart target")
                    store.log_event(datetime.now(timezone.utc).isoformat(), "RESTART_REQUEST", target, "ACCEPTED", payload)
                    self._send(202, {"accepted": True, "target": target, "status": "RESTARTING"})
                else:
                    sensor = str(payload.get("sensor", ""))
                    operation = str(payload.get("operation", "start"))
                    if sensor not in ("bno085", "water-pressure", "wind", "gps") or operation != "start":
                        raise ValueError("Unsupported sensor or calibration operation")
                    calibration_id = f"cal-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
                    store.log_event(datetime.now(timezone.utc).isoformat(), "CALIBRATION", sensor, "IN_PROGRESS", payload)
                    self._send(202, {"accepted": True, "sensor": sensor, "operation": operation,
                                     "status": "IN_PROGRESS", "calibrationId": calibration_id})
            except (ValueError, json.JSONDecodeError) as error:
                self._send(400, {"error": "INVALID_SCENARIO", "message": str(error)})
            except RuntimeError as error:
                self._send(409, {"error": "SCENARIO_UNAVAILABLE", "message": str(error)})

        def log_message(self, format: str, *args: Any) -> None:
            return

    return ApiHandler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FALCON edge telemetry service")
    parser.add_argument("--source", choices=("simulator", "esp32"), default="simulator")
    parser.add_argument("--esp32-url", default="http://192.168.4.1")
    parser.add_argument("--database", default=str(Path(__file__).parents[1] / "data" / "falcon.db"))
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = SimulatorSource() if args.source == "simulator" else Esp32Source(args.esp32_url)
    store = TelemetryStore(args.database)
    runtime = EdgeRuntime(source, store, args.interval)
    # Bind before starting collection. If another FALCON service owns the
    # port, startup now fails without leaving a hidden duplicate collector
    # writing conflicting simulator samples into the shared database.
    server = ThreadingHTTPServer((args.host, args.port), make_handler(runtime, store))
    collector = threading.Thread(target=runtime.run, name="falcon-collector", daemon=True)
    collector.start()

    def shutdown(*_: Any) -> None:
        runtime.stop()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)
    print(f"FALCON edge service listening on http://{args.host}:{args.port}")
    print(f"Telemetry source: {source.name} | Database: {Path(args.database).resolve()}")
    try:
        server.serve_forever()
    finally:
        runtime.stop()
        server.server_close()
        collector.join(timeout=3)


if __name__ == "__main__":
    main()
