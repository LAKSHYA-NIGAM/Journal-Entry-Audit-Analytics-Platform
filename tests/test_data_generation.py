"""
Unit tests for Synthetic Data Generation and Controlled Anomaly Injection.
"""
import pandas as pd
from src.data_generation.generate_users import generate_users, generate_departments
from src.data_generation.generate_accounts import generate_accounts
from src.data_generation.generate_journal_entries import generate_journal_entries
from src.data_generation.inject_anomalies import inject_controlled_anomalies

def test_generate_users():
    """Verifies that users have valid departments, roles, and deterministic generation."""
    users_1 = generate_users(seed=42, num_users=50)
    users_2 = generate_users(seed=42, num_users=50)
    
    assert len(users_1) == 50
    assert users_1["user_id"].nunique() == 50
    assert users_1["user_name"].equals(users_2["user_name"])
    assert "DEP_FIN" in users_1["department_id"].values

def test_generate_accounts():
    """Verifies chart of accounts structure."""
    accounts = generate_accounts()
    assert len(accounts) >= 20
    assert "account_code" in accounts.columns
    assert "account_category" in accounts.columns
    assert "Assets" in accounts["account_category"].values

def test_deterministic_journal_generation():
    """Verifies that fixed seed produces identical journal entries."""
    df1 = generate_journal_entries(num_rows=200, seed=42)
    df2 = generate_journal_entries(num_rows=200, seed=42)
    
    assert len(df1) == 200
    assert df1["amount"].equals(df2["amount"])
    assert df1["posting_date"].equals(df2["posting_date"])
    assert (df1["debit_amount"] >= 0).all()
    assert (df1["credit_amount"] >= 0).all()

def test_anomaly_injection_registry():
    """Verifies that anomaly injection preserves population count and logs ground truth."""
    base_df = generate_journal_entries(num_rows=1000, seed=42)
    config = {
        "anomaly_injection": {
            "weekend_count": 20,
            "holiday_count": 15,
            "near_threshold_count": 20,
            "round_amount_count": 25,
            "unusual_time_count": 20,
            "duplicate_count": 20,
            "missing_approval_count": 20,
            "multi_anomaly_count": 10
        }
    }
    
    mod_df, injected_df = inject_controlled_anomalies(base_df, seed=42, config=config)
    
    assert len(mod_df) == 1000
    assert not injected_df.empty
    assert "anomaly_type" in injected_df.columns
    assert "WEEKEND_POSTING" in injected_df["anomaly_type"].values
    assert "MISSING_APPROVAL" in injected_df["anomaly_type"].values
