"""
Integration tests for the complete End-to-End Audit Pipeline.
"""
from pathlib import Path
from src.utils.config import BASE_DIR
from run_pipeline import run_pipeline

def test_full_pipeline_run(tmp_path: Path):
    """
    Executes an end-to-end integration run of the pipeline on a test sample.
    """
    export_dir = tmp_path / "exports"
    
    result = run_pipeline(
        rows=2000,
        seed=42,
        force_sqlite=True,
        export_dir=export_dir
    )
    
    assert result["status"] == "SUCCESS"
    assert result["kpis"]["total_journal_entries"] == 2000
    assert result["kpis"]["total_exceptions"] > 0
    assert result["detection_summary"]["overall_detection_rate_pct"] > 85.0
    
    # Check exported files exist
    assert (export_dir / "fact_journal_entries.csv").exists()
    assert (export_dir / "fact_audit_exceptions.csv").exists()
    assert (export_dir / "dim_users.csv").exists()
    assert (export_dir / "dim_accounts.csv").exists()
    assert (export_dir / "dim_departments.csv").exists()
    assert (export_dir / "dim_calendar.csv").exists()
    assert (export_dir / "benford_results.csv").exists()
    assert (export_dir / "summary_kpis.json").exists()
