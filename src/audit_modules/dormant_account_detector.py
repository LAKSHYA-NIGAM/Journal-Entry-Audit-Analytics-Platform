"""
Dormant Account Reactivation Detector
Detects accounts with zero posting activity for > 90 days that suddenly receive large entries,
a high-risk sign of unauthorized expense parking or fraudulent transfers.
"""

import pandas as pd


def detect_dormant_account_activity(
  df: pd.DataFrame,
  dormancy_days_threshold: int = 90,
  min_reactivation_amount: float = 1000.0,
) -> pd.DataFrame:
  if df is None or df.empty or 'account_id' not in df.columns or 'posting_date' not in df.columns:
    return pd.DataFrame(columns=['entry_id', 'account_id', 'is_dormant_reactivation'])

  work_df = df.copy()
  work_df['date'] = pd.to_datetime(work_df['posting_date'], errors='coerce')
  work_df = work_df.sort_values(by=['account_id', 'date'])

  # Calculate days since previous transaction in the same account
  work_df['prev_date'] = work_df.groupby('account_id')['date'].shift(1)
  work_df['days_dormant'] = (work_df['date'] - work_df['prev_date']).dt.days

  amounts = pd.to_numeric(work_df['amount'], errors='coerce').fillna(0).abs()

  is_reactivation = (work_df['days_dormant'] >= dormancy_days_threshold) & (amounts >= min_reactivation_amount)

  flagged = work_df[is_reactivation].copy()
  flagged['is_dormant_reactivation'] = True

  cols = [col for col in ['entry_id', 'account_id', 'posting_date', 'amount', 'days_dormant', 'is_dormant_reactivation'] if col in flagged.columns]
  return flagged[cols]
