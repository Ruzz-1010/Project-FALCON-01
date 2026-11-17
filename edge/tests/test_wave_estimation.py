import unittest

from falcon_edge.wave_estimation import apply_pressure_window, estimate_wave_window, pressure_to_displacement


class PressureWaveEstimationTests(unittest.TestCase):
    def test_pressure_difference_is_converted_from_kpa_to_metres(self):
        displacement = pressure_to_displacement(100.5, 100.0)
        self.assertAlmostEqual(displacement, 500.0 / (1025.0 * 9.80665), places=6)

    def test_window_height_is_maximum_minus_minimum_displacement(self):
        samples = [100.0, 100.0, 100.1, 100.2, 100.3, 100.4, 100.4, 100.3]
        result = estimate_wave_window(samples, baseline_kpa=100.2)
        expected = 400.0 / (1025.0 * 9.80665)
        self.assertAlmostEqual(result["waveHeightMeters"], expected, places=6)
        self.assertEqual(result["sampleCount"], 8)

    def test_payload_requires_calibration_when_no_response_factor_is_supplied(self):
        payload = {"pressureSamplesKpa": [100.0, 100.1, 100.2, 100.3, 100.4, 100.3, 100.2, 100.1]}
        apply_pressure_window(payload)
        self.assertEqual(payload["waveHeightState"], "PRESSURE_DERIVED")
        self.assertEqual(payload["pressureCalibration"], "CALIBRATION REQUIRED")
        self.assertIn("waveLevel", payload)

    def test_response_factor_applies_depth_correction(self):
        uncorrected = pressure_to_displacement(100.5, 100.0, pressure_response_factor=1.0)
        corrected = pressure_to_displacement(100.5, 100.0, pressure_response_factor=0.5)
        self.assertAlmostEqual(corrected, uncorrected * 2, places=8)


if __name__ == "__main__":
    unittest.main()
