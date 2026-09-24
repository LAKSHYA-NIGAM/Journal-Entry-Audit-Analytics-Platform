"""
End-to-End Journal Entry Audit Analytics Pipeline Orchestrator.
Executes the full automated workflow:
Data Generation -> Anomaly Injection -> Database Ingestion -> SQL Audit Testing ->
Python Analytics -> Benford's Law -> Risk Scoring -> Validation -> Power BI Export.
"""
import argparse
import sys
import time
from pathlib import Path
import pandas as pd
from tabulate import tabulate

from src.utils.logging import get_logger
from src.utils.config import load_config, BASE_DIR
from src.utils.database import DatabaseManager
from src.utils.validation import DataValidator
from src.data_generation.generate_users import generate_users, generate_departments
from src.data_generation.generate_accounts import generate_accounts
from src.data_generation.generate_journal_entries import generate_journal_entries
from src.data_generation.inject_anomalies import inject_controlled_anomalies
from src.analytics.benford import run_benford_analysis
from src.analytics.exception_analysis import run_exception_analysis
from src.pipeline.load_to_postgres import load_all_data
from src.pipeline.run_audit_tests import execute_audit_tests
from src.pipeline.export_powerbi import export_powerbi_datasets

logger = get_logger("pipeline_runner")

def print_banner():
    banner = r"""
========================================================================================
             JOURNAL ENTRY AUDIT ANALYTICS PLATFORM (AUDIT & ASSURANCE D&A)
========================================================================================
    """
    print(banner)

def run_pipeline(
    rows: int = 500000,
    seed: int = 42,
    force_sqlite: bool = False,
    export_dir: Path = BASE_DIR / "data" / "exports"
):
    """
    Executes the complete 11-step audit data engineering and analytics pipeline.
    """
    print_banner()
    start_time = time.time()
    
    # -------------------------------------------------------------------------
    # 1. Load Configuration
    # -------------------------------------------------------------------------
    logger.info("Step 1/11: Loading configuration parameters...")
    config = load_config()
    config["dataset"]["rows"] = rows
    config["dataset"]["seed"] = seed
    
    logger.info(f"Target Population: {rows:,} journal entries | Seed: {seed}")
    
    # -------------------------------------------------------------------------
    # 2. Generate Reference Data (Users, Accounts, Departments, Holidays)
    # -------------------------------------------------------------------------
    logger.info("Step 2/11: Generating reference data (users, chart of accounts, departments)...")
    departments_df = generate_departments()
    users_df = generate_users(seed=seed, num_users=60)
    accounts_df = generate_accounts()
    holidays_file = BASE_DIR / "config" / "holidays.csv"
    
    logger.info(f"Generated {len(departments_df)} departments, {len(users_df)} users, {len(accounts_df)} GL accounts.")
    
    # -------------------------------------------------------------------------
    # 3. Generate Baseline Journal Entries (500k+ rows)
    # -------------------------------------------------------------------------
    logger.info(f"Step 3/11: Generating {rows:,} baseline realistic journal entries...")
    gen_start = time.time()
    base_je_df = generate_journal_entries(num_rows=rows, seed=seed, config=config)
    logger.info(f"Data generation completed in {time.time() - gen_start:.2f} seconds.")
    
    # -------------------------------------------------------------------------
    # 4. Inject Controlled Audit Anomalies & Ground-Truth Registry
    # -------------------------------------------------------------------------
    logger.info("Step 4/11: Injecting controlled financial control anomalies and recording ground truth...")
    je_with_anomalies, injected_df = inject_controlled_anomalies(base_je_df, seed=seed, config=config)
    
    # Save raw generated snapshot
    raw_dir = BASE_DIR / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    injected_df.to_csv(raw_dir / "injected_anomalies_ground_truth.csv", index=False)
    
    # -------------------------------------------------------------------------
    # 5. Database Initialization & Data Ingestion
    # -------------------------------------------------------------------------
    logger.info("Step 5/11: Connecting to database and loading relational tables...")
    db = DatabaseManager(force_sqlite=force_sqlite)
    load_all_data(
        db=db,
        users_df=users_df,
        accounts_df=accounts_df,
        departments_df=departments_df,
        holidays_file=holidays_file,
        journal_entries_df=je_with_anomalies,
        injected_df=injected_df,
        chunksize=config.get("database", {}).get("batch_size", 10000)
    )
    
    # -------------------------------------------------------------------------
    # 6. Execute SQL Audit Tests
    # -------------------------------------------------------------------------
    logger.info("Step 6/11: Executing 7 automated financial control audit tests...")
    test_start = time.time()
    tested_df = execute_audit_tests(db=db, df=je_with_anomalies, config=config)
    logger.info(f"Audit testing and risk scoring completed in {time.time() - test_start:.2f} seconds.")
    
    # -------------------------------------------------------------------------
    # 7. Benford's Law Analytical Testing
    # -------------------------------------------------------------------------
    logger.info("Step 7/11: Executing Benford's Law first-digit distribution analysis...")
    benford_res = run_benford_analysis(
        tested_df,
        amount_col="amount",
        population_name="FY2024-25 Positive General Ledger Transactions"
    )
    
    # -------------------------------------------------------------------------
    # 8. Dynamic In-Depth Audit Exception Analytics
    # -------------------------------------------------------------------------
    logger.info("Step 8/11: Computing multidimensional audit analytics and risk profiles...")
    analysis_res = run_exception_analysis(tested_df)
    
    # -------------------------------------------------------------------------
    # 9. Automated Data Quality & Ground-Truth Validation Checks
    # -------------------------------------------------------------------------
    logger.info("Step 9/11: Performing automated validation and detection rate checks...")
    validator = DataValidator(config=config)
    dq_results = validator.validate_journal_entries_df(
        df=tested_df,
        users_df=users_df,
        accounts_df=accounts_df,
        departments_df=departments_df
    )
    
    detection_summary = validator.evaluate_detection_accuracy(
        injected_df=injected_df,
        exceptions_df=tested_df
    )
    
    # -------------------------------------------------------------------------
    # 10. Export Power BI Ready Data Layer
    # -------------------------------------------------------------------------
    logger.info("Step 10/11: Exporting star-schema tables and KPIs to Power BI data layer...")
    exported_files = export_powerbi_datasets(
        full_df=tested_df,
        users_df=users_df,
        accounts_df=accounts_df,
        departments_df=departments_df,
        benford_df=benford_res.digits_df,
        export_dir=export_dir,
        config=config
    )
    
    # -------------------------------------------------------------------------
    # 11. Final Executive Reporting & Metrics Summary
    # -------------------------------------------------------------------------
    total_elapsed = time.time() - start_time
    logger.info(f"Step 11/11: Pipeline executed successfully in {total_elapsed:.2f} seconds!")
    
    print("\n" + "="*85)
    print("                      AUDIT ANALYTICS EXECUTIVE DASHBOARD SUMMARY")
    print("="*85)
    
    kpis = analysis_res["executive_kpis"].iloc[0]
    print(f"Total Transactions Tested      : {int(kpis['total_journal_entries']):,}")
    print(f"Total Population Amount        : INR {kpis['total_population_amount']:,.2f}")
    print(f"Total Flagged Exceptions       : {int(kpis['total_exceptions']):,} ({kpis['overall_exception_rate_pct']}%)")
    print(f"Total Exception Amount         : INR {kpis['total_exception_amount']:,.2f}")
    print(f"High-Risk Prioritization Items : {int(kpis['high_risk_exceptions']):,} (INR {kpis['high_risk_amount']:,.2f})")
    print(f"Medium-Risk Items              : {int(kpis['medium_risk_exceptions']):,}")
    print(f"Low-Risk Items                 : {int(kpis['low_risk_exceptions']):,}")
    
    print("\n" + "-"*85)
    print("                           AUDIT EXCEPTIONS BY RULE CATEGORY")
    print("-"*85)
    print(tabulate(analysis_res["by_type"], headers="keys", tablefmt="github", showindex=False))
    
    print("\n" + "-"*85)
    print("                        BENFORD'S LAW FIRST-DIGIT DISTRIBUTION")
    print("-"*85)
    print(tabulate(benford_res.digits_df, headers="keys", tablefmt="github", showindex=False))
    print(f"Conformity Status: {benford_res.conformity_status} (MAD = {benford_res.mean_absolute_deviation})")
    
    print("\n" + "-"*85)
    print("                 GROUND-TRUTH ANOMALY DETECTION EVALUATION")
    print("-"*85)
    print(f"Total Injected Anomalies       : {detection_summary['total_injected_anomalies']:,}")
    print(f"Total Detected Injected        : {detection_summary['total_detected_injected']:,}")
    print(f"Overall Ground-Truth Recall    : {detection_summary['overall_detection_rate_pct']}%")
    
    det_rows = []
    for k, v in detection_summary["by_anomaly_type"].items():
        det_rows.append({
            "Anomaly Category": k,
            "Injected Count": v["injected_count"],
            "Detected Count": v["detected_count"],
            "Missed Count": v["missed_count"],
            "Recall (%)": f"{v['detection_rate_pct']}%",
            "Audit Flag": v["audit_flag"]
        })
    print(tabulate(det_rows, headers="keys", tablefmt="github"))
    
    print("\n" + "="*85)
    print(f"DATASET READY FOR POWER BI IMPORT: {export_dir.as_posix()}")
    print("="*85 + "\n")
    
    return {
        "status": "SUCCESS",
        "elapsed_seconds": total_elapsed,
        "kpis": kpis.to_dict(),
        "detection_summary": detection_summary,
        "benford": benford_res,
        "exported_files": exported_files
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Journal Entry Audit Analytics Pipeline Orchestrator")
    parser.add_argument("--rows", type=int, default=500000, help="Number of journal entries to generate (default: 500000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--sqlite", action="store_true", help="Force SQLite database engine")
    parser.add_argument("--export-dir", type=str, default=str(BASE_DIR / "data" / "exports"), help="Directory for Power BI exports")
    
    args = parser.parse_args()
    run_pipeline(
        rows=args.rows,
        seed=args.seed,
        force_sqlite=args.sqlite,
        export_dir=Path(args.export_dir)
    )
