"""
Round Number Transaction Clustering Detector
Flags journal entries with round thousand or hundred amounts that lack natural cents,
a recognized SOX forensic indicator of manual top-side management estimates or fraudulent accruals.
"""

import pandas as pd


def detect_round_number_entries(df: pd.DataFrame, threshold_round: int = 1000) -> pd.DataFrame:
    if df is None or df.empty or 'amount' not in df.columns:
        return pd.DataFrame(columns=['entry_id', 'amount', 'is_round', 'round_magnitude'])

    work_df = df.copy()
    work_df['amount_clean'] = pd.to_numeric(work_df['amount'], errors='coerce').fillna(0).abs()

    # Criteria: divisible cleanly by 100 or 1000 and has zero fractional cents
    is_round = (work_df['amount_clean'] >= threshold_round) & (work_df['amount_clean'] % threshold_round == 0)

    results = work_df[is_round].copy()
    results['is_round'] = True
    results['round_magnitude'] = threshold_round

    cols = [col for col in ['entry_id', 'account_id', 'amount', 'is_round', 'round_magnitude'] if col in results.columns]
    return results[cols]
