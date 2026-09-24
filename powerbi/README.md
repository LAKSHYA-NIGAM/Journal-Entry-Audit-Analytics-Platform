# Power BI Data Layer & Dashboard Architecture

This directory contains the data architecture, data dictionary, DAX measure catalog, and dashboard specifications for the **Journal Entry Audit Analytics Platform**.

---

## 1. Exported Data Files

All exported datasets reside in `data/exports/` and are available in both **CSV** and **Parquet** formats for high-speed import into Power BI Desktop:

| File Name | Format | Role | Description |
|---|---|---|---|
| `fact_journal_entries.csv` / `.parquet` | Fact | Core Transaction Population | All 500,000 general ledger transaction records |
| `fact_audit_exceptions.csv` / `.parquet` | Fact | Exception & Risk Results | Detailed exception flags, risk scores, and priority tiers |
| `dim_users.csv` / `.parquet` | Dimension | User Hierarchy | User names, departments, roles, manager mappings, status |
| `dim_accounts.csv` / `.parquet` | Dimension | Chart of Accounts | GL account codes, account descriptions, categories |
| `dim_departments.csv` / `.parquet` | Dimension | Department Reference | Department IDs and formal department names |
| `dim_calendar.csv` / `.parquet` | Dimension | Fiscal Calendar | Day, Month, Quarter, FY, Weekend/Holiday flags |
| `benford_results.csv` / `.parquet` | Fact / Table | Analytical Procedure | Digits 1–9 observed vs expected distributions & Z-stats |
| `summary_kpis.json` | Metadata | High-Level KPIs | Executive summary metrics for reconciliation |

---

## 2. Power BI Data Model (Star Schema)

The data layer is organized in a classic Kimball Star Schema with 1-to-many (`1:*`) relationships and single-direction cross-filtering:

```text
                  +-------------------+
                  |   dim_calendar    |
                  +-------------------+
                            | (1)
                            | 
                            | (*)
+------------------+  (*) +------------------------+ (*)  +--------------------+
|    dim_users     |----->|  fact_audit_exceptions |<-----|    dim_accounts    |
+------------------+ (1)  +------------------------+ (1)  +--------------------+
         ^                            | (*)
         | (1)                        |
         |                            | (1)
+------------------+                  v
| dim_departments  |      +------------------------+
+------------------+      |  fact_journal_entries  |
                          +------------------------+
```

### Relationship Configuration:
1. `dim_calendar[date]` `1` $\rightarrow$ `*` `fact_audit_exceptions[posting_date]`
2. `dim_users[user_id]` `1` $\rightarrow$ `*` `fact_audit_exceptions[user_id]`
3. `dim_accounts[account_code]` `1` $\rightarrow$ `*` `fact_audit_exceptions[account_code]`
4. `dim_departments[department_id]` `1` $\rightarrow$ `*` `dim_users[department_id]`
5. `fact_journal_entries[journal_id]` `1` $\rightarrow$ `1` `fact_audit_exceptions[journal_id]`

---

## 3. How to Connect Power BI to the Data Layer

### Method A: Direct CSV / Parquet Folder Import (Recommended)
1. Open **Power BI Desktop**.
2. Click **Get Data** $\rightarrow$ **Folder** (or **CSV/Parquet**).
3. Select `data/exports/` directory.
4. Transform Data in Power Query:
   - Ensure `date` columns are formatted as `Date`.
   - Ensure `amount`, `debit_amount`, `credit_amount` are formatted as `Decimal Number` or `Fixed Decimal`.
   - Ensure IDs (`journal_id`, `user_id`, `account_code`) are formatted as `Text`.
5. Click **Close & Apply**.
6. Switch to the **Model View** and verify the Star Schema relationships.

### Method B: PostgreSQL Direct Connection
1. Ensure PostgreSQL container is running (`docker compose up -d`).
2. In Power BI Desktop, click **Get Data** $\rightarrow$ **PostgreSQL database**.
3. Server: `localhost:5432` | Database: `journal_audit_db`.
4. Import view `audit_exception_results` and reference tables (`users`, `accounts`, `departments`, `holidays`).

---

## 4. Documentation Index

* **[Data Dictionary](file:///powerbi/data_dictionary.md)**: Field-by-field definitions, types, business rules, and examples.
* **[Dashboard Specification](file:///powerbi/dashboard_specification.md)**: Visual layouts, charts, slicers, and interactive drill-through paths for all 4 dashboard pages.
* **[DAX Measures Catalog](file:///powerbi/dax_measures.md)**: Production-ready DAX measures ready to paste into Power BI.
