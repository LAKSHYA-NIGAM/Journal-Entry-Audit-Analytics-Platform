"""
Unit tests for Risk Scoring and Prioritization Engine.
"""
import pandas as pd
from src.analytics.risk_scoring import calculate_risk_scores

def test_risk_score_calculation():
    """Verifies that weights are applied correctly to compute total risk score."""
    sample_data = pd.DataFrame([
        {
            "journal_id": "JE_LOW",
            "weekend_flag": 1,        # 1*1 = 1
            "holiday_flag": 0,
            "threshold_flag": 0,
            "round_amount_flag": 0,
            "unusual_time_flag": 0,
            "duplicate_flag": 0,
            "approval_exception_flag": 0
        },
        {
            "journal_id": "JE_MED",
            "weekend_flag": 1,        # 1*1 = 1
            "holiday_flag": 0,
            "threshold_flag": 1,      # 1*2 = 2 (Total = 3)
            "round_amount_flag": 0,
            "unusual_time_flag": 0,
            "duplicate_flag": 0,
            "approval_exception_flag": 0
        },
        {
            "journal_id": "JE_HIGH",
            "weekend_flag": 1,        # 1*1 = 1
            "holiday_flag": 0,
            "threshold_flag": 1,      # 1*2 = 2
            "round_amount_flag": 0,
            "unusual_time_flag": 1,   # 1*2 = 2
            "duplicate_flag": 0,
            "approval_exception_flag": 1  # 1*3 = 3 (Total = 8)
        },
        {
            "journal_id": "JE_CLEAN",
            "weekend_flag": 0,
            "holiday_flag": 0,
            "threshold_flag": 0,
            "round_amount_flag": 0,
            "unusual_time_flag": 0,
            "duplicate_flag": 0,
            "approval_exception_flag": 0
        }
    ])
    
    res = calculate_risk_scores(sample_data)
    scores = dict(zip(res["journal_id"], res["risk_score"]))
    categories = dict(zip(res["journal_id"], res["risk_category"]))
    
    assert scores["JE_LOW"] == 1
    assert categories["JE_LOW"] == "Low"
    
    assert scores["JE_MED"] == 3
    assert categories["JE_MED"] == "Medium"
    
    assert scores["JE_HIGH"] == 8
    assert categories["JE_HIGH"] == "High"
    
    assert scores["JE_CLEAN"] == 0
    assert categories["JE_CLEAN"] == "None"
