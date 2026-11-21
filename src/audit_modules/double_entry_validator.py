"""
Double-Entry General Ledger Balance Verifier & Trial Balance Reconciler
Validates fundamental accounting equation: Sum(Debits) == Sum(Credits)
per journal voucher and computes ledger trial balance discrepancies.
"""

from typing import Dict, List, Tuple


class DoubleEntryValidator:
    TOLERANCE = 0.001  # Tolerance for floating-point currency representation

    @classmethod
    def validate_entry(cls, entry_id: str, lines: List[Dict]) -> Dict:
        """
        Validates that a single journal entry voucher has equal debits and credits.
        lines: [{ account_id, type: 'DEBIT'|'CREDIT', amount: float }]
        """
        if not lines:
            return {
                "entry_id": entry_id,
                "is_balanced": False,
                "total_debits": 0.0,
                "total_credits": 0.0,
                "discrepancy": 0.0,
                "error": "Empty journal entry lines"
            }

        total_debits = 0.0
        total_credits = 0.0

        for line in lines:
            amt = abs(float(line.get("amount", 0.0)))
            line_type = str(line.get("type", "")).upper().strip()
            if line_type in ("DEBIT", "DR"):
                total_debits += amt
            elif line_type in ("CREDIT", "CR"):
                total_credits += amt

        discrepancy = round(abs(total_debits - total_credits), 4)
        is_balanced = discrepancy <= cls.TOLERANCE

        return {
            "entry_id": entry_id,
            "line_count": len(lines),
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "discrepancy": discrepancy,
            "is_balanced": is_balanced,
            "audit_flag": None if is_balanced else f"UNBALANCED_ENTRY: Out of balance by {discrepancy}"
        }

    @classmethod
    def reconcile_trial_balance(cls, entries: List[Dict]) -> Dict:
        """
        Aggregates debits and credits across all entries and verifies net trial balance.
        """
        unbalanced_entries = []
        grand_debits = 0.0
        grand_credits = 0.0

        for entry in entries:
            eid = entry.get("entry_id", "UNKNOWN")
            lines = entry.get("lines", [])
            val = cls.validate_entry(eid, lines)
            grand_debits += val["total_debits"]
            grand_credits += val["total_credits"]
            if not val["is_balanced"]:
                unbalanced_entries.append(val)

        net_discrepancy = round(abs(grand_debits - grand_credits), 4)

        return {
            "total_entries_checked": len(entries),
            "unbalanced_entry_count": len(unbalanced_entries),
            "grand_debits": round(grand_debits, 2),
            "grand_credits": round(grand_credits, 2),
            "net_trial_balance_discrepancy": net_discrepancy,
            "is_trial_balance_reconciled": net_discrepancy <= cls.TOLERANCE,
            "unbalanced_entries": unbalanced_entries
        }
