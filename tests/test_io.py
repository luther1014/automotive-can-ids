import tempfile
import unittest
from pathlib import Path
from canids.io import load_sample, csv_has_header


class IOTest(unittest.TestCase):
    def test_both_csv_header_styles(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / 'train_01'
            folder.mkdir()
            no_header = folder / 'a.csv'
            with_header = folder / 'b.csv'
            no_header.write_text('1672531209.2,191,0001,0\n1672531209.3,1F5,00FF,1\n')
            with_header.write_text('timestamp,arbitration_id,data_field,attack\n1672531210.1,0C1,00,0\n')
            self.assertFalse(csv_has_header(no_header))
            self.assertTrue(csv_has_header(with_header))
            sample = load_sample(root, 'train_01', fraction=1)
            self.assertEqual(len(sample), 3)
            self.assertEqual(sum(sample.attack), 1)
            self.assertEqual(sample.source_file.nunique(), 2)

if __name__ == '__main__':
    unittest.main()
