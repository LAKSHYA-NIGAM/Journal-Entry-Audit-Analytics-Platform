"""
Explainable Risk & Exception Scoring Engine.
Computes deterministic multi-factor risk scores, exception counts,
and maps transactions into Low / Medium / High exception prioritization tiers.
"""
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from src.utils.logging import get_logger

logger = get_logger("risk_scoring")

DEFAULT_WEIGHTS = {
    "weekend": 1,
    "holiday": 1,
    "threshold": 2,
    "round_amount": 1,
    "unusual_time": 2,
    "duplicate": 3,
    "approval": 3
}

def calculate_risk_scores(
    df: pd.DataFrame,
    config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Computes total exception counts, explainable weighted risk score,
    and assigns prioritization risk categories (Low / Medium / High).
    """
    logger.info("Computing explainable multi-factor risk scores and prioritization tiers...")
    df = df.copy()
    
    weights = config.get("risk_weights", DEFAULT_WEIGHTS) if config else DEFAULT_WEIGHTS
    
    w_weekend = weights.get("weekend", 1)
    w_holiday = weights.get("holiday", 1)
    w_threshold = weights.get("threshold", 2)
    w_round = weights.get("round_amount", 1)
    w_time = weights.get("unusual_time", 2)
    w_duplicate = weights.get("duplicate", 3)
    w_approval = weights.get("approval", 3)
    
    # Fill missing flag columns with 0 if needed
    flag_cols = [
        "weekend_flag", "holiday_flag", "threshold_flag",
        "round_amount_flag", "unusual_time_flag", "duplicate_flag", "approval_exception_flag"
    ]
    for col in flag_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = df[col].fillna(0).astype(int)
            
    # Vectorized exception count calculation
    df["exception_count"] = (
        df["weekend_flag"] +
        df["holiday_flag"] +
        df["threshold_flag"] +
        df["round_amount_flag"] +
        df["unusual_time_flag"] +
        df["duplicate_flag"] +
        df["approval_exception_flag"]
    )
    
    # Vectorized explainable risk score calculation
    df["risk_score"] = (
        df["weekend_flag"] * w_weekend +
        df["holiday_flag"] * w_holiday +
        df["threshold_flag"] * w_threshold +
        df["round_amount_flag"] * w_round +
        df["unusual_time_flag"] * w_time +
        df["duplicate_flag"] * w_duplicate +
        df["approval_exception_flag"] * w_approval
    )
    
    # Prioritization Risk Category
    # 0 = None (Baseline clean)
    # 1 - 2 = Low Priority
    # 3 - 5 = Medium Priority
    # 6+ = High Priority Investigation
    conditions = [
        df["risk_score"] >= 6,
        (df["risk_score"] >= 3) & (df["risk_score"] < 6),
        (df["risk_score"] >= 1) & (df["risk_score"] < 3),
        df["risk_score"] == 0
    ]
    choices = ["High", "Medium", "Low", "None"]
    
    df["risk_category"] = np.select(conditions, choices, default="None")
    
    # High-level breakdown logging
    summary_counts = df["risk_category"].value_counts().to_dict()
    logger.info(
        f"Risk Scoring Complete: High={summary_counts.get('High', 0):,}, "
        f"Medium={summary_counts.get('Medium', 0):,}, "
        f"Low={summary_counts.get('Low', 0):,}, "
        f"None={summary_counts.get('None', 0):,}"
    )
    
    return df
