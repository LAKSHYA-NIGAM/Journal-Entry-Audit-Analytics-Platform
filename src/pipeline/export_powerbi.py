"""
Power BI Star-Schema Data Layer Exporter.
Exports optimized dimension and fact tables in CSV, Parquet, and JSON formats
for seamless import into Microsoft Power BI Desktop and cloud analytics.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from src.utils.logging import get_logger
from src.utils.config import BASE_DIR

logger = get_logger("powerbi_exporter")

def build_dim_calendar(start_date: str, end_date: str, holidays_file: Path) -> pd.DataFrame:
    """
    Generates comprehensive enterprise fiscal calendar dimension table.
    """
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    
    holiday_map = {}
    if holidays_file.exists():
        h_df = pd.read_csv(holidays_file)
        holiday_map = dict(zip(h_df["holiday_date"].astype(str), h_df["holiday_name"]))
        
    cal_rows = []
    for d in dates:
        d_str = d.strftime("%Y-%m-%d")
        dow = d.weekday()  # 0=Mon..6=Sun
        is_wknd = 1 if dow in (5, 6) else 0
        is_hol = 1 if d_str in holiday_map else 0
        hol_name = holiday_map.get(d_str, "None")
        
        # Indian fiscal year: April to March
        fy = f"FY{d.year}-{str(d.year+1)[2:]}" if d.month >= 4 else f"FY{d.year-1}-{str(d.year)[2:]}"
        
        cal_rows.append({
            "date_key": int(d.strftime("%Y%m%d")),
            "date": d_str,
            "day_of_month": d.day,
            "day_of_week": dow + 1,
            "day_name": d.strftime("%A"),
            "is_weekend": is_wknd,
            "is_holiday": is_hol,
            "holiday_name": hol_name,
            "month": d.month,
            "month_name": d.strftime("%B"),
            "month_year": d.strftime("%b %Y"),
            "quarter": f"Q{(d.month - 1) // 3 + 1}",
            "fiscal_year": fy
        })
        
    return pd.DataFrame(cal_rows)

def export_powerbi_datasets(
    full_df: pd.DataFrame,
    users_df: pd.DataFrame,
    accounts_df: pd.DataFrame,
    departments_df: pd.DataFrame,
    benford_df: pd.DataFrame,
    export_dir: Optional[Path] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Exports all star-schema dimension and fact tables to CSV and Parquet formats.
    """
    out_dir = export_dir or (BASE_DIR / "data" / "exports")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Exporting Power BI Data Layer tables to {out_dir}...")
    
    start_date = config.get("dataset", {}).get("start_date", "2024-04-01") if config else "2024-04-01"
    end_date = config.get("dataset", {}).get("end_date", "2025-03-31") if config else "2025-03-31"
    holidays_file = BASE_DIR / "config" / "holidays.csv"
    
    exported_files = {}

    def safe_export_parquet(df_to_save: pd.DataFrame, target_path: Path):
        try:
            df_to_save.to_parquet(target_path, index=False)
        except Exception as err:
            logger.debug(f"Parquet export skipped for {target_path.name}: {err}")

    # 1. Dim Departments
    dim_dept_path_csv = out_dir / "dim_departments.csv"
    departments_df.to_csv(dim_dept_path_csv, index=False)
    safe_export_parquet(departments_df, out_dir / "dim_departments.parquet")
    exported_files["dim_departments"] = str(dim_dept_path_csv)

    # 2. Dim Users (enriched with department name)
    dim_users = users_df.merge(departments_df, on="department_id", how="left")
    dim_users_path_csv = out_dir / "dim_users.csv"
    dim_users.to_csv(dim_users_path_csv, index=False)
    safe_export_parquet(dim_users, out_dir / "dim_users.parquet")
    exported_files["dim_users"] = str(dim_users_path_csv)

    # 3. Dim Accounts
    dim_acc_path_csv = out_dir / "dim_accounts.csv"
    accounts_df.to_csv(dim_acc_path_csv, index=False)
    safe_export_parquet(accounts_df, out_dir / "dim_accounts.parquet")
    exported_files["dim_accounts"] = str(dim_acc_path_csv)

    # 4. Dim Calendar
    dim_calendar = build_dim_calendar(start_date, end_date, holidays_file)
    dim_cal_path_csv = out_dir / "dim_calendar.csv"
    dim_calendar.to_csv(dim_cal_path_csv, index=False)
    safe_export_parquet(dim_calendar, out_dir / "dim_calendar.parquet")
    exported_files["dim_calendar"] = str(dim_cal_path_csv)

    # 5. Benford Results
    benford_path_csv = out_dir / "benford_results.csv"
    benford_df.to_csv(benford_path_csv, index=False)
    safe_export_parquet(benford_df, out_dir / "benford_results.parquet")
    exported_files["benford_results"] = str(benford_path_csv)

    # 6. Fact Journal Entries (Base population)
    fact_je_cols = [
        "journal_id", "posting_date", "posting_time", "user_id", "department_id",
        "account_code", "entry_type", "debit_amount", "credit_amount", "amount",
        "description", "currency", "approval_status", "approver_id", "source_system",
        "vendor_id", "invoice_id", "created_timestamp"
    ]
    fact_je = full_df[[c for c in fact_je_cols if c in full_df.columns]]
    fact_je_path_csv = out_dir / "fact_journal_entries.csv"
    fact_je.to_csv(fact_je_path_csv, index=False)
    safe_export_parquet(fact_je, out_dir / "fact_journal_entries.parquet")
    exported_files["fact_journal_entries"] = str(fact_je_path_csv)

    # 7. Fact Audit Exceptions (Exceptions & Risk Scoring Layer)
    fact_exceptions_cols = [
        "journal_id", "posting_date", "posting_time", "user_id", "department_id",
        "account_code", "amount", "weekend_flag", "holiday_flag", "holiday_name",
        "threshold_flag", "distance_from_threshold", "round_amount_flag", "rounding_level",
        "unusual_time_flag", "duplicate_flag", "duplicate_group_id", "duplicate_count",
        "approval_exception_flag", "approval_exception_reason", "exception_count",
        "risk_score", "risk_category"
    ]
    fact_exceptions = full_df[[c for c in fact_exceptions_cols if c in full_df.columns]]
    fact_exc_path_csv = out_dir / "fact_audit_exceptions.csv"
    fact_exceptions.to_csv(fact_exc_path_csv, index=False)
    safe_export_parquet(fact_exceptions, out_dir / "fact_audit_exceptions.parquet")
    exported_files["fact_audit_exceptions"] = str(fact_exc_path_csv)

    # 8. Summary KPIs JSON metadata
    has_exc = full_df["exception_count"] > 0
    kpis = {
        "total_journal_entries": len(full_df),
        "total_population_amount": float(full_df["amount"].sum()),
        "total_exceptions": int(has_exc.sum()),
        "total_exception_amount": float(full_df.loc[has_exc, "amount"].sum()),
        "overall_exception_rate_pct": round((has_exc.sum() / len(full_df) * 100.0), 2),
        "high_risk_exceptions": int((full_df["risk_category"] == "High").sum()),
        "medium_risk_exceptions": int((full_df["risk_category"] == "Medium").sum()),
        "low_risk_exceptions": int((full_df["risk_category"] == "Low").sum()),
        "weekend_exceptions": int((full_df["weekend_flag"] == 1).sum()),
        "holiday_exceptions": int((full_df["holiday_flag"] == 1).sum()),
        "near_threshold_exceptions": int((full_df["threshold_flag"] == 1).sum()),
        "round_amount_exceptions": int((full_df["round_amount_flag"] == 1).sum()),
        "unusual_time_exceptions": int((full_df["unusual_time_flag"] == 1).sum()),
        "duplicate_exceptions": int((full_df["duplicate_flag"] == 1).sum()),
        "approval_exceptions": int((full_df["approval_exception_flag"] == 1).sum()),
    }
    kpi_file = out_dir / "summary_kpis.json"
    with open(kpi_file, "w", encoding="utf-8") as f:
        json.dump(kpis, f, indent=2)
    exported_files["summary_kpis"] = str(kpi_file)

    logger.info(f"Power BI Data Layer export completed successfully. ({len(exported_files)} assets produced)")
    return exported_files
