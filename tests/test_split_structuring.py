import unittest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.audit_modules.split_structuring_detector import detect_split_structuring


class TestSplitStructuringDetector(unittest.TestCase):
    def test_detects_transactions_just_below_ten_thousand(self):
        data = pd.DataFrame([
            {'entry_id': 'E1', 'preparer_id': 'USER_1', 'amount': 9950.00},  # Suspect (just below 10k)
            {'entry_id': 'E2', 'preparer_id': 'USER_1', 'amount': 9800.00},  # Suspect
            {'entry_id': 'E3', 'preparer_id': 'USER_2', 'amount': 15000.00}, # Explicitly over 10k
            {'entry_id': 'E4', 'preparer_id': 'USER_3', 'amount': 250.00},   # Normal small entry
        ])

        flagged = detect_split_structuring(data, approval_limit=10000.0, proximity_pct=0.15)
        self.assertEqual(len(flagged), 2)
        self.assertListEqual(flagged['entry_id'].tolist(), ['E1', 'E2'])
        self.assertTrue(all(flagged['is_split_suspect']))


if __name__ == '__main__':
    unittest.main()
