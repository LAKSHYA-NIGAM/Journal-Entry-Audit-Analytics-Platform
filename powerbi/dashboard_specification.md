# Power BI Dashboard Functional & Visual Specification

This specification outlines the visual design, layout, filters, drill-through paths, and visual-to-field mappings for the 4-page **Audit & Assurance Journal Entry Testing Dashboard**.

---

## Global Navigation & Theme

* **Color Palette**:
  * Navy Primary: `#1E293B`
  * Slate Secondary: `#475569`
  * High Risk Accent: `#E11D48` (Rose / Red)
  * Medium Risk Accent: `#F59E0B` (Amber / Orange)
  * Low Risk Accent: `#3B82F6` (Blue)
  * Neutral Clean: `#10B981` (Emerald / Green)
  * Canvas Background: `#F8FAFC` (Off-white / Light Grey)
* **Standard Header**: Includes Title, Population Fiscal Year (`FY2024-25`), Dataset Refresh Timestamp, and Audit Disclaimer:
  > *"Analytical screening tool for auditor review and exception prioritization. Does not establish fraud."*

---

## PAGE 1 — Audit Executive Summary

### 1. Objective
Provides the Audit Partner and Engagement Manager with an instantaneous high-level overview of the total journal entry population, control exceptions volume, monetary exposure, and macro risk distribution.

### 2. Layout Wireframe
```text
+---------------------------------------------------------------------------------------------------+
| HEADER: Journal Entry Testing - Executive Summary | FY2024-25 | Total Population: 500,000 Records |
+---------------------------------------------------------------------------------------------------+
| [KPI 1: Total Entries] [KPI 2: Total Exceptions] [KPI 3: High-Risk Items] [KPI 4: Exception Rate] |
| 500,000                8,501 (1.7%)              500 (INR 24.5 Cr)        1.70%                   |
+---------------------------------------------------------------------------------------------------+
| [SLICERS: Date Range | Department | GL Category | Source System | Risk Category]                  |
+-----------------------------------------------------------------+---------------------------------+
| CHART 1: Exceptions by Rule Type (Horizontal Bar)               | CHART 2: Risk Category Donut    |
| - Approval Exception (2,343)                                    | - Low Risk: 5,258 (61.8%)       |
| - Weekend Posting (1,819)                                       | - Medium Risk: 2,743 (32.3%)    |
| - Unusual Time (1,700)                                          | - High Risk: 500 (5.9%)         |
| - Round Amount (1,501)                                          |                                 |
| - Near Threshold (1,500)                                        |                                 |
| - Duplicate Entry (900)                                         |                                 |
| - Holiday Posting (868)                                         |                                 |
+-----------------------------------------------------------------+---------------------------------+
| CHART 3: Exceptions by Department (Stacked Bar)                 | CHART 4: Monthly Trend Over Time|
| [Corporate Accounting, Finance, Procurement, Operations...]     | [Line Chart: Entries vs Excepts]|
+-----------------------------------------------------------------+---------------------------------+
```

### 3. Visual Components & Field Mappings
1. **KPI Cards (Top Row)**:
   * `[Total Journal Entries]` = `COUNTROWS(fact_journal_entries)`
   * `[Total Population Amount]` = `SUM(fact_journal_entries[amount])`
   * `[Total Exceptions Count]` = `CALCULATE(COUNTROWS(fact_audit_exceptions), fact_audit_exceptions[exception_count] > 0)`
   * `[High Risk Count & Amount]` = `CALCULATE(COUNTROWS(fact_audit_exceptions), fact_audit_exceptions[risk_category] = "High")`
   * `[Exception Rate %]` = `DIVIDE([Total Exceptions Count], [Total Journal Entries])`
2. **Chart 1 (Clustered Bar)**: Exceptions by Audit Rule Type.
   * Y-Axis: Audit Rule Category
   * X-Axis: Exception Count & Impact Amount
3. **Chart 2 (Donut Chart)**: Exceptions by Prioritization Tier (`High`, `Medium`, `Low`).
4. **Chart 3 (Stacked Column)**: Departmental Breakdown with High/Med/Low risk stack.
5. **Chart 4 (Area/Line Chart)**: Monthly exception volume over the 12-month audit period.

---

## PAGE 2 — User Risk Profiling & Control Exposure

### 1. Objective
Identifies disproportionate exception activity across enterprise users, highlighting individuals with repeated near-threshold entries, missing approvals, or off-hour postings for targeted substantive sampling.

### 2. Layout Wireframe
```text
+---------------------------------------------------------------------------------------------------+
| HEADER: User Risk & Governance Profile | Substantive Audit Sampling Assistant                     |
+---------------------------------------------------------------------------------------------------+
| [SLICERS: Department Slicer | Role Slicer | User Search | Risk Score Threshold Slider]            |
+-----------------------------------------------------------------+---------------------------------+
| TABLE 1: Top 15 Users by Risk Exposure                          | CHART 1: User Activity Scatter  |
| [User Name, Role, Dept, Total Entries, Exceptions, High-Risk,   | X: Total Volume Posted (INR)    |
|  Near-Threshold Count, Missing Approvals, Total Risk Score]     | Y: Exception Count              |
|                                                                 | Size: High Risk Count           |
+-----------------------------------------------------------------+---------------------------------+
| CHART 2: User Exception Types Heatmap / Stacked Matrix          | CARD: Selected User Profile     |
| [User vs Weekend / Holiday / Threshold / Round / Time / Dup]   | - Manager, Department, Status   |
+-----------------------------------------------------------------+---------------------------------+
```

### 3. Visual Components & Field Mappings
1. **Top Risky Users Table**:
   * Columns: `dim_users[user_name]`, `dim_users[role]`, `dim_users[department_name]`, `[User Total Entries]`, `[User Exception Count]`, `[User High Risk Count]`, `[User Near Threshold Count]`, `[User Approval Exceptions]`, `[User Total Risk Score]`.
   * Sort: `[User High Risk Count]` Descending.
2. **User Activity Matrix**:
   * Enables auditors to drill down into a specific user's portfolio and review exact transaction distributions.

---

## PAGE 3 — Journal Entry Transaction Investigation

### 1. Objective
Provides a forensic, line-level investigation ledger allowing auditors to inspect flagged entries, review diagnostic reasons, verify supporting documentation, and tag items for audit sample workpapers.

### 2. Layout Wireframe
```text
+---------------------------------------------------------------------------------------------------+
| HEADER: Forensic Journal Entry Investigation Grid | Line-Item Audit Workpaper                     |
+---------------------------------------------------------------------------------------------------+
| [FILTERS: Risk Category (High/Med/Low) | Exception Type | Dept | Account Code | Journal ID Search]|
+---------------------------------------------------------------------------------------------------+
| INVESTIGATION MATRIX (Detailed Grid with Drill-Through)                                           |
| Journal ID  | Date       | Time     | User       | Dept     | Account     | Amount     | Status   |
| JE_00041201 | 2024-08-15 | 02:15:30 | USR_1015   | Finance  | Legal Fees  | 498,500.00 | PENDING  |
| -> Risk Score: 8 (HIGH) | Triggers: Weekend (1), Unusual Time (2), Near Threshold (2), Approval (3)|
+---------------------------------------------------------------------------------------------------+
| DETAILS PANE (Context on Selected Record):                                                        |
| - Vendor ID: VEND_1042                                                                            |
| - Invoice ID: INV-2024-819201                                                                     |
| - Source System: SAP_S4HANA                                                                       |
| - Description: Legal advisory retainer invoice                                                    |
| - Diagnostic Reason: Material transaction missing approver ID; Posted on Holiday (Independence Day)|
+---------------------------------------------------------------------------------------------------+
```

### 3. Visual Components & Field Mappings
* **Main Grid Columns**: `journal_id`, `posting_date`, `posting_time`, `user_name`, `department_name`, `account_code`, `account_name`, `amount`, `approval_status`, `approver_id`, `risk_score`, `risk_category`, `approval_exception_reason`, `rounding_level`.
* **Conditional Formatting**:
  * `risk_score` $\ge 6$: Light Red Background (`#FFE4E6`)
  * `risk_score` 3–5: Light Amber Background (`#FEF3C7`)
  * `risk_score` 1–2: Light Blue Background (`#E0F2FE`)

---

## PAGE 4 — Benford's Law Analytical Testing

### 1. Objective
Visualizes first-digit frequency distribution across the financial population against theoretical Benford distributions, detecting digit anomalies and threshold clustering in accordance with ISA 520 / AU-C 520 Analytical Procedures.

### 2. Layout Wireframe
```text
+---------------------------------------------------------------------------------------------------+
| HEADER: Benford's Law First-Digit Distribution Analysis | Analytical Audit Procedure             |
+---------------------------------------------------------------------------------------------------+
| [KPI CARDS: Population Size | Mean Absolute Deviation (MAD) | Conformity Status | Chi-Square Stat]|
| 500,000                      0.00144                         Close Conformity    130.69 (p < 0.001)|
+---------------------------------------------------------------------------------------------------+
| CHART 1: Observed vs. Expected Benford Distribution (Clustered Column + Expected Trend Line)      |
| X-Axis: Leading Digits (1, 2, 3, 4, 5, 6, 7, 8, 9)                                               |
| Blue Columns = Observed Frequency % | Black Line = Theoretical Benford Probability %              |
+---------------------------------------------------------------------------------------------------+
| TABLE 1: Digit Deviation & Z-Score Metric Table                                                   |
| Digit | Observed Count | Expected Count | Observed % | Expected % | Difference % | Z-Statistic|
| 1     | 151,631        | 150,515        | 30.33%     | 30.10%     | +0.22%       | 3.44       |
| 4     | 50,216         | 48,455         | 10.04%     | 9.69%      | +0.35%       | 8.42 (SPIKE|
+---------------------------------------------------------------------------------------------------+
| AUDIT CALLOUT NOTE:                                                                               |
| "Noticeable positive spike on Digit 4 (Z=8.42) corresponds to controlled clustering of            |
| near-threshold transactions structured in the INR 450,000 - 499,999 range. Overall dataset         |
| exhibits Close Conformity (MAD = 0.00144 < 0.006)."                                                |
+---------------------------------------------------------------------------------------------------+
```

### 3. Visual Components & Field Mappings
1. **Clustered Column + Line Chart**:
   * Shared X-Axis: `benford_results[digit]`
   * Column Values: `benford_results[observed_percentage]`
   * Line Values: `benford_results[expected_percentage]`
2. **Deviation Summary Table**:
   * `digit`, `observed_count`, `expected_count`, `observed_percentage`, `expected_percentage`, `difference_percentage`, `z_statistic`.
