"""
Controlled Anomaly Injection Engine.
Injects deterministic, documented audit exceptions into the journal entry population
and maintains an exact ground-truth registry in `injected_anomalies`.
"""
import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from src.utils.logging import get_logger
from src.utils.config import BASE_DIR

logger = get_logger("anomaly_injector")

def get_weekend_dates(start_date: str, end_date: str) -> List[str]:
    """Returns list of weekend dates (Saturday & Sunday) in fiscal range."""
    all_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    return [d.strftime("%Y-%m-%d") for d in all_dates if d.weekday() in (5, 6)]

def get_holiday_dates(holidays_file: Path) -> List[str]:
    """Returns list of holiday dates from CSV."""
    if not holidays_file.exists():
        return ["2024-08-15", "2024-10-02", "2024-12-25", "2025-01-26"]
    df = pd.read_csv(holidays_file)
    return df["holiday_date"].astype(str).tolist()

def inject_controlled_anomalies(
    df: pd.DataFrame,
    seed: int = 42,
    config: Optional[Dict[str, Any]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Injects controlled audit anomalies into journal entries dataset.
    Returns (modified_df, injected_anomalies_df).
    """
    logger.info("Injecting controlled audit exceptions and creating ground-truth registry...")
    np.random.seed(seed)
    
    df = df.copy()
    total_rows = len(df)
    
    cfg = config.get("anomaly_injection", {}) if config else {}
    scale_factor = total_rows / 500000.0 if total_rows < 500000 else 1.0

    weekend_target = max(2, int(cfg.get("weekend_count", 1200) * scale_factor))
    holiday_target = max(2, int(cfg.get("holiday_count", 800) * scale_factor))
    threshold_target = max(2, int(cfg.get("near_threshold_count", 1000) * scale_factor))
    round_amount_target = max(2, int(cfg.get("round_amount_count", 1500) * scale_factor))
    unusual_time_target = max(2, int(cfg.get("unusual_time_count", 1200) * scale_factor))
    duplicate_target = max(2, int(cfg.get("duplicate_count", 900) * scale_factor))
    missing_approval_target = max(2, int(cfg.get("missing_approval_count", 1400) * scale_factor))
    multi_anomaly_target = max(2, int(cfg.get("multi_anomaly_count", 500) * scale_factor))
    
    start_date = config.get("dataset", {}).get("start_date", "2024-04-01") if config else "2024-04-01"
    end_date = config.get("dataset", {}).get("end_date", "2025-03-31") if config else "2025-03-31"
    
    weekend_dates = get_weekend_dates(start_date, end_date)
    holidays_file = BASE_DIR / "config" / "holidays.csv"
    holiday_dates = get_holiday_dates(holidays_file)
    
    injected_records: List[Dict[str, Any]] = []
    
    # Shuffle indices to assign disjoint anomaly slots
    shuffled_idx = np.random.permutation(total_rows)
    curr_offset = 0
    
    def get_slot_indices(count: int) -> np.ndarray:
        nonlocal curr_offset
        slot = shuffled_idx[curr_offset : curr_offset + count]
        curr_offset += count
        return slot

    # -------------------------------------------------------------------------
    # 1. Weekend Posting Exceptions
    # -------------------------------------------------------------------------
    weekend_idx = get_slot_indices(weekend_target)
    for idx in weekend_idx:
        w_date = np.random.choice(weekend_dates)
        df.at[idx, "posting_date"] = w_date
        t = df.at[idx, "posting_time"]
        df.at[idx, "created_timestamp"] = f"{w_date} {t}"
        
        injected_records.append({
            "journal_id": df.at[idx, "journal_id"],
            "anomaly_type": "WEEKEND_POSTING",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": f"Posting date changed to weekend date: {w_date}"
        })
    logger.info(f"Injected {len(weekend_idx):,} Weekend Posting anomalies.")

    # -------------------------------------------------------------------------
    # 2. Holiday Posting Exceptions
    # -------------------------------------------------------------------------
    holiday_idx = get_slot_indices(holiday_target)
    for idx in holiday_idx:
        h_date = np.random.choice(holiday_dates)
        df.at[idx, "posting_date"] = h_date
        t = df.at[idx, "posting_time"]
        df.at[idx, "created_timestamp"] = f"{h_date} {t}"
        
        injected_records.append({
            "journal_id": df.at[idx, "journal_id"],
            "anomaly_type": "HOLIDAY_POSTING",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": f"Posting date changed to statutory holiday: {h_date}"
        })
    logger.info(f"Injected {len(holiday_idx):,} Holiday Posting anomalies.")

    # -------------------------------------------------------------------------
    # 3. Near Approval Threshold Exceptions (₹450,000 to ₹499,999)
    # -------------------------------------------------------------------------
    threshold_idx = get_slot_indices(threshold_target)
    for idx in threshold_idx:
        # Amount structured just beneath ₹500,000 threshold
        near_amt = round(float(np.random.uniform(450000.00, 499950.00)), 2)
        df.at[idx, "amount"] = near_amt
        if df.at[idx, "entry_type"] == "DEBIT":
            df.at[idx, "debit_amount"] = near_amt
            df.at[idx, "credit_amount"] = 0.00
        else:
            df.at[idx, "debit_amount"] = 0.00
            df.at[idx, "credit_amount"] = near_amt
            
        injected_records.append({
            "journal_id": df.at[idx, "journal_id"],
            "anomaly_type": "NEAR_THRESHOLD",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": f"Amount structured near threshold: ₹{near_amt:,.2f}"
        })
    logger.info(f"Injected {len(threshold_idx):,} Near Threshold anomalies.")

    # -------------------------------------------------------------------------
    # 4. Round-Number Posting Exceptions
    # -------------------------------------------------------------------------
    round_idx = get_slot_indices(round_amount_target)
    round_values = [10000.00, 50000.00, 100000.00, 250000.00, 500000.00, 1000000.00]
    for idx in round_idx:
        r_amt = float(np.random.choice(round_values))
        df.at[idx, "amount"] = r_amt
        if df.at[idx, "entry_type"] == "DEBIT":
            df.at[idx, "debit_amount"] = r_amt
            df.at[idx, "credit_amount"] = 0.00
        else:
            df.at[idx, "debit_amount"] = 0.00
            df.at[idx, "credit_amount"] = r_amt
            
        injected_records.append({
            "journal_id": df.at[idx, "journal_id"],
            "anomaly_type": "ROUND_AMOUNT",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": f"Amount set to round number: ₹{r_amt:,.2f}"
        })
    logger.info(f"Injected {len(round_idx):,} Round Amount anomalies.")

    # -------------------------------------------------------------------------
    # 5. Unusual Posting Time Exceptions (< 06:00 or >= 22:00)
    # -------------------------------------------------------------------------
    time_idx = get_slot_indices(unusual_time_target)
    for idx in time_idx:
        # Off-hours: 22:00 to 05:59
        is_night = (np.random.rand() > 0.5)
        if is_night:
            hour = np.random.choice([22, 23])
        else:
            hour = np.random.choice([0, 1, 2, 3, 4, 5])
        minute = np.random.randint(0, 60)
        sec = np.random.randint(0, 60)
        u_time = f"{hour:02d}:{minute:02d}:{sec:02d}"
        
        df.at[idx, "posting_time"] = u_time
        d = df.at[idx, "posting_date"]
        df.at[idx, "created_timestamp"] = f"{d} {u_time}"
        
        injected_records.append({
            "journal_id": df.at[idx, "journal_id"],
            "anomaly_type": "UNUSUAL_TIME",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": f"Posting time set to off-hours: {u_time}"
        })
    logger.info(f"Injected {len(time_idx):,} Unusual Posting Time anomalies.")

    # -------------------------------------------------------------------------
    # 6. Duplicate Entry Exceptions
    # -------------------------------------------------------------------------
    # Duplicate pairs: take duplicate_target // 2 source rows and clone into target rows
    dup_pairs = duplicate_target // 2
    src_indices = get_slot_indices(dup_pairs)
    tgt_indices = get_slot_indices(dup_pairs)
    
    for src_i, tgt_i in zip(src_indices, tgt_indices):
        # Clone key attributes from src to tgt while preserving tgt's unique journal_id
        df.at[tgt_i, "posting_date"] = df.at[src_i, "posting_date"]
        df.at[tgt_i, "user_id"] = df.at[src_i, "user_id"]
        df.at[tgt_i, "department_id"] = df.at[src_i, "department_id"]
        df.at[tgt_i, "account_code"] = df.at[src_i, "account_code"]
        df.at[tgt_i, "account_name"] = df.at[src_i, "account_name"]
        df.at[tgt_i, "amount"] = df.at[src_i, "amount"]
        df.at[tgt_i, "entry_type"] = df.at[src_i, "entry_type"]
        df.at[tgt_i, "debit_amount"] = df.at[src_i, "debit_amount"]
        df.at[tgt_i, "credit_amount"] = df.at[src_i, "credit_amount"]
        df.at[tgt_i, "description"] = df.at[src_i, "description"]
        df.at[tgt_i, "vendor_id"] = df.at[src_i, "vendor_id"]
        df.at[tgt_i, "invoice_id"] = df.at[src_i, "invoice_id"]
        
        # Log both records in ground truth
        injected_records.append({
            "journal_id": df.at[src_i, "journal_id"],
            "anomaly_type": "DUPLICATE_ENTRY",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": f"Primary entry duplicated by {df.at[tgt_i, 'journal_id']}"
        })
        injected_records.append({
            "journal_id": df.at[tgt_i, "journal_id"],
            "anomaly_type": "DUPLICATE_ENTRY",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": f"Duplicate clone of {df.at[src_i, 'journal_id']}"
        })
    logger.info(f"Injected {dup_pairs * 2:,} Duplicate Entry anomalies ({dup_pairs:,} pairs).")

    # -------------------------------------------------------------------------
    # 7. Missing / Invalid Approval Control Exceptions
    # -------------------------------------------------------------------------
    missing_appr_idx = get_slot_indices(missing_approval_target)
    for idx in missing_appr_idx:
        # Amount exceeds threshold (>= ₹500,000)
        large_amt = round(float(np.random.uniform(520000.00, 1850000.00)), 2)
        df.at[idx, "amount"] = large_amt
        if df.at[idx, "entry_type"] == "DEBIT":
            df.at[idx, "debit_amount"] = large_amt
            df.at[idx, "credit_amount"] = 0.00
        else:
            df.at[idx, "debit_amount"] = 0.00
            df.at[idx, "credit_amount"] = large_amt
            
        mode = np.random.choice(["MISSING_APPROVER", "STATUS_PENDING", "STATUS_REJECTED"], p=[0.45, 0.40, 0.15])
        if mode == "MISSING_APPROVER":
            df.at[idx, "approval_status"] = "APPROVED"
            df.at[idx, "approver_id"] = None
            reason = "Material entry (>= 500k) missing approver ID"
        elif mode == "STATUS_PENDING":
            df.at[idx, "approval_status"] = "PENDING"
            df.at[idx, "approver_id"] = None
            reason = "Material entry posted with PENDING status"
        else:
            df.at[idx, "approval_status"] = "REJECTED"
            reason = "Rejected entry posted directly into General Ledger"
            
        injected_records.append({
            "journal_id": df.at[idx, "journal_id"],
            "anomaly_type": "MISSING_APPROVAL",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": f"{reason} (Amount: ₹{large_amt:,.2f})"
        })
    logger.info(f"Injected {len(missing_appr_idx):,} Missing/Invalid Approval anomalies.")

    # -------------------------------------------------------------------------
    # 8. Multi-Anomaly Compound Exceptions (High Risk Score >= 6)
    # -------------------------------------------------------------------------
    multi_idx = get_slot_indices(multi_anomaly_target)
    for idx in multi_idx:
        # 1. Weekend date
        w_date = np.random.choice(weekend_dates)
        df.at[idx, "posting_date"] = w_date
        
        # 2. Unusual time (02:15 AM)
        u_time = f"{np.random.choice([1, 2, 3, 23]):02d}:{np.random.randint(10, 50):02d}:{np.random.randint(10, 50):02d}"
        df.at[idx, "posting_time"] = u_time
        df.at[idx, "created_timestamp"] = f"{w_date} {u_time}"
        
        # 3. Near threshold amount
        near_amt = round(float(np.random.uniform(480000.00, 499500.00)), 2)
        df.at[idx, "amount"] = near_amt
        if df.at[idx, "entry_type"] == "DEBIT":
            df.at[idx, "debit_amount"] = near_amt
            df.at[idx, "credit_amount"] = 0.00
        else:
            df.at[idx, "debit_amount"] = 0.00
            df.at[idx, "credit_amount"] = near_amt
            
        # 4. Missing approver
        df.at[idx, "approval_status"] = "PENDING"
        df.at[idx, "approver_id"] = None
        
        jid = df.at[idx, "journal_id"]
        injected_records.append({
            "journal_id": jid,
            "anomaly_type": "WEEKEND_POSTING",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": "Compound multi-anomaly: weekend posting"
        })
        injected_records.append({
            "journal_id": jid,
            "anomaly_type": "UNUSUAL_TIME",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": "Compound multi-anomaly: unusual time"
        })
        injected_records.append({
            "journal_id": jid,
            "anomaly_type": "NEAR_THRESHOLD",
            "injected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": "Compound multi-anomaly: near threshold"
        })
    logger.info(f"Injected {len(multi_idx):,} Compound Multi-Anomaly cases.")

    injected_df = pd.DataFrame(injected_records)
    logger.info(f"Total anomaly ground-truth records logged: {len(injected_df):,}")
    
    return df, injected_df
