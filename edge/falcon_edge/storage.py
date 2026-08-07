"""SQLite persistence for telemetry and alerts."""

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


class TelemetryStore:
    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recorded_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telemetry_id INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    FOREIGN KEY (telemetry_id) REFERENCES telemetry(id)
                );
                CREATE INDEX IF NOT EXISTS idx_telemetry_recorded_at ON telemetry(recorded_at DESC);
                """
                )

    def save(self, recorded_at: str, source: str, payload: dict[str, Any], alerts: list[dict[str, str]]) -> int:
        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    "INSERT INTO telemetry(recorded_at, source, payload) VALUES (?, ?, ?)",
                    (recorded_at, source, json.dumps(payload, separators=(",", ":"))),
                )
                telemetry_id = int(cursor.lastrowid)
                connection.executemany(
                    "INSERT INTO alerts(telemetry_id, code, severity, message) VALUES (?, ?, ?, ?)",
                    [(telemetry_id, item["code"], item["severity"], item["message"]) for item in alerts],
                )
                return telemetry_id

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = max(1, min(500, int(limit)))
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT id, recorded_at, source, payload FROM telemetry ORDER BY id DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        return [
            {"id": row["id"], "recordedAt": row["recorded_at"], "source": row["source"], **json.loads(row["payload"])}
            for row in rows
        ]

    def recent_alerts(self, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = max(1, min(200, int(limit)))
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """SELECT alerts.id, alerts.telemetry_id, telemetry.recorded_at,
                          alerts.code, alerts.severity, alerts.message
                   FROM alerts JOIN telemetry ON telemetry.id = alerts.telemetry_id
                   ORDER BY alerts.id DESC LIMIT ?""",
                (safe_limit,),
            ).fetchall()
        return [
            {"id": row["id"], "telemetryId": row["telemetry_id"], "recordedAt": row["recorded_at"],
             "code": row["code"], "severity": row["severity"], "message": row["message"]}
            for row in rows
        ]
