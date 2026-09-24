# Enterprise Data Dictionary

This document provides a comprehensive technical and business dictionary for all tables and fields within the **Journal Entry Audit Analytics Platform**.

---

## 1. `fact_journal_entries` (Core Transaction Population)

| Field | Data Type | Source | Business Meaning & Description | Example Value |
|---|---|---|---|---|
| `journal_id` | `VARCHAR(64)` | System Generated | Unique primary identifier for the general ledger journal line item. | `JE_00000001` |
| `posting_date` | `DATE` | General Ledger | Effective accounting posting date recorded in the GL. | `2024-05-15` |
| `posting_time` | `TIME` | General Ledger | Wall-clock timestamp of when the entry was committed to the ledger. | `14:22:10` |
| `user_id` | `VARCHAR(32)` | Identity / ERP | User ID of the employee or system service that created the entry. | `USR_1012` |
| `department_id` | `VARCHAR(32)` | Organization Hierarchy | Department originating or accountable for the entry. | `DEP_ACC` |
| `account_code` | `VARCHAR(32)` | Chart of Accounts | General ledger account number for debit/credit allocation. | `6060` |
| `account_name` | `VARCHAR(128)` | Chart of Accounts | Standard accounting name corresponding to the GL code. | `Office Supplies and Administration` |
| `entry_type` | `VARCHAR(10)` | Accounting Engine | Categorization of line entry: `DEBIT` or `CREDIT`. | `DEBIT` |
| `debit_amount` | `NUMERIC(15,2)` | Accounting Engine | Non-negative debit transaction amount in base currency. | `15450.00` |
| `credit_amount` | `NUMERIC(15,2)` | Accounting Engine | Non-negative credit transaction amount in base currency. | `0.00` |
| `amount` | `NUMERIC(15,2)` | Accounting Engine | Absolute magnitude of the transaction line item. | `15450.00` |
| `description` | `TEXT` | ERP / User Input | Business narration or description documenting entry purpose. | `Quarterly stationery supplies` |
| `currency` | `VARCHAR(10)` | Multi-Currency Table | ISO currency code of the transaction (Default: `INR`). | `INR` |
| `approval_status` | `VARCHAR(32)` | Workflow Engine | Approval lifecycle state: `APPROVED`, `AUTO_APPROVED`, `PENDING`, `REJECTED`. | `APPROVED` |
| `approver_id` | `VARCHAR(32)` | Workflow Engine | User ID of the managerial authority who authorized the posting. | `USR_1002` |
| `source_system` | `VARCHAR(64)` | Integration Layer | Upstream originating system: `SAP_S4HANA`, `ORACLE_FUSION`, `NETSUITE`, `MANUAL_EXCEL`. | `SAP_S4HANA` |
| `vendor_id` | `VARCHAR(32)` | Vendor Master | Identifier of third-party vendor associated with expenditure. | `VEND_1042` |
| `invoice_id` | `VARCHAR(64)` | AP Invoicing | Upstream invoice reference voucher identifier. | `INV-2024-819201` |
| `created_timestamp` | `TIMESTAMP` | System Audit Log | Exact timestamp of entry creation in ERP audit database. | `2024-05-15 14:22:10` |

---

## 2. `fact_audit_exceptions` (Exceptions & Risk Scoring Layer)

| Field | Data Type | Source | Business Meaning & Description | Example Value |
|---|---|---|---|---|
| `journal_id` | `VARCHAR(64)` | Audit Engine | Foreign key referencing the primary journal entry. | `JE_00001245` |
| `weekend_flag` | `INTEGER (0/1)` | Audit Rule 1 | Flag indicating if posting date fell on Saturday or Sunday. | `1` |
| `holiday_flag` | `INTEGER (0/1)` | Audit Rule 2 | Flag indicating if posting date matched a statutory company holiday. | `1` |
| `holiday_name` | `VARCHAR(128)` | Holidays Ref Table | Name of the recognized corporate holiday if flagged, else `None`. | `Independence Day` |
| `threshold_flag` | `INTEGER (0/1)` | Audit Rule 3 | Flag indicating amount fell in 90%-100% threshold window (₹450k–₹500k). | `1` |
| `distance_from_threshold` | `NUMERIC(15,2)` | Audit Rule 3 | Monetary distance from the mandatory ₹500,000 threshold. | `4500.00` |
| `round_amount_flag` | `INTEGER (0/1)` | Audit Rule 4 | Flag indicating transaction amount is a clean round number (multiple of 10k). | `1` |
| `rounding_level` | `VARCHAR(64)` | Audit Rule 4 | Specific granularity tier of round number. | `Multiple of 100,000` |
| `unusual_time_flag` | `INTEGER (0/1)` | Audit Rule 5 | Flag indicating posting occurred outside business hours (< 06:00 or $\ge$ 22:00). | `1` |
| `duplicate_flag` | `INTEGER (0/1)` | Audit Rule 6 | Flag indicating entry shares key attributes with 1+ other entries. | `1` |
| `duplicate_group_id` | `INTEGER` | Audit Rule 6 | Identifier clustering duplicate transaction sets together. | `482` |
| `duplicate_count` | `INTEGER` | Audit Rule 6 | Total count of occurrences within the duplicate cluster. | `2` |
| `approval_exception_flag` | `INTEGER (0/1)` | Audit Rule 7 | Flag indicating material transaction missing approval or rejected. | `1` |
| `approval_exception_reason` | `VARCHAR(128)` | Audit Rule 7 | Diagnostic explanation of the approval control deficiency. | `Material transaction missing approver ID` |
| `exception_count` | `INTEGER` | Scoring Model | Total count of distinct financial control rules violated (0 to 7). | `3` |
| `risk_score` | `INTEGER` | Scoring Model | Weighted composite risk prioritization score. | `7` |
| `risk_category` | `VARCHAR(16)` | Scoring Model | Audit investigation prioritization tier: `High` (6+), `Medium` (3-5), `Low` (1-2), `None` (0). | `High` |

---

## 3. `dim_users` (Enterprise User Dimension)

| Field | Data Type | Source | Business Meaning & Description | Example Value |
|---|---|---|---|---|
| `user_id` | `VARCHAR(32)` | HR / Active Directory | Unique corporate employee identifier. | `USR_1015` |
| `user_name` | `VARCHAR(128)` | HR Master | Employee full name. | `Sunita Deshmukh` |
| `department_id` | `VARCHAR(32)` | HR Master | Identifier of employee's primary department. | `DEP_ACC` |
| `department_name` | `VARCHAR(128)` | Organization Ref | Formal business unit name. | `Corporate Accounting` |
| `role` | `VARCHAR(64)` | HR Master | Official corporate job title and governance level. | `Senior Accountant` |
| `manager_id` | `VARCHAR(32)` | Org Hierarchy | User ID of direct supervisor/approver. | `USR_1002` |
| `active_status` | `BOOLEAN` | HR Master | Employment active status (`TRUE` = Active, `FALSE` = Inactive). | `TRUE` |

---

## 4. `dim_accounts` (General Ledger Chart of Accounts)

| Field | Data Type | Source | Business Meaning & Description | Example Value |
|---|---|---|---|---|
| `account_code` | `VARCHAR(32)` | Chart of Accounts | Unique general ledger 4-digit numeric code. | `6040` |
| `account_name` | `VARCHAR(128)` | Chart of Accounts | Descriptive GL account title. | `Legal and Professional Fees` |
| `account_category` | `VARCHAR(64)` | Financial Taxonomy | Financial statement bucket: `Assets`, `Liabilities`, `Equity`, `Revenue`, `COGS`, `Operating Expenses`. | `Operating Expenses` |

---

## 5. `dim_calendar` (Fiscal Calendar Dimension)

| Field | Data Type | Source | Business Meaning & Description | Example Value |
|---|---|---|---|---|
| `date_key` | `INTEGER` | Date Dimension | Integer surrogate key in `YYYYMMDD` format. | `20240815` |
| `date` | `DATE` | Date Dimension | Calendar date. | `2024-08-15` |
| `day_of_month` | `INTEGER` | Date Dimension | Day number (1–31). | `15` |
| `day_of_week` | `INTEGER` | Date Dimension | ISO day of week (1 = Monday, 7 = Sunday). | `4` |
| `day_name` | `VARCHAR(16)` | Date Dimension | Name of day (e.g., `Thursday`). | `Thursday` |
| `is_weekend` | `INTEGER (0/1)` | Date Dimension | Binary flag for Saturday or Sunday. | `0` |
| `is_holiday` | `INTEGER (0/1)` | Date Dimension | Binary flag for statutory company holiday. | `1` |
| `holiday_name` | `VARCHAR(128)` | Date Dimension | Official holiday title if applicable. | `Independence Day` |
| `month` | `INTEGER` | Date Dimension | Month number (1–12). | `8` |
| `month_name` | `VARCHAR(16)` | Date Dimension | Month name (e.g., `August`). | `August` |
| `month_year` | `VARCHAR(16)` | Date Dimension | Formatted Month Year string. | `Aug 2024` |
| `quarter` | `VARCHAR(8)` | Date Dimension | Calendar quarter (`Q1`, `Q2`, `Q3`, `Q4`). | `Q3` |
| `fiscal_year` | `VARCHAR(16)` | Date Dimension | Corporate fiscal year string (e.g., `FY2024-25`). | `FY2024-25` |

---

## 6. `benford_results` (Analytical Testing Output)

| Field | Data Type | Source | Business Meaning & Description | Example Value |
|---|---|---|---|---|
| `digit` | `INTEGER` | Benford Model | Leading non-zero first digit analyzed (1 through 9). | `4` |
| `observed_count` | `INTEGER` | Transaction Population | Actual observed count of transactions leading with this digit. | `50216` |
| `expected_count` | `NUMERIC(15,1)` | Benford Model | Statistically expected count: $N \times \log_{10}(1 + 1/d)$. | `48455.0` |
| `observed_percentage` | `NUMERIC(6,3)` | Transaction Population | Empirical frequency percentage. | `10.043` |
| `expected_percentage` | `NUMERIC(6,3)` | Benford Model | Theoretical Benford frequency percentage. | `9.691` |
| `difference_percentage` | `NUMERIC(6,3)` | Benford Model | Signed percentage difference ($P_{obs} - P_{exp}$). | `0.352` |
| `abs_difference_percentage`| `NUMERIC(6,3)` | Benford Model | Absolute percentage deviation ($|P_{obs} - P_{exp}|$). | `0.352` |
| `z_statistic` | `NUMERIC(6,2)` | Statistical Test | Standardized Z-statistic with continuity correction. | `8.42` |
