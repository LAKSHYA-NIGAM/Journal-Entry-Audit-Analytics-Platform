"""
Unit tests for Benford's Law Analytical Testing Module.
"""
import math
import numpy as np
import pandas as pd
from src.analytics.benford import (
    extract_first_digit,
    evaluate_mad_conformity,
    run_benford_analysis,
    BENFORD_EXPECTED_PROBS
)

def test_first_digit_extraction():
    """Verifies that first leading digits are correctly extracted across orders of magnitude."""
    series = pd.Series([1.50, 245.90, 3000.00, 48500.25, 500000.00, 6789.12, 70.0, 891.0, 99999.0])
    digits = extract_first_digit(series)
    expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(digits) == expected

def test_benford_expected_probabilities_sum_to_one():
    """Verifies that theoretical Benford probabilities sum to 1.0."""
    total_prob = sum(BENFORD_EXPECTED_PROBS.values())
    assert math.isclose(total_prob, 1.0, rel_tol=1e-3)

def test_mad_conformity_thresholds():
    """Verifies standard Nigrini & Drake MAD evaluation thresholds."""
    assert evaluate_mad_conformity(0.004) == "Close Conformity"
    assert evaluate_mad_conformity(0.008) == "Acceptable Conformity"
    assert evaluate_mad_conformity(0.013) == "Marginally Acceptable Conformity"
    assert evaluate_mad_conformity(0.020) == "Non-Conformity (Requires Analytical Review)"

def test_benford_analysis_execution():
    """Verifies full Benford analysis run on a synthetic lognormal distribution."""
    np.random.seed(42)
    synth_amounts = np.random.lognormal(mean=9.0, sigma=1.5, size=5000)
    df = pd.DataFrame({"amount": synth_amounts})
    
    result = run_benford_analysis(df, amount_col="amount")
    
    assert result.population_size == 5000
    assert len(result.digits_df) == 9
    assert result.mean_absolute_deviation < 0.015
    assert "Close Conformity" in result.conformity_status or "Acceptable" in result.conformity_status
    assert result.chi_square_stat > 0
