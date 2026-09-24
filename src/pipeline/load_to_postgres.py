"""
Data Ingestion Pipeline Module.
Loads reference tables, users, chart of accounts, journal entries,
and ground-truth anomalies into PostgreSQL / SQLite database.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from src.utils.logging import get_logger
from src.utils.database import DatabaseManager

logger = get_logger("data_loader")

def load_all_data(
    db: DatabaseManager,
    users_df: pd.DataFrame,
    accounts_df: pd.DataFrame,
    departments_df: pd.DataFrame,
    holidays_file: Path,
    journal_entries_df: pd.DataFrame,
    injected_df: pd.DataFrame,
    chunksize: int = 10000
):
    """
    Initializes database schema and ingests all datasets into relational tables.
    """
    logger.info("Starting complete database initialization and bulk data ingestion...")
    
    # 1. Initialize schema
    db.init_schema()
    
    # 2. Ingest Departments
    db.bulk_insert_df("departments", departments_df, chunksize=chunksize)
    
    # 3. Ingest Users
    db.bulk_insert_df("users", users_df, chunksize=chunksize)
    
    # 4. Ingest Accounts
    db.bulk_insert_df("accounts", accounts_df, chunksize=chunksize)
    
    # 5. Ingest Holidays
    if holidays_file.exists():
        holidays_df = pd.read_csv(holidays_file)
        db.bulk_insert_df("holidays", holidays_df, chunksize=chunksize)
        
    # 6. Ingest Approval Rules
    rules_df = pd.DataFrame([
        {"rule_id": "RULE_STANDARD", "transaction_type": "GENERAL_GL", "threshold_amount": 500000.00, "required_approval_level": "Finance Director"},
        {"rule_id": "RULE_EXPENSE", "transaction_type": "OPERATING_EXPENSE", "threshold_amount": 500000.00, "required_approval_level": "Department Head & Controller"},
        {"rule_id": "RULE_CAPEX", "transaction_type": "CAPITAL_EXPENDITURE", "threshold_amount": 500000.00, "required_approval_level": "CFO Approval"},
        {"rule_id": "RULE_MANUAL", "transaction_type": "MANUAL_JOURNAL", "threshold_amount": 500000.00, "required_approval_level": "Senior Controller"}
    ])
    db.bulk_insert_df("approval_rules", rules_df, chunksize=chunksize)
    
    # 7. Ingest Journal Entries (500k+ rows)
    db.bulk_insert_df("journal_entries", journal_entries_df, chunksize=chunksize)
    
    # 8. Ingest Ground Truth Injected Anomalies
    if not injected_df.empty:
        db.bulk_insert_df("injected_anomalies", injected_df, chunksize=chunksize)
        
    logger.info("Database ingestion completed successfully.")
