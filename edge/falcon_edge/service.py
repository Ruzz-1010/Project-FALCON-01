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
from .forecast import build_forecast, evaluate_forecast
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

    def collect_once(self) -> dict[str, Any]:
        payload = self.source.read()
        alerts = [alert.as_dict() for alert in analyze(payload)]
        recorded_at = datetime.now(timezone.utc).isoformat()
        telemetry_id = self.store.save(recorded_at, self.source.name, payload, alerts)
        snapshot = {"id": telemetry_id, "recordedAt": recorded_at, "source": self.source.name, "data": payload, "alerts": alerts}
        with self._lock:
            self.latest = snapshot
            self.last_error = None
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

    def scenario_status(self) -> dict[str, Any]:
        if not isinstance(self.source, SimulatorSource):
            return {"available": False, "active": None, "scenarios": []}
        return {"available": True, "active": self.source.scenario, "scenarios": list(self.source.scenarios)}

    def set_scenario(self, scenario: str) -> dict[str, Any]:
        if not isinstance(self.source, SimulatorSource):
            raise RuntimeError("Scenarios are only available with the simulator source")
        self.source.set_scenario(scenario)
        return self.scenario_status()


def make_handler(runtime: EdgeRuntime, store: TelemetryStore):
    dashboard_directory = Path(__file__).parents[2] / "data"
    static_assets = {
        "/": ("index.html", "text/html; charset=utf-8"),
        "/index.html": ("index.html", "text/html; charset=utf-8"),
        "/style.css": ("style.css", "text/css; charset=utf-8"),
        "/app.js": ("app.js", "application/javascript; charset=utf-8"),
        "/falcon-logo.jpg": ("falcon-logo.jpg", "image/jpeg"),
    }

    class ApiHandler(BaseHTTPRequestHandler):
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
            self.wfile.write(body)

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
            self.wfile.write(body)

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
                self._send(200, build_forecast(store.recent(120)))
            elif parsed.path == "/api/forecast/validation":
                self._send(200, evaluate_forecast(store.recent(120)))
            else:
                self._send(404, {"error": "NOT_FOUND"})

        def do_POST(self) -> None:
            if urlparse(self.path).path != "/api/scenario":
                self._send(404, {"error": "NOT_FOUND"})
                return
            try:
                length = min(int(self.headers.get("Content-Length", "0")), 4096)
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                self._send(200, runtime.set_scenario(str(payload.get("scenario", ""))))
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
    collector = threading.Thread(target=runtime.run, name="falcon-collector", daemon=True)
    collector.start()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(runtime, store))

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
