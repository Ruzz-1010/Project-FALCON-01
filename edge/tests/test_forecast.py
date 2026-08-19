import unittest
from datetime import datetime, timedelta, timezone

from falcon_edge.forecast import build_forecast, build_wave_prediction, classify_sea_condition, evaluate_forecast


def records(count: int = 20):
    started = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [{"recordedAt": (started + timedelta(seconds=index * 2)).isoformat(),
             "source": "simulator", "waveLevel": 0.4 + index * 0.001} for index in range(count)]


class ForecastTest(unittest.TestCase):
    def test_only_approved_horizons_are_returned(self):
        result = build_forecast(records())
        self.assertEqual(set(result["horizons"]), {"5", "10", "15"})
        self.assertEqual(result["horizons"]["15"]["horizonMinutes"], 15)
        self.assertNotIn("30", result["horizons"])

    def test_ten_minute_presentation_horizon(self):
        result = build_wave_prediction(records(), 10)
        self.assertEqual(result["horizonMinutes"], 10)
        self.assertIsNone(result["lastTrainingDate"])
        self.assertIsInstance(result["inferenceTimeMs"], float)
        self.assertGreaterEqual(result["inferenceTimeMs"], 0)
        self.assertEqual(result["status"], "READY")
        self.assertGreater(len(result["forecastSeries"]), 2)
        self.assertEqual(result["forecastSeries"][0]["predictedWaveHeight"], result["currentWaveHeight"])
        self.assertEqual(result["forecastSeries"][-1]["predictedWaveHeight"], result["predictedWaveHeight"])
        self.assertLessEqual(result["forecastSeries"][-1]["lowerBound"], result["predictedWaveHeight"])
        self.assertGreaterEqual(result["forecastSeries"][-1]["upperBound"], result["predictedWaveHeight"])
        self.assertGreater(len(result["historicalPredictionSeries"]), 2)
        self.assertIn("at", result["historicalPredictionSeries"][0])

    def test_prediction_is_wave_only_and_transparent(self):
        result = build_wave_prediction(records(), 15)
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["unit"], "m")
        self.assertIn("currentWaveHeight", result)
        self.assertIn("predictedWaveHeight", result)
        self.assertIn(result["seaCondition"], {"CALM", "MODERATE", "ROUGH"})

    def test_invalid_horizon_is_rejected(self):
        with self.assertRaises(ValueError):
            build_wave_prediction(records(), 30)

    def test_wave_only_backtest(self):
        result = evaluate_forecast(records())
        self.assertEqual(set(result["metrics"]), {"waveLevel"})
        self.assertEqual(set(result["comparisons"]), {"waveLevel"})

    def test_sea_condition_thresholds(self):
        self.assertEqual(classify_sea_condition(0.4), "CALM")
        self.assertEqual(classify_sea_condition(1.2), "MODERATE")
        self.assertEqual(classify_sea_condition(3.0), "ROUGH")


if __name__ == "__main__":
    unittest.main()
