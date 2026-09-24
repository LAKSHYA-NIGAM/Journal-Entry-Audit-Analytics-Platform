"""
Pandas-based In-Depth Audit Exception Analysis Module.
Calculates dynamic aggregations across departments, users, general ledger accounts,
time periods, and exception categories for auditor reporting and Power BI summaries.
"""
from typing import Dict, Any
import numpy as np
import pandas as pd
from src.utils.logging import get_logger

logger = get_logger("exception_analytics")

def run_exception_analysis(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Computes multidimensional audit metrics and aggregations dynamically from dataset.
    """
    logger.info("Performing multidimensional audit analytics & risk aggregation...")
    
    total_entries = len(df)
    total_amount = float(df["amount"].sum())
    
    has_exceptions = df["exception_count"] > 0
    total_exceptions = int(has_exceptions.sum())
    exception_amount = float(df.loc[has_exceptions, "amount"].sum())
    
    high_risk_mask = df["risk_category"] == "High"
    medium_risk_mask = df["risk_category"] == "Medium"
    low_risk_mask = df["risk_category"] == "Low"
    
    # 1. Executive Summary KPIs
    executive_kpis = pd.DataFrame([{
        "total_journal_entries": total_entries,
        "total_population_amount": total_amount,
        "total_exceptions": total_exceptions,
        "total_exception_amount": exception_amount,
        "overall_exception_rate_pct": round((total_exceptions / total_entries * 100.0) if total_entries > 0 else 0.0, 2),
        "high_risk_exceptions": int(high_risk_mask.sum()),
        "medium_risk_exceptions": int(medium_risk_mask.sum()),
        "low_risk_exceptions": int(low_risk_mask.sum()),
        "high_risk_amount": float(df.loc[high_risk_mask, "amount"].sum())
    }])

    # 2. Exceptions by Type Breakdown
    exception_types = [
        {"exception_type": "Weekend Posting", "flag_col": "weekend_flag", "weight": 1},
        {"exception_type": "Holiday Posting", "flag_col": "holiday_flag", "weight": 1},
        {"exception_type": "Near Threshold", "flag_col": "threshold_flag", "weight": 2},
        {"exception_type": "Round Amount", "flag_col": "round_amount_flag", "weight": 1},
        {"exception_type": "Unusual Posting Time", "flag_col": "unusual_time_flag", "weight": 2},
        {"exception_type": "Duplicate Entry", "flag_col": "duplicate_flag", "weight": 3},
        {"exception_type": "Approval Exception", "flag_col": "approval_exception_flag", "weight": 3},
    ]
    
    type_rows = []
    for item in exception_types:
        col = item["flag_col"]
        if col in df.columns:
            cnt = int((df[col] == 1).sum())
            amt = float(df.loc[df[col] == 1, "amount"].sum())
            pct = round(cnt / total_entries * 100.0, 2)
            type_rows.append({
                "exception_type": item["exception_type"],
                "flag_column": col,
                "risk_weight": item["weight"],
                "exception_count": cnt,
                "exception_percentage": pct,
                "total_impact_amount": amt
            })
    by_type_df = pd.DataFrame(type_rows)

    # 3. Department Risk Breakdown
    dept_summary = df.groupby(["department_id"]).agg(
        total_entries=("journal_id", "count"),
        total_amount=("amount", "sum"),
        total_exceptions=("exception_count", lambda x: int((x > 0).sum())),
        high_risk_count=("risk_category", lambda x: int((x == "High").sum())),
        medium_risk_count=("risk_category", lambda x: int((x == "Medium").sum())),
        low_risk_count=("risk_category", lambda x: int((x == "Low").sum())),
        exception_amount=("amount", lambda x: float(x[df.loc[x.index, "exception_count"] > 0].sum()))
    ).reset_index()
    
    dept_summary["exception_rate_pct"] = round(dept_summary["total_exceptions"] / dept_summary["total_entries"] * 100.0, 2)
    dept_summary = dept_summary.sort_values(by="high_risk_count", ascending=False)

    # 4. User Risk Profiling (Top Risky Users)
    user_summary = df.groupby(["user_id"]).agg(
        total_entries=("journal_id", "count"),
        total_amount=("amount", "sum"),
        total_exceptions=("exception_count", lambda x: int((x > 0).sum())),
        high_risk_count=("risk_category", lambda x: int((x == "High").sum())),
        near_threshold_count=("threshold_flag", "sum"),
        approval_exceptions=("approval_exception_flag", "sum"),
        duplicate_entries=("duplicate_flag", "sum"),
        total_risk_score=("risk_score", "sum")
    ).reset_index()
    
    user_summary["exception_rate_pct"] = round(user_summary["total_exceptions"] / user_summary["total_entries"] * 100.0, 2)
    user_summary = user_summary.sort_values(by=["high_risk_count", "total_risk_score"], ascending=False)

    # 5. General Ledger Account Risk Breakdown
    acc_summary = df.groupby(["account_code", "account_name"]).agg(
        total_transactions=("journal_id", "count"),
        total_account_volume=("amount", "sum"),
        exception_transactions=("exception_count", lambda x: int((x > 0).sum())),
        high_risk_transactions=("risk_category", lambda x: int((x == "High").sum())),
        round_amount_count=("round_amount_flag", "sum")
    ).reset_index()
    
    acc_summary["account_exception_rate_pct"] = round(acc_summary["exception_transactions"] / acc_summary["total_transactions"] * 100.0, 2)
    acc_summary = acc_summary.sort_values(by="high_risk_transactions", ascending=False)

    # 6. Monthly Trend Analysis
    df["posting_month"] = pd.to_datetime(df["posting_date"]).dt.to_period("M").astype(str)
    monthly_trend = df.groupby("posting_month").agg(
        total_entries=("journal_id", "count"),
        total_amount=("amount", "sum"),
        total_exceptions=("exception_count", lambda x: int((x > 0).sum())),
        high_risk_exceptions=("risk_category", lambda x: int((x == "High").sum())),
        medium_risk_exceptions=("risk_category", lambda x: int((x == "Medium").sum())),
        low_risk_exceptions=("risk_category", lambda x: int((x == "Low").sum()))
    ).reset_index()
    monthly_trend["exception_rate_pct"] = round(monthly_trend["total_exceptions"] / monthly_trend["total_entries"] * 100.0, 2)
    monthly_trend = monthly_trend.sort_values("posting_month")

    logger.info("Exception analysis calculations completed successfully.")
    
    return {
        "executive_kpis": executive_kpis,
        "by_type": by_type_df,
        "department_summary": dept_summary,
        "user_summary": user_summary,
        "account_summary": acc_summary,
        "monthly_trend": monthly_trend
    }
