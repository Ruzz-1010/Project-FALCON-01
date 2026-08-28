import unittest
import tempfile
from pathlib import Path

from falcon_edge.service import EdgeRuntime
from falcon_edge.sources import SimulatorSource
from falcon_edge.storage import TelemetryStore


class MemoryStore:
    def __init__(self, records):
        self.records = records

    def recent(self, limit):
        return list(reversed(self.records[-limit:]))


class ForecastHistoryTests(unittest.TestCase):
    def test_grouped_dashboard_contract_uses_adviser_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = EdgeRuntime(SimulatorSource(), TelemetryStore(Path(directory) / "test.db"), 2.0)
            runtime.collect_once()
            payload = runtime.current_telemetry()
            self.assertTrue({"system", "wave", "environment", "gps", "power", "security", "health", "assistant", "alerts"}.issubset(payload))
            self.assertEqual(payload["wave"]["estimationMethod"], "pressure-calibration-v1")
            self.assertEqual(payload["assistant"]["mode"], "RULE_BASED")
            self.assertNotIn("roll", payload["wave"])

    def test_status_history_supports_operator_overview_graphs(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = EdgeRuntime(SimulatorSource(), TelemetryStore(Path(directory) / "graphs.db"), 2.0)
            runtime.collect_once()
            history = runtime.v4_status()["sensorHistory"]
            self.assertTrue(history)
            self.assertTrue({"recordedAt", "windSpeed", "waterTemperature", "internalTemperature",
                             "anchorDistance", "solarPower"}.issubset(history[-1]))

    def test_tamper_requires_three_consecutive_frames(self):
        with tempfile.TemporaryDirectory() as directory:
            source = SimulatorSource()
            source.set_scenario("tamper_alert")
            runtime = EdgeRuntime(source, TelemetryStore(Path(directory) / "security.db"), 2.0)
            runtime.collect_once()
            self.assertEqual(runtime.current_telemetry()["security"]["state"], "WARNING")
            runtime.collect_once()
            self.assertEqual(runtime.current_telemetry()["security"]["state"], "WARNING")
            runtime.collect_once()
            self.assertEqual(runtime.current_telemetry()["security"]["state"], "ALERT")
    def test_smooth_scenario_boundary_keeps_recent_ai_history(self):
        records = [
            {"recordedAt": f"2026-08-11T00:00:{index * 2:02d}+00:00", "waveLevel": 0.50 + index * 0.01,
             "scenario": "normal" if index < 8 else "rough_sea", "source": "simulator"}
            for index in range(10)
        ]
        runtime = EdgeRuntime(SimulatorSource(), MemoryStore(records), 2.0)
        runtime.source.set_scenario("rough_sea")
        self.assertEqual(len(runtime.forecast_records()), 10)

    def test_abrupt_legacy_jump_still_stops_history_segment(self):
        records = [
            {"recordedAt": "2026-08-11T00:00:00+00:00", "waveLevel": 0.5, "scenario": "normal"},
            {"recordedAt": "2026-08-11T00:00:02+00:00", "waveLevel": 0.6, "scenario": "normal"},
            {"recordedAt": "2026-08-11T00:00:04+00:00", "waveLevel": 3.2, "scenario": "rough_sea"},
            {"recordedAt": "2026-08-11T00:00:06+00:00", "waveLevel": 3.3, "scenario": "rough_sea"},
        ]
        runtime = EdgeRuntime(SimulatorSource(), MemoryStore(records), 2.0)
        runtime.source.set_scenario("rough_sea")
        self.assertEqual(len(runtime.forecast_records()), 2)

    def test_duplicate_interleaved_simulator_samples_are_filtered(self):
        records = [
            {"recordedAt": "2026-08-11T00:00:00.000000+00:00", "waveLevel": 0.50, "scenario": "normal"},
            {"recordedAt": "2026-08-11T00:00:00.800000+00:00", "waveLevel": 0.62, "scenario": "normal"},
            {"recordedAt": "2026-08-11T00:00:02.000000+00:00", "waveLevel": 0.51, "scenario": "normal"},
            {"recordedAt": "2026-08-11T00:00:02.800000+00:00", "waveLevel": 0.63, "scenario": "normal"},
            {"recordedAt": "2026-08-11T00:00:04.000000+00:00", "waveLevel": 0.52, "scenario": "normal"},
        ]
        runtime = EdgeRuntime(SimulatorSource(), MemoryStore(records), 2.0)
        kept = runtime.forecast_records()
        self.assertEqual([item["waveLevel"] for item in kept], [0.52, 0.51, 0.50])


if __name__ == "__main__":
    unittest.main()
