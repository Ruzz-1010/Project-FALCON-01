import unittest
from datetime import datetime, timedelta, timezone

from falcon_edge.forecast import build_forecast, evaluate_forecast


class ForecastTest(unittest.TestCase):
    def test_forecast_contains_all_demo_sensor_predictions(self):
        started = datetime(2026, 1, 1, tzinfo=timezone.utc)
        records = []
        for index in range(20):
            records.append({
                "recordedAt": (started + timedelta(seconds=index * 2)).isoformat(),
                "waveLevel": 0.4 + index * 0.001,
                "windSpeed": 8.0 + index * 0.01,
                "waterLevel": 1.4 + index * 0.001,
                "temperature": 28.0 + index * 0.002,
                "battery": 90.0 - index * 0.001,
            })
        result = build_forecast(records)
        self.assertEqual(result["status"], "READY")
        self.assertEqual(set(result["horizons"]), {"5", "15", "30"})
        self.assertEqual(len(result["horizons"]["15"]), 5)
        self.assertGreater(result["horizons"]["15"]["windSpeed"]["confidence"], 0)

        validation = evaluate_forecast(records)
        self.assertEqual(validation["status"], "READY")
        self.assertIsNotNone(validation["overallScore"])
        self.assertGreater(len(validation["comparisons"]), 0)
        self.assertIn("waveLevel", validation["metrics"])


if __name__ == "__main__":
    unittest.main()
