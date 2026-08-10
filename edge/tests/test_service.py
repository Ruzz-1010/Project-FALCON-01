import unittest

from falcon_edge.service import EdgeRuntime
from falcon_edge.sources import SimulatorSource


class MemoryStore:
    def __init__(self, records):
        self.records = records

    def recent(self, limit):
        return list(reversed(self.records[-limit:]))


class ForecastHistoryTests(unittest.TestCase):
    def test_smooth_scenario_boundary_keeps_recent_ai_history(self):
        records = [
            {"recordedAt": f"2026-08-11T00:00:{index:02d}+00:00", "waveLevel": 0.50 + index * 0.01,
             "scenario": "normal" if index < 8 else "rough_sea", "source": "simulator"}
            for index in range(10)
        ]
        runtime = EdgeRuntime(SimulatorSource(), MemoryStore(records), 2.0)
        runtime.source.set_scenario("rough_sea")
        self.assertEqual(len(runtime.forecast_records()), 10)

    def test_abrupt_legacy_jump_still_stops_history_segment(self):
        records = [
            {"recordedAt": "2026-08-11T00:00:00+00:00", "waveLevel": 0.5, "scenario": "normal"},
            {"recordedAt": "2026-08-11T00:00:01+00:00", "waveLevel": 0.6, "scenario": "normal"},
            {"recordedAt": "2026-08-11T00:00:02+00:00", "waveLevel": 3.2, "scenario": "rough_sea"},
            {"recordedAt": "2026-08-11T00:00:03+00:00", "waveLevel": 3.3, "scenario": "rough_sea"},
        ]
        runtime = EdgeRuntime(SimulatorSource(), MemoryStore(records), 2.0)
        runtime.source.set_scenario("rough_sea")
        self.assertEqual(len(runtime.forecast_records()), 2)


if __name__ == "__main__":
    unittest.main()
