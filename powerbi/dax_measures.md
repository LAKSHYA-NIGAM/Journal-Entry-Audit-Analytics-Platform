# DAX Measures Catalog for Power BI

Copy and paste these DAX measures directly into your Power BI Desktop model within a dedicated **`_Measures`** table.

---

## 1. Population & Monetary Exposure Measures

```dax
// Total count of all journal entries in the population
Total Journal Entries = 
COUNTROWS('fact_journal_entries')

// Total monetary value of all journal entries
Total Population Amount = 
SUM('fact_journal_entries'[amount])

// Formatted Total Population Amount in Crores (INR)
Total Population Amount (Cr) = 
DIVIDE([Total Population Amount], 10000000, 0)
```

---

## 2. Exception Volume & Rate Measures

```dax
// Total distinct journal entries flagged with at least one exception
Total Exceptions Count = 
CALCULATE(
    COUNTROWS('fact_audit_exceptions'),
    'fact_audit_exceptions'[exception_count] > 0
)

// Overall exception rate percentage
Exception Rate % = 
DIVIDE(
    [Total Exceptions Count],
    [Total Journal Entries],
    0
)

// Total monetary amount associated with flagged exceptions
Total Exception Amount = 
CALCULATE(
    SUM('fact_audit_exceptions'[amount]),
    'fact_audit_exceptions'[exception_count] > 0
)

// Percentage of total GL volume exposed to exceptions
Exception Amount Exposure % = 
DIVIDE(
    [Total Exception Amount],
    [Total Population Amount],
    0
)
```

---

## 3. Prioritization & Risk Tier Measures

```dax
// Count of High-Risk prioritization transactions (Score >= 6)
High Risk Exceptions Count = 
CALCULATE(
    COUNTROWS('fact_audit_exceptions'),
    'fact_audit_exceptions'[risk_category] = "High"
)

// Total monetary value of High-Risk transactions
High Risk Amount = 
CALCULATE(
    SUM('fact_audit_exceptions'[amount]),
    'fact_audit_exceptions'[risk_category] = "High"
)

// Count of Medium-Risk prioritization transactions (Score 3 to 5)
Medium Risk Exceptions Count = 
CALCULATE(
    COUNTROWS('fact_audit_exceptions'),
    'fact_audit_exceptions'[risk_category] = "Medium"
)

// Count of Low-Risk prioritization transactions (Score 1 to 2)
Low Risk Exceptions Count = 
CALCULATE(
    COUNTROWS('fact_audit_exceptions'),
    'fact_audit_exceptions'[risk_category] = "Low"
)

// Average risk score across all flagged exceptions
Average Risk Score = 
CALCULATE(
    AVERAGE('fact_audit_exceptions'[risk_score]),
    'fact_audit_exceptions'[exception_count] > 0
)
```

---

## 4. Rule-Specific Exception Measures

```dax
// Weekend Posting Exceptions
Weekend Exceptions Count = 
SUM('fact_audit_exceptions'[weekend_flag])

// Holiday Posting Exceptions
Holiday Exceptions Count = 
SUM('fact_audit_exceptions'[holiday_flag])

// Near Approval Threshold Exceptions (₹450k–₹500k)
Near Threshold Exceptions Count = 
SUM('fact_audit_exceptions'[threshold_flag])

// Round Amount Posting Exceptions
Round Amount Exceptions Count = 
SUM('fact_audit_exceptions'[round_amount_flag])

// Unusual Posting Time Exceptions (< 06:00 or >= 22:00)
Unusual Time Exceptions Count = 
SUM('fact_audit_exceptions'[unusual_time_flag])

// Duplicate Entry Exceptions
Duplicate Exceptions Count = 
SUM('fact_audit_exceptions'[duplicate_flag])

// Approval Governance Exceptions
Approval Exceptions Count = 
SUM('fact_audit_exceptions'[approval_exception_flag])
```

---

## 5. Dynamic Slicer & Audit Color Formatting

```dax
// Hex color code based on Risk Category for Conditional Formatting
Risk Category Color = 
SWITCH(
    SELECTEDVALUE('fact_audit_exceptions'[risk_category]),
    "High", "#E11D48",    // Rose / Red
    "Medium", "#F59E0B",  // Amber
    "Low", "#3B82F6",     // Blue
    "#10B981"             // Green / Clean
)

// Dynamic Title for User Investigation
Investigation Grid Title = 
VAR SelectedUser = SELECTEDVALUE('dim_users'[user_name], "All Users")
VAR SelectedDept = SELECTEDVALUE('dim_departments'[department_name], "All Departments")
RETURN
"Journal Entry Investigation | Department: " & SelectedDept & " | User: " & SelectedUser
```
