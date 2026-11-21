"""
SOX-404 Voucher Sequence Integrity and Backdated Entry Auditor
Identifies missing voucher gaps in sequential audit runs and flags backdated
journal postings exceeding permissible accounting period closes.
"""

from datetime import datetime
from typing import Dict, List, Set, Tuple


class SequenceIntegrityAuditor:
    @classmethod
    def detect_sequence_gaps(cls, voucher_ids: List[int]) -> Dict:
        """
        Detects missing voucher numbers in a sequential integer series.
        """
        if not voucher_ids:
            return {
                "total_vouchers": 0,
                "has_gaps": False,
                "missing_voucher_count": 0,
                "missing_vouchers": []
            }

        sorted_ids = sorted(list(set(voucher_ids)))
        min_id = sorted_ids[0]
        max_id = sorted_ids[-1]
        expected_set = set(range(min_id, max_id + 1))
        actual_set = set(sorted_ids)

        missing = sorted(list(expected_set - actual_set))

        return {
            "total_vouchers": len(sorted_ids),
            "range": (min_id, max_id),
            "has_gaps": len(missing) > 0,
            "missing_voucher_count": len(missing),
            "missing_vouchers": missing
        }

    @classmethod
    def detect_backdated_entries(
        cls, entries: List[Dict], max_backdate_days: int = 15
    ) -> List[Dict]:
        """
        Identifies entries where effective_date is earlier than created_date by > max_backdate_days.
        entries: [{ entry_id, effective_date: 'YYYY-MM-DD', created_date: 'YYYY-MM-DD' }]
        """
        flagged = []

        for e in entries:
            try:
                eff = datetime.strptime(str(e.get("effective_date", "")).split()[0], "%Y-%m-%d")
                cre = datetime.strptime(str(e.get("created_date", "")).split()[0], "%Y-%m-%d")
                delta_days = (cre - eff).days

                if delta_days > max_backdate_days:
                    flagged.append({
                        "entry_id": e.get("entry_id"),
                        "effective_date": str(e.get("effective_date")),
                        "created_date": str(e.get("created_date")),
                        "backdated_days": delta_days,
                        "threshold_days": max_backdate_days,
                        "audit_flag": f"SOX_BACKDATED_ENTRY: Posted {delta_days} days retroactively (max allowed: {max_backdate_days})"
                    })
            except (ValueError, TypeError):
                continue

        return flagged
