import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.audit_modules.sequence_integrity import SequenceIntegrityAuditor


class TestSequenceIntegrityAuditor(unittest.TestCase):
    def test_detect_sequence_gaps(self):
        vouchers = [101, 102, 104, 105, 107]
        res = SequenceIntegrityAuditor.detect_sequence_gaps(vouchers)
        self.assertTrue(res["has_gaps"])
        self.assertEqual(res["missing_voucher_count"], 2)
        self.assertEqual(res["missing_vouchers"], [103, 106])
        self.assertEqual(res["range"], (101, 107))

    def test_unbroken_sequence_has_no_gaps(self):
        vouchers = [500, 501, 502, 503]
        res = SequenceIntegrityAuditor.detect_sequence_gaps(vouchers)
        self.assertFalse(res["has_gaps"])
        self.assertEqual(res["missing_voucher_count"], 0)

    def test_detect_backdated_entries(self):
        entries = [
            # Normal: effective on same day as creation
            {"entry_id": "JE-200", "effective_date": "2026-11-20", "created_date": "2026-11-20"},
            # Normal backdating: 5 days back within 15-day tolerance
            {"entry_id": "JE-201", "effective_date": "2026-11-15", "created_date": "2026-11-20"},
            # Severe backdating: 45 days retroactively (SOX violation)
            {"entry_id": "JE-202", "effective_date": "2026-10-01", "created_date": "2026-11-20"}
        ]
        flagged = SequenceIntegrityAuditor.detect_backdated_entries(entries, max_backdate_days=15)
        self.assertEqual(len(flagged), 1)
        self.assertEqual(flagged[0]["entry_id"], "JE-202")
        self.assertEqual(flagged[0]["backdated_days"], 50)
        self.assertIn("SOX_BACKDATED_ENTRY", flagged[0]["audit_flag"])


if __name__ == "__main__":
    unittest.main()
