"""
Vectorized Realistic Journal Entry Generator.
Generates baseline non-anomalous journal entries adhering to accounting rules,
realistic business hours, weekday schedules, and log-normal financial distributions.
"""
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from src.utils.logging import get_logger
from src.utils.config import BASE_DIR

logger = get_logger("journal_entry_generator")

ACCOUNT_DESCRIPTIONS = {
    "1010": ["Treasury wire settlement", "Operating bank cash balance sweep", "Inter-account sweep transaction"],
    "1020": ["Customer trade receivable clearance", "Invoice collections posting", "Client billing adjustment"],
    "1050": ["Advance payment to supplier", "Prepaid annual insurance premium", "Advance facility maintenance deposit"],
    "1510": ["Factory tooling equipment purchase", "Warehouse material handling asset", "Office furniture capitalization"],
    "1520": ["Enterprise cloud server hardware", "Database enterprise software license", "Network router infrastructure upgrade"],
    "2010": ["Vendor invoice settlement", "Commercial invoice voucher posting", "Supplier materials disbursement"],
    "2020": ["Month-end operating expense accrual", "Audit fee year-end provision", "Quarterly incentive bonus accrual"],
    "2030": ["Monthly GST tax liability remittance", "Withholding TDS statutory payment", "State professional tax settlement"],
    "3010": ["Share capital equity issuance", "Authorized share capital adjustment", "Equity contribution from parent entity"],
    "3020": ["Annual retained earnings rollover", "Intercompany dividend reserve transfer", "Statutory reserve allocation"],
    "4010": ["Commercial product revenue recognition", "Wholesale client shipment invoicing", "Core operating milestone billing"],
    "4020": ["Management consulting retainer billing", "Implementation advisory fee milestone", "Technical support contract revenue"],
    "5010": ["Direct raw materials procurement", "Third-party contract manufacturing", "Inbound freight and logistics cost"],
    "6010": ["Monthly employee salary disbursement", "Corporate payroll health insurance", "Staff provident fund contribution"],
    "6020": ["Corporate office lease rental", "Branch office municipal property tax", "Warehouse lease monthly payment"],
    "6030": ["Executive domestic flight travel", "Client on-site travel reimbursement", "Employee lodging and conveyance expense"],
    "6040": ["Statutory audit professional fee", "Legal advisory retainer invoice", "Tax compliance advisory fee"],
    "6050": ["Digital search ad campaign spend", "Television commercial broadcast fee", "Annual industry summit sponsorship"],
    "6060": ["Office supplies and stationery", "Printer maintenance and toner", "Courier and postal administrative expense"],
    "6070": ["AWS cloud hosting infrastructure", "Salesforce CRM enterprise subscription", "Microsoft 365 cloud licensing"],
    "6080": ["Office electricity utility invoice", "High-speed leased line telecom invoice", "Water and municipal utility charges"],
    "6090": ["Equipment quarterly depreciation", "Software asset monthly amortization", "Building facility depreciation run"]
}

SOURCE_SYSTEMS = ["SAP_S4HANA", "ORACLE_FUSION", "NETSUITE", "MANUAL_EXCEL"]
SOURCE_WEIGHTS = [0.55, 0.28, 0.12, 0.05]

def get_business_weekdays(start_date: str, end_date: str, holidays_file: Path) -> List[str]:
    """
    Returns list of business weekdays (Monday-Friday) strictly excluding holidays.
    """
    all_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    
    # Exclude Saturday (5) and Sunday (6) in python weekday
    weekdays = [d.strftime("%Y-%m-%d") for d in all_dates if d.weekday() < 5]
    
    holiday_set = set()
    if holidays_file.exists():
        holidays_df = pd.read_csv(holidays_file)
        holiday_set = set(holidays_df["holiday_date"].astype(str))
        
    business_days = [d for d in weekdays if d not in holiday_set]
    return business_days

def generate_journal_entries(
    num_rows: int = 500000,
    seed: int = 42,
    config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Vectorized generation of realistic baseline journal entries.
    """
    logger.info(f"Generating {num_rows:,} baseline journal entries (seed={seed})...")
    np.random.seed(seed)
    
    start_date = config.get("dataset", {}).get("start_date", "2024-04-01") if config else "2024-04-01"
    end_date = config.get("dataset", {}).get("end_date", "2025-03-31") if config else "2025-03-31"
    currency = config.get("dataset", {}).get("currency", "INR") if config else "INR"
    
    holidays_file = BASE_DIR / "config" / "holidays.csv"
    business_days = get_business_weekdays(start_date, end_date, holidays_file)
    
    # 1. Unique Journal IDs
    journal_ids = [f"JE_{i+1:08d}" for i in range(num_rows)]
    
    # 2. Posting Dates (Business days)
    posting_date_indices = np.random.randint(0, len(business_days), size=num_rows)
    posting_dates = np.array(business_days)[posting_date_indices]
    
    # 3. Posting Times: Normal business hours (08:30 to 18:30)
    # Total seconds in window = 10 hours * 3600 = 36000 seconds
    base_second = 8 * 3600 + 30 * 60  # 08:30:00 = 30600 seconds
    time_offsets = np.random.randint(0, 10 * 3600, size=num_rows)
    total_seconds = base_second + time_offsets
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    posting_times = [f"{h:02d}:{m:02d}:{s:02d}" for h, m, s in zip(hours, minutes, seconds)]
    
    # 4. User selection & Department mapping
    # Heavy posting by Accounting (DEP_ACC) and Finance (DEP_FIN)
    users_weights = []
    user_id_pool = []
    user_dept_map = {}
    user_mgr_map = {}
    
    from src.data_generation.generate_users import generate_users
    users_df = generate_users(seed=seed)
    
    for _, u in users_df.iterrows():
        uid = u["user_id"]
        did = u["department_id"]
        mgr = u["manager_id"] or "USR_1001"
        user_id_pool.append(uid)
        user_dept_map[uid] = did
        user_mgr_map[uid] = mgr
        
        if did in ["DEP_ACC", "DEP_FIN"]:
            users_weights.append(10.0 if u["active_status"] else 0.5)
        elif did in ["DEP_PROC", "DEP_OPS"]:
            users_weights.append(3.0 if u["active_status"] else 0.2)
        else:
            users_weights.append(1.0 if u["active_status"] else 0.1)
            
    users_weights = np.array(users_weights) / sum(users_weights)
    user_indices = np.random.choice(len(user_id_pool), size=num_rows, p=users_weights)
    selected_users = [user_id_pool[i] for i in user_indices]
    selected_depts = [user_dept_map[uid] for uid in selected_users]
    selected_approvers = [user_mgr_map[uid] for uid in selected_users]
    
    # 5. Account selection
    from src.data_generation.generate_accounts import generate_accounts
    accounts_df = generate_accounts()
    account_codes = accounts_df["account_code"].tolist()
    account_names_dict = dict(zip(accounts_df["account_code"], accounts_df["account_name"]))
    
    # Weighted accounts distribution (operating expenses, receivables, payables most frequent)
    acc_weights = np.array([
        0.08, 0.10, 0.04, 0.02, 0.03,  # Assets
        0.12, 0.06, 0.05,              # Liabilities
        0.01, 0.01,                    # Equity
        0.09, 0.05,                    # Revenue
        0.07,                          # COGS
        0.06, 0.03, 0.04, 0.03, 0.04,  # OpEx 6010-6050
        0.03, 0.02, 0.02, 0.01         # OpEx 6060-6090
    ])
    acc_weights = acc_weights / sum(acc_weights)
    acc_indices = np.random.choice(len(account_codes), size=num_rows, p=acc_weights)
    selected_acc_codes = [account_codes[i] for i in acc_indices]
    selected_acc_names = [account_names_dict[code] for code in selected_acc_codes]
    
    # 6. Amount generation (Log-normal: median ~₹18,000, 95% < ₹250,000, max ~₹430,000)
    # Log-normal distribution parameters mu=9.8, sigma=1.2 ensures natural Benford's Law distribution
    raw_amounts = np.random.lognormal(mean=9.8, sigma=1.2, size=num_rows)
    # Clip bounds to realistic corporate ticket sizes (₹150 to ₹425,000 baseline, avoiding near-threshold ₹450k-500k)
    clipped_amounts = np.clip(raw_amounts, 150.0, 425000.0)
    # Round to 2 decimal places with non-zero cents (e.g. 14238.45)
    amounts = np.round(clipped_amounts + np.random.uniform(0.01, 0.99, size=num_rows), 2)
    
    # 7. Entry Types (Debit vs Credit)
    entry_types = np.random.choice(["DEBIT", "CREDIT"], size=num_rows, p=[0.52, 0.48])
    debit_amounts = np.where(entry_types == "DEBIT", amounts, 0.00)
    credit_amounts = np.where(entry_types == "CREDIT", amounts, 0.00)
    
    # 8. Realistic Descriptions
    descriptions = []
    for code in selected_acc_codes:
        opts = ACCOUNT_DESCRIPTIONS.get(code, ["General ledger standard transaction"])
        descriptions.append(opts[np.random.randint(0, len(opts))])
        
    # 9. Source System
    source_systems = np.random.choice(SOURCE_SYSTEMS, size=num_rows, p=SOURCE_WEIGHTS)
    
    # 10. Vendor & Invoice IDs
    vendor_num = np.random.randint(1001, 1250, size=num_rows)
    vendor_ids = [f"VEND_{v}" for v in vendor_num]
    invoice_num = np.random.randint(100000, 999999, size=num_rows)
    invoice_ids = [f"INV-2024-{inv}" for inv in invoice_num]
    
    # 11. Approval Status (Baseline compliant entries)
    # Below ₹500,000: AUTO_APPROVED (80%) or APPROVED (20%)
    # Above ₹500,000: APPROVED with approver_id
    approval_choices = ["AUTO_APPROVED", "APPROVED"]
    approval_statuses = np.random.choice(approval_choices, size=num_rows, p=[0.82, 0.18])
    
    # 12. Created Timestamps
    created_timestamps = [f"{d} {t}" for d, t in zip(posting_dates, posting_times)]
    
    df = pd.DataFrame({
        "journal_id": journal_ids,
        "posting_date": posting_dates,
        "posting_time": posting_times,
        "user_id": selected_users,
        "department_id": selected_depts,
        "account_code": selected_acc_codes,
        "account_name": selected_acc_names,
        "entry_type": entry_types,
        "debit_amount": debit_amounts,
        "credit_amount": credit_amounts,
        "amount": amounts,
        "description": descriptions,
        "currency": currency,
        "approval_status": approval_statuses,
        "approver_id": selected_approvers,
        "source_system": source_systems,
        "vendor_id": vendor_ids,
        "invoice_id": invoice_ids,
        "created_timestamp": created_timestamps
    })
    
    logger.info(f"Baseline generation complete: {len(df):,} entries generated.")
    return df
