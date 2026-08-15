import json
import unittest

from falcon_edge.sources import parse_telemetry_line


class SerialTelemetryTests(unittest.TestCase):
    def test_version_one_frame_is_flattened_for_edge_rules(self):
        line = json.dumps({"protocol": "falcon.telemetry", "version": 1, "sequence": 7,
                           "uptimeMs": 4200, "source": "sensor", "monitoring": True,
                           "sensors": {"bar02": "DETECTED"},
                           "measurements": {"waveLevel": 0.42, "waterPressure": 115.1}})
        payload = parse_telemetry_line(line)
        self.assertEqual(payload["sequence"], 7)
        self.assertEqual(payload["uptime"], 4)
        self.assertEqual(payload["waveLevel"], 0.42)
        self.assertEqual(payload["sensorStatus"]["bar02"], "DETECTED")

    def test_unknown_protocol_version_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_telemetry_line('{"protocol":"falcon.telemetry","version":2,"sequence":1,"measurements":{}}')


if __name__ == "__main__":
    unittest.main()
