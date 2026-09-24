"""
SQL Audit Tests Execution Engine.
Executes the 7 core financial control exception tests against the journal entry population,
generating the consolidated exception results with explainable risk scores and prioritization tiers.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from src.utils.logging import get_logger
from src.utils.database import DatabaseManager
from src.utils.config import BASE_DIR
from src.analytics.risk_scoring import calculate_risk_scores

logger = get_logger("audit_test_runner")

def execute_audit_tests(
    db: Optional[DatabaseManager] = None,
    df: Optional[pd.DataFrame] = None,
    config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Executes all 7 SQL audit tests and computes exception flags, risk score, and risk category.
    Supports direct database view queries or high-speed vectorized calculation.
    """
    logger.info("Executing 7 core financial control audit tests...")
    
    threshold_amt = float(config.get("approval", {}).get("threshold", 500000.00)) if config else 500000.00
    near_pct = float(config.get("approval", {}).get("near_threshold_percentage", 0.90)) if config else 0.90
    near_lower = threshold_amt * near_pct
    
    unusual_before = int(config.get("posting_time", {}).get("unusual_before", 6)) if config else 6
    unusual_after = int(config.get("posting_time", {}).get("unusual_after", 22)) if config else 22
    
    holidays_file = BASE_DIR / "config" / "holidays.csv"
    holiday_map = {}
    if holidays_file.exists():
        h_df = pd.read_csv(holidays_file)
        holiday_map = dict(zip(h_df["holiday_date"].astype(str), h_df["holiday_name"]))
        
    # If df is not provided, query from database
    if df is None:
        if db is None:
            raise ValueError("Either 'df' or 'db' must be provided to execute_audit_tests.")
        logger.info("Loading journal entries from database for audit test execution...")
        df = db.query_to_df("SELECT * FROM journal_entries;")
        
    result_df = df.copy()
    
    # -------------------------------------------------------------------------
    # Test 1: Weekend Posting Exception
    # -------------------------------------------------------------------------
    logger.info("Running SQL Audit Test 1: Weekend Posting...")
    dates = pd.to_datetime(result_df["posting_date"])
    # In python dt.weekday: 5 = Saturday, 6 = Sunday
    is_weekend = dates.dt.weekday.isin([5, 6])
    result_df["weekend_flag"] = np.where(is_weekend, 1, 0)
    
    # -------------------------------------------------------------------------
    # Test 2: Holiday Posting Exception
    # -------------------------------------------------------------------------
    logger.info("Running SQL Audit Test 2: Holiday Posting...")
    str_dates = result_df["posting_date"].astype(str)
    result_df["holiday_flag"] = np.where(str_dates.isin(holiday_map.keys()), 1, 0)
    result_df["holiday_name"] = str_dates.map(holiday_map).fillna("None")
    
    # -------------------------------------------------------------------------
    # Test 3: Near Approval Threshold Exception
    # -------------------------------------------------------------------------
    logger.info("Running SQL Audit Test 3: Near Approval Threshold...")
    amounts = result_df["amount"].astype(float)
    is_near = (amounts >= near_lower) & (amounts < threshold_amt)
    result_df["threshold_flag"] = np.where(is_near, 1, 0)
    result_df["distance_from_threshold"] = np.where(
        amounts < threshold_amt,
        np.round(threshold_amt - amounts, 2),
        0.00
    )
    
    # -------------------------------------------------------------------------
    # Test 4: Round Amount Exception
    # -------------------------------------------------------------------------
    logger.info("Running SQL Audit Test 4: Round Amount Detection...")
    # Multiples of 10k: amount >= 10000 and amount % 10000 == 0
    is_round = (amounts >= 10000.00) & (amounts % 10000.00 == 0.0)
    result_df["round_amount_flag"] = np.where(is_round, 1, 0)
    
    round_conds = [
        (amounts >= 1000000.00) & (amounts % 1000000.00 == 0.0),
        (amounts >= 500000.00) & (amounts % 500000.00 == 0.0),
        (amounts >= 250000.00) & (amounts % 250000.00 == 0.0),
        (amounts >= 100000.00) & (amounts % 100000.00 == 0.0),
        (amounts >= 50000.00) & (amounts % 50000.00 == 0.0),
        (amounts >= 10000.00) & (amounts % 10000.00 == 0.0)
    ]
    round_labels = [
        "Multiple of 1,000,000",
        "Multiple of 500,000",
        "Multiple of 250,000",
        "Multiple of 100,000",
        "Multiple of 50,000",
        "Multiple of 10,000"
    ]
    result_df["rounding_level"] = np.select(round_conds, round_labels, default="Not Round")
    
    # -------------------------------------------------------------------------
    # Test 5: Unusual Posting Time Exception
    # -------------------------------------------------------------------------
    logger.info("Running SQL Audit Test 5: Unusual Posting Time...")
    posting_hours = result_df["posting_time"].astype(str).str.split(":").str[0].astype(int)
    is_unusual_time = (posting_hours < unusual_before) | (posting_hours >= unusual_after)
    result_df["unusual_time_flag"] = np.where(is_unusual_time, 1, 0)
    
    # -------------------------------------------------------------------------
    # Test 6: Duplicate Entry Detection
    # -------------------------------------------------------------------------
    logger.info("Running SQL Audit Test 6: Duplicate Journal Entry Detection...")
    dup_cols = ["user_id", "posting_date", "account_code", "amount", "vendor_id", "invoice_id"]
    dup_counts = result_df.groupby(dup_cols)["journal_id"].transform("count")
    result_df["duplicate_count"] = dup_counts
    result_df["duplicate_flag"] = np.where(dup_counts > 1, 1, 0)
    
    # Duplicate group IDs for matching groups
    dup_groups = result_df.groupby(dup_cols).ngroup()
    result_df["duplicate_group_id"] = np.where(dup_counts > 1, dup_groups + 1, np.nan)
    
    # -------------------------------------------------------------------------
    # Test 7: Approval Control Exception
    # -------------------------------------------------------------------------
    logger.info("Running SQL Audit Test 7: Approval Control Verification...")
    status = result_df["approval_status"].astype(str)
    approver = result_df["approver_id"]
    
    cond_missing_approver = (amounts >= threshold_amt) & (approver.isna() | (approver == "") | (approver == "None"))
    cond_not_approved = (amounts >= threshold_amt) & (status != "APPROVED")
    cond_rejected = (status == "REJECTED")
    cond_non_standard = (~status.isin(["APPROVED", "AUTO_APPROVED", "SYSTEM"])) & (amounts >= 100000.00)
    
    approval_flag = cond_missing_approver | cond_not_approved | cond_rejected | cond_non_standard
    result_df["approval_exception_flag"] = np.where(approval_flag, 1, 0)
    
    reason_conds = [
        cond_missing_approver,
        cond_not_approved,
        cond_rejected,
        cond_non_standard
    ]
    reason_labels = [
        "Material transaction missing approver ID",
        "Material transaction not approved",
        "Rejected transaction posted to GL",
        "Non-standard approval status on large entry"
    ]
    result_df["approval_exception_reason"] = np.select(reason_conds, reason_labels, default="None")
    
    # -------------------------------------------------------------------------
    # Combined Risk Scoring and Categorization
    # -------------------------------------------------------------------------
    result_df = calculate_risk_scores(result_df, config=config)
    
    logger.info("All 7 SQL audit tests executed successfully.")
    return result_df
