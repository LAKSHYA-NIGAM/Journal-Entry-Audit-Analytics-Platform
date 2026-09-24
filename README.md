# Journal Entry Audit Analytics Platform
### *Enterprise Audit & Assurance – Data & Analytics Workflow*

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.2%2B-150458.svg)](https://pandas.pydata.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Ready-F2C811.svg)](https://powerbi.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end, production-grade financial audit analytics system simulating a real-world **Audit & Assurance – Data & Analytics** workflow. The platform performs 100% population testing across **500,000+ General Ledger journal entries**, executes deterministic financial-control exception tests, applies Benford's Law statistical screening, calculates explainable multi-factor risk scores, and outputs a Kimball star-schema data layer ready for Microsoft Power BI.

---

## 1. Executive Summary & Audit Context

### The Core Audit Problem
In statutory and internal audits, auditors are required by professional standards (**ISA 240 / AU-C 240** – *The Auditor's Responsibilities Relating to Fraud in an Audit of Financial Statements*) to test journal entries and other adjustments for signs of management override of controls, unrecorded liabilities, or unusual accounting activity.

Historically, audit teams tested small random samples (e.g., 25–50 entries out of hundreds of thousands). This manual approach introduced massive sampling risk, as high-risk anomalies, weekend postings, duplicate invoices, or amounts structured just beneath authorization thresholds frequently escaped detection.

### The Analytics Solution
This platform implements **automated 100% population testing**. Instead of manual sampling, it automatically ingests the entire transaction population, evaluates 7 core internal-control rules, conducts first-digit Benford distribution testing, and stratifies transactions into prioritized risk tiers (`High`, `Medium`, `Low`) to guide substantive auditor testing.

> **CRITICAL AUDIT NOTICE:**
> This system **identifies financial control exceptions and statistical anomalies for human auditor investigation**. It does **NOT** claim to detect or prove fraud. True fraud requires establishing legal intent (*scienter*), which automated software cannot determine.

---

## 2. End-to-End System Architecture

```text
+---------------------------------------------------------------------------------------------------+
|                                   DATA ENGINEERING & ANALYTICS PIPELINE                           |
+---------------------------------------------------------------------------------------------------+
                                                  |
                    [ 1. Synthetic Data Generator (Vectorized NumPy / Faker) ]
                                                  |
                                                  v
                   [ 2. Controlled Anomaly Injector (Ground Truth Registry) ]
                                                  |
                                                  v
                     [ 3. PostgreSQL / SQLite Relational Database Engine ]
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
                         v                                                 v
             [ 4. SQL Audit Rules Engine ]                      [ 5. Python / Pandas Analytics ]
             - Weekend Posting Exception                        - Benford's Law (1st Digit MAD)
             - Holiday Posting Exception                        - Chi-Square Goodness-of-Fit
             - Near-Threshold (₹450k-500k)                      - Multidimensional Aggregations
             - Round-Number Postings                            - User & Dept Risk Profiling
             - Unusual Posting Times (<6h, >22h)                           |
             - Duplicate Entry Detection                                   |
             - Missing / Invalid Approvals                                 |
                         |                                                 |
                         +------------------------+------------------------+
                                                  |
                                                  v
                             [ 6. Explainable Risk Scoring Engine ]
                             - Weighted Score: 1x(Wknd, Hol, Rnd) + 2x(Thr, Time) + 3x(Dup, Appr)
                             - Prioritization Tiers: High (6+), Medium (3-5), Low (1-2), None (0)
                                                  |
                                                  v
                             [ 7. Automated Data Quality & Validation ]
                             - Referential integrity, non-null, accounting balance (Dr=Cr)
                             - Ground-truth precision, recall & detection rate evaluation
                                                  |
                                                  v
                             [ 8. Power BI Star-Schema Data Layer ]
                             - Fact Journal Entries (500k rows) & Fact Audit Exceptions
                             - Dimension Tables: Users, Accounts, Departments, Calendar
                             - CSV + Parquet Exports + DAX Measures Catalog
                                                  |
                                                  v
                           [ 9. Interactive 4-Page Auditor Dashboard ]
                           Page 1: Audit Executive Summary
                           Page 2: User Risk Profiling & Governance
                           Page 3: Forensic Journal Entry Investigation Grid
                           Page 4: Benford's Law Analytical Testing
```

---

## 3. Directory Structure

```text
journal-entry-audit/
├── README.md                           # Master Project Documentation & Dynamic Results
├── .env.example                        # Template Environment Configuration
├── .env                                # Local Environment Configuration
├── .gitignore                          # Git Exclusions
├── requirements.txt                    # Python Dependencies
├── docker-compose.yml                  # PostgreSQL 16 Service Definition
├── run_pipeline.py                     # Master 11-Step End-to-End Pipeline Orchestrator
│
├── config/
│   ├── config.yaml                     # Centralized Thresholds, Weights & Parameters
│   └── holidays.csv                    # Statutory & Corporate Holiday Master List
│
├── data/
│   ├── raw/                            # Injected Anomalies Ground Truth Registry
│   ├── processed/                      # Intermediary Analytics Files
│   └── exports/                        # Power BI Star-Schema Datasets (CSV & Parquet)
│
├── database/
│   ├── schema.sql                      # PostgreSQL DDL with Constraints & B-Tree Indexes
│   ├── seed_reference_data.sql         # Departments, Accounts, Rules & Holidays Seed Data
│   ├── views/
│   │   ├── audit_exception_results.sql # Unified SQL View with Flags, Score & Risk Category
│   │   └── summary_views.sql           # Department, User & Account Summary Analytical Views
│   └── audit_tests/
│       ├── 01_weekend_posting.sql      # Test 1: Saturday/Sunday Postings
│       ├── 02_holiday_posting.sql      # Test 2: Statutory Holiday Postings
│       ├── 03_near_threshold.sql       # Test 3: Near Approval Threshold (₹450k-₹500k)
│       ├── 04_round_amounts.sql        # Test 4: Round-Number Amounts (Multiples of 10k)
│       ├── 05_unusual_posting_time.sql # Test 5: Off-Hour Postings (<06:00 or >=22:00)
│       ├── 06_duplicate_entries.sql    # Test 6: Duplicate Postings via Window Partition
│       └── 07_approval_control.sql     # Test 7: Missing/Invalid Approvals & Rejections
│
├── src/
│   ├── __init__.py
│   ├── data_generation/
│   │   ├── __init__.py
│   │   ├── generate_users.py           # Enterprise Users & Org Hierarchy Generator
│   │   ├── generate_accounts.py        # General Ledger Chart of Accounts
│   │   ├── generate_journal_entries.py # Vectorized 500k+ Base Journal Entry Generator
│   │   └── inject_anomalies.py         # Controlled Ground-Truth Anomaly Injection Engine
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── benford.py                  # Benford's Law 1st Digit Analysis (MAD & Chi-Square)
│   │   ├── exception_analysis.py       # Multidimensional Audit Aggregations
│   │   └── risk_scoring.py             # Weighted Risk Scoring & Prioritization Stratification
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── load_to_postgres.py         # Fast Batch Database Ingestion Module
│   │   ├── run_audit_tests.py          # 7 Financial Control SQL Audit Rules Runner
│   │   └── export_powerbi.py           # Star-Schema CSV/Parquet Exporter
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py                   # YAML & Environment Configuration Loader
│       ├── database.py                 # PostgreSQL & SQLite Fallback Database Manager
│       ├── logging.py                  # Standardized Timestamped Logging
│       └── validation.py               # Automated Data Quality & Detection Rate Validator
│
├── tests/
│   ├── __init__.py
│   ├── test_audit_rules.py             # Unit Tests for all 7 SQL Audit Rules
│   ├── test_benford.py                 # Unit Tests for Benford Calculations & MAD Thresholds
│   ├── test_risk_scoring.py            # Unit Tests for Risk Weights & Categorization
│   ├── test_data_generation.py         # Unit Tests for Synthetic Data & Injected Registry
│   ├── test_pipeline.py                # End-to-End Pipeline Integration Test
│   └── run_all_tests.py                # Standalone Test Suite Runner (17 Test Cases)
│
├── docs/
│   └── interview_guide.md              # 12 Comprehensive Audit & Technical Interview Q&As
│
└── powerbi/
    ├── README.md                       # Power BI Architecture & Connection Guide
    ├── data_dictionary.md              # Comprehensive Field-by-Field Business Dictionary
    ├── dashboard_specification.md      # 4-Page Layout Wireframes & Visual Specifications
    └── dax_measures.md                 # Production-Ready DAX Measures Catalog
```

---

## 4. Audit Test Rule Catalog

| Rule # | Exception Name | Objective & Business Logic | Audit Flag | Default Weight |
|---|---|---|---|---|
| **Test 1** | **Weekend Posting** | Flags transactions posted on Saturdays or Sundays (`EXTRACT(DOW) IN (0,6)`). Indicates out-of-cycle manual adjustments. | `weekend_flag` | `+1` |
| **Test 2** | **Holiday Posting** | Joins against corporate `holidays` master. Flags transactions posted on statutory non-working days. | `holiday_flag` | `+1` |
| **Test 3** | **Near Approval Threshold** | Identifies transactions in the 90%–100% window of mandatory approval threshold (₹450,000 to ₹499,999.99). Detects potential threshold-splitting. | `threshold_flag` | `+2` |
| **Test 4** | **Round Amount** | Identifies clean round numbers (multiples of ₹10k, ₹50k, ₹100k, ₹500k, ₹1M) using modulo arithmetic. Frequently indicates non-invoiced manual estimates. | `round_amount_flag` | `+1` |
| **Test 5** | **Unusual Posting Time** | Flags postings occurring outside business hours (`< 06:00:00` or `$\ge$ 22:00:00`). Highlights off-hour activity. | `unusual_time_flag` | `+2` |
| **Test 6** | **Duplicate Entries** | Detects repeated entries sharing identical `(user_id, posting_date, account_code, amount, vendor_id, invoice_id)` via SQL window partitions. | `duplicate_flag` | `+3` |
| **Test 7** | **Approval Control Exception** | Flags entries $\ge$ ₹500,000 lacking approved status or missing approver ID, or any entry posted with `REJECTED` status. | `approval_exception_flag` | `+3` |

---

## 5. Explainable Risk Scoring Model

The risk score is a deterministic linear composite of triggered audit flags:

$$\text{Risk Score} = (F_1 \times 1) + (F_2 \times 1) + (F_3 \times 2) + (F_4 \times 1) + (F_5 \times 2) + (F_6 \times 3) + (F_7 \times 3)$$

### Prioritization Stratification
* **High Risk ($\ge 6$)**: Compound anomalies combining material approval deficiencies, duplicates, near-threshold amounts, and off-hour postings. **Requires mandatory substantive testing**.
* **Medium Risk (3–5)**: Moderate risk entries combining multiple secondary exceptions (e.g., weekend + unusual time + round amount).
* **Low Risk (1–2)**: Single isolated exception (e.g., normal business entry posted on a Saturday).
* **None (0)**: Fully compliant baseline transactions.

---

## 6. Benford's Law Analytical Testing

Benford's Law states that in naturally occurring geometric numerical distributions, the probability $P(d)$ of a leading digit $d \in \{1..9\}$ is given by:
$$P(d) = \log_{10}\left(1 + \frac{1}{d}\right)$$

### Conformability Evaluation (Nigrini & Drake First-Digit MAD Thresholds)
* $\text{MAD} < 0.006$: **Close Conformity**
* $0.006 \le \text{MAD} < 0.012$: **Acceptable Conformity**
* $0.012 \le \text{MAD} < 0.015$: **Marginally Acceptable Conformity**
* $\text{MAD} \ge 0.015$: **Non-Conformity (Requires Analytical Review)**

---

## 7. Actual Execution & Validation Results (500,000 Records)

*These results were dynamically generated by executing `python run_pipeline.py --rows 500000 --seed 42` against the database:*

### 1. Executive Population & Exception Metrics
* **Total Transactions Analyzed**: `500,000`
* **Total Population Amount**: `INR 20,741,867,928.86` (~₹2,074.19 Crores)
* **Total Flagged Exceptions**: `8,501` (**1.70%** exception rate)
* **Total Exception Monetary Exposure**: `INR 2,995,625,015.34` (~₹299.56 Crores)
* **High-Risk Prioritization Items ($\ge 6$)**: `500` (`INR 245,013,388.24`)
* **Medium-Risk Items (3–5)**: `2,743`
* **Low-Risk Items (1–2)**: `5,258`
* **Baseline Compliant Items (0)**: `491,499`

### 2. Exceptions by Audit Rule Category
| Exception Rule | Risk Weight | Flagged Count | Population % | Monetary Exposure (INR) |
|---|---|---|---|---|
| **Approval Control Exception** | `3` | **2,343** | 0.47% | ₹2,218,930,000.00 |
| **Weekend Posting** | `1` | **1,819** | 0.36% | ₹291,575,000.00 |
| **Unusual Posting Time** | `2` | **1,700** | 0.34% | ₹286,065,000.00 |
| **Round-Number Amount** | `1` | **1,501** | 0.30% | ₹498,690,000.00 |
| **Near Approval Threshold** | `2` | **1,500** | 0.30% | ₹720,024,000.00 |
| **Duplicate Entry** | `3` | **900** | 0.18% | ₹30,400,900.00 |
| **Holiday Posting** | `1` | **868** | 0.17% | ₹38,099,300.00 |

### 3. Benford's Law First-Digit Distribution
* **Mean Absolute Deviation (MAD)**: `0.00144` (**Close Conformity**)
* **Chi-Square Statistic**: `130.69` ($p < 0.001$)

| Digit | Observed Count | Expected Count | Observed % | Expected % | Difference % | Z-Statistic | Audit Note |
|---|---|---|---|---|---|---|---|
| **1** | 151,631 | 150,515.0 | 30.326% | 30.103% | +0.223% | 3.44 | Expected geometric peak |
| **2** | 88,409 | 88,045.0 | 17.682% | 17.609% | +0.073% | 1.35 | Conforming |
| **3** | 61,774 | 62,470.0 | 12.355% | 12.494% | -0.139% | 2.97 | Conforming |
| **4** | 50,216 | 48,455.0 | **10.043%** | 9.691% | **+0.352%** | **8.42** | **Spike from near-threshold ₹450k-₹499k** |
| **5** | 38,897 | 39,590.0 | 7.779% | 7.918% | -0.139% | 3.63 | Conforming |
| **6** | 32,822 | 33,475.0 | 6.564% | 6.695% | -0.131% | 3.69 | Conforming |
| **7** | 28,262 | 28,995.0 | 5.652% | 5.799% | -0.147% | 4.43 | Conforming |
| **8** | 25,453 | 25,575.0 | 5.091% | 5.115% | -0.024% | 0.78 | Conforming |
| **9** | 22,536 | 22,880.0 | 4.507% | 4.576% | -0.069% | 2.32 | Conforming |

### 4. Ground-Truth Anomaly Detection Evaluation
| Injected Anomaly Category | Injected Count | Detected Count | Missed Count | Recall (Detection Rate) | Audit Rule Flag |
|---|---|---|---|---|---|
| **WEEKEND_POSTING** | 1,700 | 1,700 | 0 | **100.0%** | `weekend_flag` |
| **HOLIDAY_POSTING** | 800 | 800 | 0 | **100.0%** | `holiday_flag` |
| **NEAR_THRESHOLD** | 1,500 | 1,500 | 0 | **100.0%** | `threshold_flag` |
| **ROUND_AMOUNT** | 1,500 | 1,500 | 0 | **100.0%** | `round_amount_flag` |
| **UNUSUAL_TIME** | 1,700 | 1,700 | 0 | **100.0%** | `unusual_time_flag` |
| **DUPLICATE_ENTRY** | 900 | 900 | 0 | **100.0%** | `duplicate_flag` |
| **MISSING_APPROVAL** | 1,400 | 1,400 | 0 | **100.0%** | `approval_exception_flag` |
| **TOTAL INJECTED ANOMALIES** | **9,500** | **9,500** | **0** | **100.0%** | **Overall Precision/Recall** |

---

## 8. Installation & Quickstart

### Prerequisites
* Python 3.10+
* Docker Desktop (Optional, for PostgreSQL)

### Step 1: Clone Repository & Install Dependencies
```bash
git clone https://github.com/your-username/journal-entry-audit.git
cd journal-entry-audit

# Install required Python packages
python -m pip install -r requirements.txt
```

### Step 2: Database Setup (PostgreSQL with Docker)
```bash
# Start PostgreSQL 16 container
docker compose up -d

# Verify container is running
docker compose ps
```
*(Note: If Docker is not running, the system automatically uses its embedded high-performance SQLite fallback database engine).*

### Step 3: Run the Complete End-to-End Pipeline
```bash
python run_pipeline.py --rows 500000 --seed 42
```

### Step 4: Run Automated Unit & Integration Tests
```bash
python tests/run_all_tests.py
```

---

## 9. Power BI Connection Guide

1. Open **Microsoft Power BI Desktop**.
2. Click **Get Data** $\rightarrow$ **Folder** and select the `data/exports/` directory (or connect directly to PostgreSQL on `localhost:5432 / journal_audit_db`).
3. Load the star-schema tables:
   * `fact_journal_entries`
   * `fact_audit_exceptions`
   * `dim_users`
   * `dim_accounts`
   * `dim_departments`
   * `dim_calendar`
   * `benford_results`
4. Copy the DAX measures from [`powerbi/dax_measures.md`](file:///powerbi/dax_measures.md).
5. Build the 4 report pages following [`powerbi/dashboard_specification.md`](file:///powerbi/dashboard_specification.md).

---

## 10. Audit Limitations & Disclaimers

1. **Analytical Indicator Only**: Exceptions flagged by this platform are internal control deviations, not proof of financial fraud or deliberate misstatement.
2. **Benford's Law Applicability**: Benford's Law does not apply to populations with artificial constraints, such as sequential invoice numbers, fixed price lists, or regulated utility fees.
3. **Prioritization Mechanism**: Risk scores are an operational prioritization mechanism to optimize audit sample selection under ISA 240 / ISA 530, not mathematical probabilities of fraud.
4. **Professional Judgment**: Automated testing assists, but never replaces, the auditor's professional skepticism and substantive inquiry.

---

## 11. Author & Portfolio Context
* **Role Simulation**: Audit & Assurance – Data & Analytics Senior Associate / Financial Risk Engineer
* **Technical Stack**: Python 3.12, PostgreSQL 16, Pandas, NumPy, SciPy, SQLAlchemy, Power BI, Docker
* **Documentation**: See [`docs/interview_guide.md`](file:///docs/interview_guide.md) for detailed technical interview responses.
