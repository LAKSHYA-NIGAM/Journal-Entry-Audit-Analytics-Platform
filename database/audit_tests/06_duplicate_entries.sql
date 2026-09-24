-- ==============================================================================
-- SQL Audit Test 6: Duplicate Journal Entry Detection
-- Objective: Detect duplicate or suspiciously repeated entries sharing identical key attributes
-- (user_id, posting_date, account_code, amount, vendor_id, invoice_id).
-- Interpretation: Duplicate records can indicate inadvertent double-posting,
-- reconciliation errors, or duplicate invoice processing.
-- ==============================================================================

WITH duplicate_window AS (
    SELECT 
        journal_id,
        posting_date,
        posting_time,
        user_id,
        department_id,
        account_code,
        amount,
        vendor_id,
        invoice_id,
        COUNT(*) OVER (
            PARTITION BY user_id, posting_date, account_code, amount, vendor_id, invoice_id
        ) AS duplicate_count,
        DENSE_RANK() OVER (
            ORDER BY user_id, posting_date, account_code, amount, vendor_id, invoice_id
        ) AS duplicate_group_id
    FROM journal_entries
)
SELECT 
    journal_id,
    posting_date,
    user_id,
    account_code,
    amount,
    duplicate_count,
    CASE 
        WHEN duplicate_count > 1 THEN duplicate_group_id 
        ELSE NULL 
    END AS duplicate_group_id,
    CASE 
        WHEN duplicate_count > 1 THEN 1 
        ELSE 0 
    END AS duplicate_flag
FROM duplicate_window;
