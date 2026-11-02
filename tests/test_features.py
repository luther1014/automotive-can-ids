import unittest
import pandas as pd
from canids.features import can_id_to_int, payload_to_bytes, frame_features


class FeaturesTest(unittest.TestCase):
    def test_hex_string_not_decimal(self):
        self.assertEqual(can_id_to_int('191'), 0x191)
        self.assertEqual(can_id_to_int('0C1'), 0x0C1)
    def test_bytes(self):
        self.assertEqual(payload_to_bytes('0F00'), [15, 0])
        self.assertEqual(payload_to_bytes(''), [])
        self.assertIsNone(payload_to_bytes('0F0'))
    def test_frame(self):
        frame = pd.DataFrame({'arbitration_id': ['1F5'], 'data_field': ['0F0F002100000300']})
        row = frame_features(frame).iloc[0]
        self.assertEqual(row.can_id, 0x1F5)
        self.assertEqual(row.dlc, 8)
        self.assertEqual(row.byte_3, 0x21)

if __name__ == '__main__':
    unittest.main()
