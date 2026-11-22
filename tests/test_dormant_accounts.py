import unittest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.audit_modules.dormant_account_detector import detect_dormant_account_activity


class TestDormantAccountDetector(unittest.TestCase):
    def test_detects_dormant_account_reactivation(self):
        data = pd.DataFrame([
            {'entry_id': 'E1', 'account_id': '9001', 'posting_date': '2025-01-01', 'amount': 500},
            # 180 days gap before next entry in account 9001
            {'entry_id': 'E2', 'account_id': '9001', 'posting_date': '2025-07-01', 'amount': 50000},
            # Active account 1001 with frequent entries
            {'entry_id': 'E3', 'account_id': '1001', 'posting_date': '2025-01-01', 'amount': 100},
            {'entry_id': 'E4', 'account_id': '1001', 'posting_date': '2025-01-05', 'amount': 200},
        ])

        flagged = detect_dormant_account_activity(data, dormancy_days_threshold=90, min_reactivation_amount=1000)
        self.assertEqual(len(flagged), 1)
        self.assertEqual(flagged.iloc[0]['entry_id'], 'E2')
        self.assertEqual(flagged.iloc[0]['account_id'], '9001')
        self.assertTrue(flagged.iloc[0]['days_dormant'] >= 180)


if __name__ == '__main__':
    unittest.main()
