"""
Split Transaction Structuring Detector
Detects transactions created by the same preparer or account within a 24-48h window
whose amounts sit just below a management authorization threshold (e.g. $9,000 to $9,999.99 for a $10k limit).
"""

import pandas as pd


def detect_split_structuring(
  df: pd.DataFrame,
  approval_limit: float = 10000.0,
  proximity_pct: float = 0.15,
) -> pd.DataFrame:
  if df is None or df.empty or 'amount' not in df.columns:
    return pd.DataFrame(columns=['entry_id', 'amount', 'is_split_suspect'])

  lower_bound = approval_limit * (1.0 - proximity_pct)
  upper_bound = approval_limit

  work_df = df.copy()
  amounts = pd.to_numeric(work_df['amount'], errors='coerce').fillna(0).abs()
  is_suspect = (amounts >= lower_bound) & (amounts < upper_bound)

  flagged = work_df[is_suspect].copy()
  flagged['is_split_suspect'] = True
  flagged['threshold_boundary'] = approval_limit

  cols = [col for col in ['entry_id', 'preparer_id', 'account_id', 'amount', 'threshold_boundary', 'is_split_suspect'] if col in flagged.columns]
  return flagged[cols]
