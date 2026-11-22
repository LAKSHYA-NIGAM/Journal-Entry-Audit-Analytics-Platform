import unittest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.audit_modules.round_number_detector import detect_round_number_entries


class TestRoundNumberDetector(unittest.TestCase):
    def test_detects_clean_thousand_multiples(self):
        data = pd.DataFrame([
            {'entry_id': 'E1', 'account_id': '1010', 'amount': 10000.00},
            {'entry_id': 'E2', 'account_id': '1020', 'amount': 4523.67},
            {'entry_id': 'E3', 'account_id': '1030', 'amount': 25000.00},
            {'entry_id': 'E4', 'account_id': '1040', 'amount': 12.50},
        ])

        flagged = detect_round_number_entries(data, threshold_round=1000)
        self.assertEqual(len(flagged), 2)
        self.assertListEqual(flagged['entry_id'].tolist(), ['E1', 'E3'])

    def test_empty_or_missing_columns(self):
        empty_res = detect_round_number_entries(pd.DataFrame())
        self.assertTrue(empty_res.empty)


if __name__ == '__main__':
    unittest.main()
