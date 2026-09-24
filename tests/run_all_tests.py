"""
Unified Test Runner for Journal Entry Audit Platform.
Executes all unit tests and integration tests cleanly.
"""
import sys
import time
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure project root is in PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_audit_rules import (
    test_weekend_detection,
    test_holiday_detection,
    test_threshold_detection,
    test_round_amount_detection,
    test_unusual_time_detection,
    test_duplicate_detection,
    test_missing_approval_detection,
    base_sample_df
)
from tests.test_benford import (
    test_first_digit_extraction,
    test_benford_expected_probabilities_sum_to_one,
    test_mad_conformity_thresholds,
    test_benford_analysis_execution
)
from tests.test_risk_scoring import test_risk_score_calculation
from tests.test_data_generation import (
    test_generate_users,
    test_generate_accounts,
    test_deterministic_journal_generation,
    test_anomaly_injection_registry
)
from tests.test_pipeline import test_full_pipeline_run

class AuditPlatformTestSuite(unittest.TestCase):
    """Encapsulates all unit and integration test assertions."""
    
    def setUp(self):
        self.sample_df = base_sample_df()

    def test_01_weekend_detection(self):
        test_weekend_detection(self.sample_df)

    def test_02_holiday_detection(self):
        test_holiday_detection(self.sample_df)

    def test_03_threshold_detection(self):
        test_threshold_detection(self.sample_df)

    def test_04_round_amount_detection(self):
        test_round_amount_detection(self.sample_df)

    def test_05_unusual_time_detection(self):
        test_unusual_time_detection(self.sample_df)

    def test_06_duplicate_detection(self):
        test_duplicate_detection(self.sample_df)

    def test_07_missing_approval_detection(self):
        test_missing_approval_detection(self.sample_df)

    def test_08_first_digit_extraction(self):
        test_first_digit_extraction()

    def test_09_benford_probabilities(self):
        test_benford_expected_probabilities_sum_to_one()

    def test_10_mad_thresholds(self):
        test_mad_conformity_thresholds()

    def test_11_benford_analysis(self):
        test_benford_analysis_execution()

    def test_12_risk_scores(self):
        test_risk_score_calculation()

    def test_13_generate_users(self):
        test_generate_users()

    def test_14_generate_accounts(self):
        test_generate_accounts()

    def test_15_deterministic_data(self):
        test_deterministic_journal_generation()

    def test_16_anomaly_injection(self):
        test_anomaly_injection_registry()

    def test_17_full_pipeline_integration(self):
        tmp_dir = PROJECT_ROOT / "data" / "test_exports"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        test_full_pipeline_run(tmp_dir)

if __name__ == "__main__":
    print("=" * 80)
    print("      RUNNING COMPLETE JOURNAL ENTRY AUDIT SUITE (17 TEST CASES)")
    print("=" * 80)
    suite = unittest.TestLoader().loadTestsFromTestCase(AuditPlatformTestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
