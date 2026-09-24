"""
Unit tests for the 7 Financial Control SQL Audit Rules.
Uses small, deterministic test fixtures to verify exact rule logic.
"""
from typing import Optional
import pandas as pd
import numpy as np
from src.pipeline.run_audit_tests import execute_audit_tests

def base_sample_df() -> pd.DataFrame:
    """Provides a deterministic base DataFrame of test transactions."""
    return pd.DataFrame([
        {
            "journal_id": "JE_TEST_001",
            "posting_date": "2024-04-10",  # Wednesday (Weekday, Normal)
            "posting_time": "11:30:00",    # Normal business hours
            "user_id": "USR_1010",
            "department_id": "DEP_ACC",
            "account_code": "6060",
            "account_name": "Office Supplies",
            "entry_type": "DEBIT",
            "debit_amount": 12450.75,
            "credit_amount": 0.00,
            "amount": 12450.75,
            "description": "Stationery supplies",
            "currency": "INR",
            "approval_status": "AUTO_APPROVED",
            "approver_id": "USR_1002",
            "source_system": "SAP_S4HANA",
            "vendor_id": "VEND_1001",
            "invoice_id": "INV-100",
            "created_timestamp": "2024-04-10 11:30:00"
        }
    ])

def test_weekend_detection(sample_df: Optional[pd.DataFrame] = None):
    """Verifies that Saturday and Sunday postings are accurately flagged."""
    df = sample_df.copy() if sample_df is not None else base_sample_df()
    # Add Saturday (2024-04-13) and Sunday (2024-04-14)
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_SAT", "posting_date": "2024-04-13"}
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_SUN", "posting_date": "2024-04-14"}
    
    res = execute_audit_tests(df=df)
    flags = dict(zip(res["journal_id"], res["weekend_flag"]))
    
    assert flags["JE_TEST_001"] == 0, "Wednesday should not be flagged as weekend"
    assert flags["JE_SAT"] == 1, "Saturday must be flagged as weekend"
    assert flags["JE_SUN"] == 1, "Sunday must be flagged as weekend"

def test_holiday_detection(sample_df: Optional[pd.DataFrame] = None):
    """Verifies that statutory holidays (e.g. Independence Day) are flagged."""
    df = sample_df.copy() if sample_df is not None else base_sample_df()
    # Add Independence Day 2024-08-15
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_HOLIDAY", "posting_date": "2024-08-15"}
    
    res = execute_audit_tests(df=df)
    flags = dict(zip(res["journal_id"], res["holiday_flag"]))
    names = dict(zip(res["journal_id"], res["holiday_name"]))
    
    assert flags["JE_TEST_001"] == 0
    assert flags["JE_HOLIDAY"] == 1
    assert "Independence Day" in names["JE_HOLIDAY"]

def test_threshold_detection(sample_df: Optional[pd.DataFrame] = None):
    """Verifies that transactions within 90%-100% of threshold (₹450k-500k) are flagged."""
    df = sample_df.copy() if sample_df is not None else base_sample_df()
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_BELOW_WINDOW", "amount": 440000.00}
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_NEAR_THRESHOLD", "amount": 485000.00}
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_AT_THRESHOLD", "amount": 500000.00, "approval_status": "APPROVED", "approver_id": "USR_1001"}
    
    res = execute_audit_tests(df=df)
    flags = dict(zip(res["journal_id"], res["threshold_flag"]))
    
    assert flags["JE_BELOW_WINDOW"] == 0, "₹440k is below 90% threshold window"
    assert flags["JE_NEAR_THRESHOLD"] == 1, "₹485k is near threshold (90-100%)"
    assert flags["JE_AT_THRESHOLD"] == 0, "₹500k is at/above threshold, not near"

def test_round_amount_detection(sample_df: Optional[pd.DataFrame] = None):
    """Verifies that clean multiples of 10k, 50k, 100k, 500k are flagged."""
    df = sample_df.copy() if sample_df is not None else base_sample_df()
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_ROUND_100K", "amount": 100000.00}
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_NON_ROUND", "amount": 100450.25}
    
    res = execute_audit_tests(df=df)
    flags = dict(zip(res["journal_id"], res["round_amount_flag"]))
    levels = dict(zip(res["journal_id"], res["rounding_level"]))
    
    assert flags["JE_ROUND_100K"] == 1
    assert levels["JE_ROUND_100K"] == "Multiple of 100,000"
    assert flags["JE_NON_ROUND"] == 0
    assert levels["JE_NON_ROUND"] == "Not Round"

def test_unusual_time_detection(sample_df: Optional[pd.DataFrame] = None):
    """Verifies that postings outside 06:00 to 22:00 are flagged."""
    df = sample_df.copy() if sample_df is not None else base_sample_df()
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_NIGHT_02AM", "posting_time": "02:15:30"}
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_LATE_23PM", "posting_time": "23:45:00"}
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_NORMAL_DAY", "posting_time": "14:20:00"}
    
    res = execute_audit_tests(df=df)
    flags = dict(zip(res["journal_id"], res["unusual_time_flag"]))
    
    assert flags["JE_NIGHT_02AM"] == 1
    assert flags["JE_LATE_23PM"] == 1
    assert flags["JE_NORMAL_DAY"] == 0

def test_duplicate_detection(sample_df: Optional[pd.DataFrame] = None):
    """Verifies that entries with identical key attributes are flagged with group ID."""
    df = sample_df.copy() if sample_df is not None else base_sample_df()
    # Clone record with new journal_id
    df.loc[len(df)] = {**df.iloc[0].to_dict(), "journal_id": "JE_DUP_COPY"}
    
    res = execute_audit_tests(df=df)
    flags = dict(zip(res["journal_id"], res["duplicate_flag"]))
    counts = dict(zip(res["journal_id"], res["duplicate_count"]))
    
    assert flags["JE_TEST_001"] == 1
    assert flags["JE_DUP_COPY"] == 1
    assert counts["JE_TEST_001"] == 2
    assert counts["JE_DUP_COPY"] == 2

def test_missing_approval_detection(sample_df: Optional[pd.DataFrame] = None):
    """Verifies that material transactions missing approvals or rejected entries are flagged."""
    df = sample_df.copy() if sample_df is not None else base_sample_df()
    # 1. Large transaction missing approver ID
    df.loc[len(df)] = {
        **df.iloc[0].to_dict(),
        "journal_id": "JE_MISSING_APPROVER",
        "amount": 750000.00,
        "approval_status": "APPROVED",
        "approver_id": None
    }
    # 2. Large transaction with status PENDING
    df.loc[len(df)] = {
        **df.iloc[0].to_dict(),
        "journal_id": "JE_PENDING_APPROVAL",
        "amount": 600000.00,
        "approval_status": "PENDING",
        "approver_id": "USR_1001"
    }
    # 3. Rejected entry posted to GL
    df.loc[len(df)] = {
        **df.iloc[0].to_dict(),
        "journal_id": "JE_REJECTED",
        "amount": 50000.00,
        "approval_status": "REJECTED",
        "approver_id": "USR_1001"
    }
    
    res = execute_audit_tests(df=df)
    flags = dict(zip(res["journal_id"], res["approval_exception_flag"]))
    reasons = dict(zip(res["journal_id"], res["approval_exception_reason"]))
    
    assert flags["JE_MISSING_APPROVER"] == 1
    assert "missing approver ID" in reasons["JE_MISSING_APPROVER"]
    assert flags["JE_PENDING_APPROVAL"] == 1
    assert "not approved" in reasons["JE_PENDING_APPROVAL"]
    assert flags["JE_REJECTED"] == 1
    assert "Rejected transaction" in reasons["JE_REJECTED"]
