import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.audit_modules.double_entry_validator import DoubleEntryValidator


class TestDoubleEntryValidator(unittest.TestCase):
    def test_balanced_two_legged_entry(self):
        lines = [
            {"account_id": "1010", "type": "DEBIT", "amount": 1500.00},
            {"account_id": "2010", "type": "CREDIT", "amount": 1500.00}
        ]
        res = DoubleEntryValidator.validate_entry("JE-1001", lines)
        self.assertTrue(res["is_balanced"])
        self.assertEqual(res["total_debits"], 1500.00)
        self.assertEqual(res["total_credits"], 1500.00)
        self.assertEqual(res["discrepancy"], 0.0)
        self.assertIsNone(res["audit_flag"])

    def test_unbalanced_entry_detection(self):
        lines = [
            {"account_id": "1010", "type": "DEBIT", "amount": 2500.00},
            {"account_id": "2010", "type": "CREDIT", "amount": 2000.00}
        ]
        res = DoubleEntryValidator.validate_entry("JE-1002", lines)
        self.assertFalse(res["is_balanced"])
        self.assertEqual(res["discrepancy"], 500.0)
        self.assertIn("UNBALANCED_ENTRY", res["audit_flag"])

    def test_reconcile_trial_balance_multiple_entries(self):
        entries = [
            {
                "entry_id": "JE-01",
                "lines": [
                    {"account_id": "1010", "type": "DEBIT", "amount": 500},
                    {"account_id": "2010", "type": "CREDIT", "amount": 500}
                ]
            },
            {
                "entry_id": "JE-02",
                "lines": [
                    {"account_id": "5000", "type": "DEBIT", "amount": 300},
                    {"account_id": "1010", "type": "CREDIT", "amount": 200}  # $100 unbalance
                ]
            }
        ]
        recon = DoubleEntryValidator.reconcile_trial_balance(entries)
        self.assertEqual(recon["total_entries_checked"], 2)
        self.assertEqual(recon["unbalanced_entry_count"], 1)
        self.assertEqual(recon["unbalanced_entries"][0]["entry_id"], "JE-02")
        self.assertFalse(recon["is_trial_balance_reconciled"])


if __name__ == "__main__":
    unittest.main()
