"""
Weekend & Off-Hours General Ledger Posting Detector
Flags transactions posted on Saturday or Sunday (dayofweek >= 5),
which often correlate with bypassed operational reviews or unauthorized manual adjustments.
"""

import pandas as pd


def detect_weekend_postings(df: pd.DataFrame, date_column: str = 'posting_date') -> pd.DataFrame:
    if df is None or df.empty or date_column not in df.columns:
        return pd.DataFrame(columns=['entry_id', date_column, 'day_name', 'is_weekend'])

    work_df = df.copy()
    dates = pd.to_datetime(work_df[date_column], errors='coerce')
    is_weekend = dates.dt.dayofweek >= 5  # 5 is Saturday, 6 is Sunday

    flagged = work_df[is_weekend].copy()
    flagged['day_name'] = dates[is_weekend].dt.day_name()
    flagged['is_weekend'] = True

    cols = [col for col in ['entry_id', 'account_id', date_column, 'amount', 'day_name', 'is_weekend'] if col in flagged.columns]
    return flagged[cols]
