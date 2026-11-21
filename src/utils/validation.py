"""
Automated Data Quality & Audit Integrity Validation Module.
Performs comprehensive checks on data populations, referential integrity, accounting consistency,
and ground-truth anomaly detection metrics.
"""
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from src.utils.logging import get_logger

logger = get_logger("data_validation")

class DataValidator:
    """
    Validates data quality, relational integrity, and anomaly detection accuracy.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validation_results: Dict[str, Any] = {}

    def validate_journal_entries_df(
        self,
        df: pd.DataFrame,
        users_df: pd.DataFrame,
        accounts_df: pd.DataFrame,
        departments_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Executes complete validation suite on journal entries DataFrame.
        """
        logger.info("Running automated data quality & accounting integrity validation checks...")
        checks = {}
        all_passed = True

        # 1. Row count validation
        expected_rows = self.config.get("dataset", {}).get("rows", 500000)
        actual_rows = len(df)
        checks["row_count"] = {
            "passed": actual_rows == expected_rows,
            "expected": expected_rows,
            "actual": actual_rows,
            "message": f"Expected {expected_rows:,} rows, found {actual_rows:,} rows"
        }
        if not checks["row_count"]["passed"]:
            all_passed = False

        # 2. Duplicate Primary Key validation
        dup_keys = df["journal_id"].duplicated().sum()
        checks["duplicate_journal_ids"] = {
            "passed": dup_keys == 0,
            "duplicate_count": int(dup_keys),
            "message": f"Found {dup_keys} duplicate journal_id values (must be 0)"
        }
        if not checks["duplicate_journal_ids"]["passed"]:
            all_passed = False

        # 3. Critical Columns Null check
        critical_cols = [
            "journal_id", "posting_date", "posting_time", "user_id",
            "department_id", "account_code", "amount", "entry_type", "approval_status"
        ]
        null_counts = {col: int(df[col].isnull().sum()) for col in critical_cols if col in df.columns}
        total_nulls = sum(null_counts.values())
        checks["null_validation"] = {
            "passed": total_nulls == 0,
            "null_counts": null_counts,
            "message": f"Total critical column nulls: {total_nulls}"
        }
        if not checks["null_validation"]["passed"]:
            all_passed = False

        # 4. Amount Validation
        if "amount" in df.columns and len(df) > 0:
            numeric_amounts = pd.to_numeric(df["amount"], errors="coerce")
            finite_floats = numeric_amounts.fillna(0.0).to_numpy(dtype=float)
            invalid_amounts = (numeric_amounts <= 0) | numeric_amounts.isna() | np.isinf(finite_floats)
            invalid_count = int(invalid_amounts.sum())
            valid_series = numeric_amounts.dropna()
            min_val = float(valid_series.min()) if not valid_series.empty else 0.0
            max_val = float(valid_series.max()) if not valid_series.empty else 0.0
            checks["amount_validation"] = {
                "passed": invalid_count == 0,
                "invalid_count": invalid_count,
                "min_amount": min_val,
                "max_amount": max_val,
                "message": f"All amounts are positive and finite: {invalid_count == 0}"
            }
        else:
            checks["amount_validation"] = {
                "passed": False,
                "invalid_count": len(df),
                "min_amount": 0.0,
                "max_amount": 0.0,
                "message": "Missing 'amount' column or empty dataframe"
            }

        if not checks["amount_validation"]["passed"]:
            all_passed = False

        # 5. Accounting Consistency Validation
        has_acct_cols = (
            "debit_amount" in df.columns and 
            "credit_amount" in df.columns and 
            "entry_type" in df.columns and 
            "amount" in df.columns
        )
        if has_acct_cols:
            invalid_debits = (df["debit_amount"] < 0).sum()
            invalid_credits = (df["credit_amount"] < 0).sum()
            mismatch_amounts = ((df["entry_type"] == "DEBIT") & (df["debit_amount"] != df["amount"])).sum() + \
                               ((df["entry_type"] == "CREDIT") & (df["credit_amount"] != df["amount"])).sum()
            accounting_passed = (invalid_debits == 0) and (invalid_credits == 0) and (mismatch_amounts == 0)
            checks["accounting_consistency"] = {
                "passed": bool(accounting_passed),
                "invalid_debits": int(invalid_debits),
                "invalid_credits": int(invalid_credits),
                "mismatch_amounts": int(mismatch_amounts),
                "message": "Debit/Credit non-negative and consistent with entry amount"
            }
        else:
            accounting_passed = False
            checks["accounting_consistency"] = {
                "passed": False,
                "invalid_debits": 0,
                "invalid_credits": 0,
                "mismatch_amounts": len(df),
                "message": "Missing required accounting columns"
            }
        if not accounting_passed:
            all_passed = False

        # 6. Referential Integrity Validation
        valid_users = set(users_df["user_id"]) if "user_id" in users_df.columns else set()
        valid_accounts = set(accounts_df["account_code"]) if "account_code" in accounts_df.columns else set()
        valid_departments = set(departments_df["department_id"]) if "department_id" in departments_df.columns else set()

        orphan_users = int((~df["user_id"].isin(valid_users)).sum()) if "user_id" in df.columns else len(df)
        orphan_accounts = int((~df["account_code"].isin(valid_accounts)).sum()) if "account_code" in df.columns else len(df)
        orphan_depts = int((~df["department_id"].isin(valid_departments)).sum()) if "department_id" in df.columns else len(df)

        ref_passed = (orphan_users == 0) and (orphan_accounts == 0) and (orphan_depts == 0)
        checks["referential_integrity"] = {
            "passed": bool(ref_passed),
            "orphan_users": int(orphan_users),
            "orphan_accounts": int(orphan_accounts),
            "orphan_departments": int(orphan_depts),
            "message": f"Foreign keys verified: users={orphan_users}, accounts={orphan_accounts}, depts={orphan_depts}"
        }
        if not ref_passed:
            all_passed = False

        # 7. Date Range Validation
        start_date = str(self.config.get("dataset", {}).get("start_date", "2024-04-01"))
        end_date = str(self.config.get("dataset", {}).get("end_date", "2025-03-31"))
        if "posting_date" in df.columns and len(df) > 0:
            posting_dates = pd.to_datetime(df["posting_date"], errors="coerce")
            valid_dates = posting_dates.dropna()
            out_of_range = ((valid_dates < pd.to_datetime(start_date)) | (valid_dates > pd.to_datetime(end_date))).sum() + (len(df) - len(valid_dates))
            min_d = str(valid_dates.min().date()) if not valid_dates.empty else "N/A"
            max_d = str(valid_dates.max().date()) if not valid_dates.empty else "N/A"
            checks["date_range_validation"] = {
                "passed": int(out_of_range) == 0,
                "out_of_range_count": int(out_of_range),
                "min_date": min_d,
                "max_date": max_d,
                "message": f"Dates within fiscal window {start_date} to {end_date}"
            }
        else:
            checks["date_range_validation"] = {
                "passed": False,
                "out_of_range_count": len(df),
                "min_date": "N/A",
                "max_date": "N/A",
                "message": "Missing 'posting_date' column or empty dataframe"
            }
        if not checks["date_range_validation"]["passed"]:
            all_passed = False

        checks["overall_status"] = "PASSED" if all_passed else "FAILED"
        self.validation_results = checks
        
        logger.info(f"Data Quality Validation: {checks['overall_status']}")
        return checks

    def evaluate_detection_accuracy(
        self,
        injected_df: pd.DataFrame,
        exceptions_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Calculates precision, recall (detection rate), and ground-truth validation metrics.
        """
        logger.info("Evaluating audit test detection performance against ground-truth injected anomalies...")
        
        # Mapping between injected anomaly types and audit test flag columns
        rule_map = {
            "WEEKEND_POSTING": "weekend_flag",
            "HOLIDAY_POSTING": "holiday_flag",
            "NEAR_THRESHOLD": "threshold_flag",
            "ROUND_AMOUNT": "round_amount_flag",
            "UNUSUAL_TIME": "unusual_time_flag",
            "DUPLICATE_ENTRY": "duplicate_flag",
            "MISSING_APPROVAL": "approval_exception_flag"
        }

        # Merge exceptions with injected ground truth
        merged = injected_df.merge(
            exceptions_df,
            on="journal_id",
            how="left"
        )

        type_metrics = {}
        total_injected = len(injected_df)
        total_detected_injected = 0

        for anomaly_type, flag_col in rule_map.items():
            sub = merged[merged["anomaly_type"] == anomaly_type]
            injected_cnt = len(sub)
            if injected_cnt == 0:
                continue

            detected_cnt = int((sub[flag_col] == 1).sum()) if flag_col in sub.columns else 0
            missed_cnt = injected_cnt - detected_cnt
            det_rate = (detected_cnt / injected_cnt * 100.0) if injected_cnt > 0 else 0.0

            total_detected_injected += detected_cnt

            type_metrics[anomaly_type] = {
                "injected_count": injected_cnt,
                "detected_count": detected_cnt,
                "missed_count": missed_cnt,
                "detection_rate_pct": round(det_rate, 2),
                "audit_flag": flag_col
            }

        overall_detection_rate = (total_detected_injected / total_injected * 100.0) if total_injected > 0 else 0.0

        summary = {
            "total_injected_anomalies": total_injected,
            "total_detected_injected": total_detected_injected,
            "overall_detection_rate_pct": round(overall_detection_rate, 2),
            "by_anomaly_type": type_metrics,
            "total_population_exceptions": int((exceptions_df["exception_count"] > 0).sum()) if "exception_count" in exceptions_df.columns else len(exceptions_df)
        }

        logger.info(f"Ground-Truth Detection Rate: {summary['overall_detection_rate_pct']}% ({total_detected_injected:,}/{total_injected:,})")
        return summary
