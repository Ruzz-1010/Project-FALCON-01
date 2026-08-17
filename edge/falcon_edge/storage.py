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
                CREATE TABLE IF NOT EXISTS wave_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telemetry_id INTEGER NOT NULL,
                    generated_at TEXT NOT NULL,
                    target_at TEXT,
                    horizon_minutes INTEGER NOT NULL CHECK(horizon_minutes IN (5, 10, 15)),
                    current_wave_height REAL,
                    predicted_wave_height REAL,
                    confidence INTEGER,
                    sea_condition TEXT CHECK(sea_condition IN ('CALM', 'MODERATE', 'ROUGH') OR sea_condition IS NULL),
                    model TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    FOREIGN KEY (telemetry_id) REFERENCES telemetry(id)
                );
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recorded_at TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    target TEXT,
                    status TEXT NOT NULL,
                    detail TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_telemetry_recorded_at ON telemetry(recorded_at DESC);
                CREATE INDEX IF NOT EXISTS idx_alerts_telemetry_id ON alerts(telemetry_id);
                CREATE INDEX IF NOT EXISTS idx_predictions_generated_at ON wave_predictions(generated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_events_recorded_at ON system_events(recorded_at DESC);
                """
                )
                self._migrate_prediction_horizons(connection)

    @staticmethod
    def _migrate_prediction_horizons(connection: sqlite3.Connection) -> None:
        """Expand legacy 5/15-minute prediction tables without losing records."""
        row = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'wave_predictions'"
        ).fetchone()
        table_sql = (row["sql"] or "") if row else ""
        normalized_sql = "".join(table_sql.lower().split())
        if "horizon_minutesin(5,10,15)" in normalized_sql:
            return

        connection.executescript(
            """
            DROP INDEX IF EXISTS idx_predictions_generated_at;
            ALTER TABLE wave_predictions RENAME TO wave_predictions_legacy;
            CREATE TABLE wave_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telemetry_id INTEGER NOT NULL,
                generated_at TEXT NOT NULL,
                target_at TEXT,
                horizon_minutes INTEGER NOT NULL CHECK(horizon_minutes IN (5, 10, 15)),
                current_wave_height REAL,
                predicted_wave_height REAL,
                confidence INTEGER,
                sea_condition TEXT CHECK(sea_condition IN ('CALM', 'MODERATE', 'ROUGH') OR sea_condition IS NULL),
                model TEXT NOT NULL,
                model_version TEXT NOT NULL,
                status TEXT NOT NULL,
                source TEXT NOT NULL,
                FOREIGN KEY (telemetry_id) REFERENCES telemetry(id)
            );
            INSERT INTO wave_predictions (
                id, telemetry_id, generated_at, target_at, horizon_minutes,
                current_wave_height, predicted_wave_height, confidence,
                sea_condition, model, model_version, status, source
            )
            SELECT id, telemetry_id, generated_at, target_at, horizon_minutes,
                   current_wave_height, predicted_wave_height, confidence,
                   sea_condition, model, model_version, status, source
            FROM wave_predictions_legacy;
            DROP TABLE wave_predictions_legacy;
            CREATE INDEX idx_predictions_generated_at ON wave_predictions(generated_at DESC);
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

    def save_prediction(self, telemetry_id: int, prediction: dict[str, Any]) -> int:
        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """INSERT INTO wave_predictions(
                           telemetry_id, generated_at, target_at, horizon_minutes,
                           current_wave_height, predicted_wave_height, confidence,
                           sea_condition, model, model_version, status, source
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (telemetry_id, prediction["generatedAt"], prediction.get("targetAt"),
                     prediction["horizonMinutes"], prediction.get("currentWaveHeight"),
                     prediction.get("predictedWaveHeight"), prediction.get("confidence"),
                     prediction.get("seaCondition"), prediction["model"], prediction["modelVersion"],
                     prediction["status"], prediction["dataSource"]),
                )
                return int(cursor.lastrowid)

    def log_event(self, recorded_at: str, event_type: str, target: str | None,
                  status: str, detail: dict[str, Any] | None = None) -> int:
        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    "INSERT INTO system_events(recorded_at, event_type, target, status, detail) VALUES (?, ?, ?, ?, ?)",
                    (recorded_at, event_type, target, status, json.dumps(detail or {}, separators=(",", ":"))),
                )
                return int(cursor.lastrowid)

    def recent_predictions(self, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = max(1, min(200, int(limit)))
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """SELECT id, telemetry_id, generated_at, target_at, horizon_minutes,
                          current_wave_height, predicted_wave_height, confidence,
                          sea_condition, model, model_version, status, source
                   FROM wave_predictions ORDER BY id DESC LIMIT ?""", (safe_limit,)
            ).fetchall()
        return [{"id": row["id"], "telemetryId": row["telemetry_id"],
                 "generatedAt": row["generated_at"], "targetAt": row["target_at"],
                 "horizonMinutes": row["horizon_minutes"], "currentWaveHeight": row["current_wave_height"],
                 "predictedWaveHeight": row["predicted_wave_height"], "confidence": row["confidence"],
                 "seaCondition": row["sea_condition"], "model": row["model"],
                 "modelVersion": row["model_version"], "status": row["status"],
                 "dataSource": row["source"]} for row in rows]

    def recent_events(self, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = max(1, min(200, int(limit)))
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT id, recorded_at, event_type, target, status, detail FROM system_events ORDER BY id DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        return [{"id": row["id"], "recordedAt": row["recorded_at"], "eventType": row["event_type"],
                 "target": row["target"], "status": row["status"], "detail": json.loads(row["detail"])}
                for row in rows]

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
