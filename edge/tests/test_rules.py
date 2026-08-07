import unittest

from falcon_edge.rules import analyze
from falcon_edge.sources import SimulatorSource


class RulesTest(unittest.TestCase):
    def test_nominal_reading_has_no_alerts(self):
        data = {"battery": 87, "temperature": 28.4, "tilt": 1.8, "waveLevel": 0.4}
        self.assertEqual(analyze(data), [])

    def test_critical_conditions_are_detected(self):
        data = {"battery": 10, "temperature": 28, "tilt": 40, "waveLevel": 0.5}
        codes = {alert.code for alert in analyze(data)}
        self.assertIn("BATTERY_CRITICAL", codes)
        self.assertIn("TILT_CRITICAL", codes)

    def test_missing_sensor_is_reported(self):
        data = {"battery": 90, "temperature": 28, "tilt": 2}
        self.assertIn("WAVELEVEL_INVALID", {alert.code for alert in analyze(data)})

    def test_virtual_scenarios_trigger_expected_rules(self):
        source = SimulatorSource()
        expected = {
            "rough_sea": "WAVE_HIGH",
            "low_battery": "BATTERY_LOW",
            "overheating": "WATER_TEMP_HIGH",
            "sensor_fault": "WAVELEVEL_INVALID",
        }
        for scenario, code in expected.items():
            with self.subTest(scenario=scenario):
                source.set_scenario(scenario)
                self.assertIn(code, {alert.code for alert in analyze(source.read())})


if __name__ == "__main__":
    unittest.main()
