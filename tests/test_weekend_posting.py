import unittest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.audit_modules.weekend_posting_detector import detect_weekend_postings


class TestWeekendPostingDetector(unittest.TestCase):
    def test_detects_saturday_and_sunday_postings(self):
        data = pd.DataFrame([
            {'entry_id': 'E1', 'posting_date': '2026-01-09', 'amount': 100},  # Friday
            {'entry_id': 'E2', 'posting_date': '2026-01-10', 'amount': 250},  # Saturday
            {'entry_id': 'E3', 'posting_date': '2026-01-11', 'amount': 300},  # Sunday
            {'entry_id': 'E4', 'posting_date': '2026-01-12', 'amount': 450},  # Monday
        ])

        flagged = detect_weekend_postings(data, date_column='posting_date')
        self.assertEqual(len(flagged), 2)
        self.assertListEqual(flagged['entry_id'].tolist(), ['E2', 'E3'])
        self.assertIn('Saturday', flagged['day_name'].values)
        self.assertIn('Sunday', flagged['day_name'].values)

    def test_handles_missing_column(self):
        empty_res = detect_weekend_postings(pd.DataFrame({'amount': [100]}))
        self.assertTrue(empty_res.empty)


if __name__ == '__main__':
    unittest.main()
