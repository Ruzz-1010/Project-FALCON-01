import sqlite3
import tempfile
import unittest
from pathlib import Path

from falcon_edge.storage import TelemetryStore


class TelemetryStoreMigrationTests(unittest.TestCase):
    def test_legacy_prediction_table_is_migrated_and_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "falcon.db"
            connection = sqlite3.connect(database)
            connection.executescript(
                """
                CREATE TABLE telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recorded_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE wave_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telemetry_id INTEGER NOT NULL,
                    generated_at TEXT NOT NULL,
                    target_at TEXT,
                    horizon_minutes INTEGER NOT NULL CHECK(horizon_minutes IN (5, 15)),
                    current_wave_height REAL,
                    predicted_wave_height REAL,
                    confidence INTEGER,
                    sea_condition TEXT,
                    model TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL
                );
                INSERT INTO telemetry(recorded_at, source, payload)
                VALUES ('2026-08-17T00:00:00+00:00', 'simulator', '{}');
                INSERT INTO wave_predictions(
                    telemetry_id, generated_at, target_at, horizon_minutes,
                    current_wave_height, predicted_wave_height, confidence,
                    sea_condition, model, model_version, status, source
                ) VALUES (1, '2026-08-17T00:00:00+00:00', NULL, 5,
                          0.5, 0.6, 80, 'CALM', 'test', '1', 'READY', 'simulator');
                """
            )
            connection.close()

            store = TelemetryStore(database)
            self.assertEqual(store.recent_predictions()[0]["horizonMinutes"], 5)
            prediction_id = store.save_prediction(1, {
                "generatedAt": "2026-08-17T00:01:00+00:00",
                "targetAt": "2026-08-17T00:11:00+00:00",
                "horizonMinutes": 10,
                "currentWaveHeight": 0.5,
                "predictedWaveHeight": 0.55,
                "confidence": 80,
                "seaCondition": "CALM",
                "model": "test",
                "modelVersion": "1",
                "status": "READY",
                "dataSource": "simulator",
            })
            self.assertGreater(prediction_id, 1)


if __name__ == "__main__":
    unittest.main()
