-- ==============================================================================
-- Combined Audit Exception Results View / Table Definition
-- Combines Core Journal Entries with All 7 Audit Rule Exceptions & Risk Scoring
-- ==============================================================================

CREATE OR REPLACE VIEW audit_exception_results AS
WITH duplicate_calc AS (
    SELECT 
        journal_id,
        COUNT(*) OVER (
            PARTITION BY user_id, posting_date, account_code, amount, vendor_id, invoice_id
        ) AS dup_count,
        DENSE_RANK() OVER (
            ORDER BY user_id, posting_date, account_code, amount, vendor_id, invoice_id
        ) AS dup_grp_id
    FROM journal_entries
),
rule_ref AS (
    SELECT threshold_amount 
    FROM approval_rules 
    WHERE rule_id = 'RULE_STANDARD'
    LIMIT 1
)
SELECT 
    je.journal_id,
    je.posting_date,
    je.posting_time,
    je.user_id,
    u.user_name,
    je.department_id,
    d.department_name,
    je.account_code,
    je.account_name,
    a.account_category,
    je.entry_type,
    je.debit_amount,
    je.credit_amount,
    je.amount,
    je.description,
    je.currency,
    je.approval_status,
    je.approver_id,
    je.source_system,
    je.vendor_id,
    je.invoice_id,
    je.created_timestamp,

    -- Audit Flag 1: Weekend Posting
    CASE 
        WHEN EXTRACT(DOW FROM je.posting_date) IN (0, 6) THEN 1 
        ELSE 0 
    END AS weekend_flag,

    -- Audit Flag 2: Holiday Posting
    CASE 
        WHEN h.holiday_date IS NOT NULL THEN 1 
        ELSE 0 
    END AS holiday_flag,
    COALESCE(h.holiday_name, 'None') AS holiday_name,

    -- Audit Flag 3: Near Threshold (90% - 100% of ₹500,000)
    CASE 
        WHEN je.amount >= (rc.threshold_amount * 0.90) AND je.amount < rc.threshold_amount THEN 1
        ELSE 0 
    END AS threshold_flag,
    (rc.threshold_amount - je.amount) AS distance_from_threshold,

    -- Audit Flag 4: Round Amount
    CASE 
        WHEN je.amount >= 10000.00 AND (je.amount % 10000.00 = 0) THEN 1
        ELSE 0
    END AS round_amount_flag,
    CASE 
        WHEN je.amount >= 1000000.00 AND (je.amount % 1000000.00 = 0) THEN 'Multiple of 1,000,000'
        WHEN je.amount >= 500000.00 AND (je.amount % 500000.00 = 0) THEN 'Multiple of 500,000'
        WHEN je.amount >= 250000.00 AND (je.amount % 250000.00 = 0) THEN 'Multiple of 250,000'
        WHEN je.amount >= 100000.00 AND (je.amount % 100000.00 = 0) THEN 'Multiple of 100,000'
        WHEN je.amount >= 50000.00 AND (je.amount % 50000.00 = 0) THEN 'Multiple of 50,000'
        WHEN je.amount >= 10000.00 AND (je.amount % 10000.00 = 0) THEN 'Multiple of 10,000'
        ELSE 'Not Round'
    END AS rounding_level,

    -- Audit Flag 5: Unusual Posting Time (< 06:00 or >= 22:00)
    CASE 
        WHEN EXTRACT(HOUR FROM je.posting_time) < 6 OR EXTRACT(HOUR FROM je.posting_time) >= 22 THEN 1
        ELSE 0 
    END AS unusual_time_flag,

    -- Audit Flag 6: Duplicate Entry
    CASE 
        WHEN dc.dup_count > 1 THEN 1 
        ELSE 0 
    END AS duplicate_flag,
    CASE 
        WHEN dc.dup_count > 1 THEN dc.dup_grp_id 
        ELSE NULL 
    END AS duplicate_group_id,
    dc.dup_count AS duplicate_count,

    -- Audit Flag 7: Approval Control Exception
    CASE 
        WHEN je.amount >= rc.threshold_amount AND (je.approval_status != 'APPROVED' OR je.approver_id IS NULL) THEN 1
        WHEN je.approval_status = 'REJECTED' THEN 1
        WHEN je.approval_status NOT IN ('APPROVED', 'AUTO_APPROVED', 'SYSTEM') AND je.amount >= 100000.00 THEN 1
        ELSE 0 
    END AS approval_exception_flag,
    CASE 
        WHEN je.amount >= rc.threshold_amount AND je.approver_id IS NULL THEN 'Material transaction missing approver ID'
        WHEN je.amount >= rc.threshold_amount AND je.approval_status != 'APPROVED' THEN 'Material transaction not approved'
        WHEN je.approval_status = 'REJECTED' THEN 'Rejected transaction posted to GL'
        WHEN je.approval_status NOT IN ('APPROVED', 'AUTO_APPROVED', 'SYSTEM') AND je.amount >= 100000.00 THEN 'Non-standard approval status on large entry'
        ELSE 'None'
    END AS approval_exception_reason,

    -- Exception Count
    (
        (CASE WHEN EXTRACT(DOW FROM je.posting_date) IN (0, 6) THEN 1 ELSE 0 END) +
        (CASE WHEN h.holiday_date IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN je.amount >= (rc.threshold_amount * 0.90) AND je.amount < rc.threshold_amount THEN 1 ELSE 0 END) +
        (CASE WHEN je.amount >= 10000.00 AND (je.amount % 10000.00 = 0) THEN 1 ELSE 0 END) +
        (CASE WHEN EXTRACT(HOUR FROM je.posting_time) < 6 OR EXTRACT(HOUR FROM je.posting_time) >= 22 THEN 1 ELSE 0 END) +
        (CASE WHEN dc.dup_count > 1 THEN 1 ELSE 0 END) +
        (CASE 
            WHEN je.amount >= rc.threshold_amount AND (je.approval_status != 'APPROVED' OR je.approver_id IS NULL) THEN 1
            WHEN je.approval_status = 'REJECTED' THEN 1
            WHEN je.approval_status NOT IN ('APPROVED', 'AUTO_APPROVED', 'SYSTEM') AND je.amount >= 100000.00 THEN 1
            ELSE 0 
        END)
    ) AS exception_count,

    -- Explainable Risk Score
    (
        (CASE WHEN EXTRACT(DOW FROM je.posting_date) IN (0, 6) THEN 1 ELSE 0 END) * 1 +
        (CASE WHEN h.holiday_date IS NOT NULL THEN 1 ELSE 0 END) * 1 +
        (CASE WHEN je.amount >= (rc.threshold_amount * 0.90) AND je.amount < rc.threshold_amount THEN 1 ELSE 0 END) * 2 +
        (CASE WHEN je.amount >= 10000.00 AND (je.amount % 10000.00 = 0) THEN 1 ELSE 0 END) * 1 +
        (CASE WHEN EXTRACT(HOUR FROM je.posting_time) < 6 OR EXTRACT(HOUR FROM je.posting_time) >= 22 THEN 1 ELSE 0 END) * 2 +
        (CASE WHEN dc.dup_count > 1 THEN 1 ELSE 0 END) * 3 +
        (CASE 
            WHEN je.amount >= rc.threshold_amount AND (je.approval_status != 'APPROVED' OR je.approver_id IS NULL) THEN 1
            WHEN je.approval_status = 'REJECTED' THEN 1
            WHEN je.approval_status NOT IN ('APPROVED', 'AUTO_APPROVED', 'SYSTEM') AND je.amount >= 100000.00 THEN 1
            ELSE 0 
        END) * 3
    ) AS risk_score,

    -- Prioritization Risk Category
    CASE 
        WHEN (
            (CASE WHEN EXTRACT(DOW FROM je.posting_date) IN (0, 6) THEN 1 ELSE 0 END) * 1 +
            (CASE WHEN h.holiday_date IS NOT NULL THEN 1 ELSE 0 END) * 1 +
            (CASE WHEN je.amount >= (rc.threshold_amount * 0.90) AND je.amount < rc.threshold_amount THEN 1 ELSE 0 END) * 2 +
            (CASE WHEN je.amount >= 10000.00 AND (je.amount % 10000.00 = 0) THEN 1 ELSE 0 END) * 1 +
            (CASE WHEN EXTRACT(HOUR FROM je.posting_time) < 6 OR EXTRACT(HOUR FROM je.posting_time) >= 22 THEN 1 ELSE 0 END) * 2 +
            (CASE WHEN dc.dup_count > 1 THEN 1 ELSE 0 END) * 3 +
            (CASE 
                WHEN je.amount >= rc.threshold_amount AND (je.approval_status != 'APPROVED' OR je.approver_id IS NULL) THEN 1
                WHEN je.approval_status = 'REJECTED' THEN 1
                WHEN je.approval_status NOT IN ('APPROVED', 'AUTO_APPROVED', 'SYSTEM') AND je.amount >= 100000.00 THEN 1
                ELSE 0 
            END) * 3
        ) >= 6 THEN 'High'
        WHEN (
            (CASE WHEN EXTRACT(DOW FROM je.posting_date) IN (0, 6) THEN 1 ELSE 0 END) * 1 +
            (CASE WHEN h.holiday_date IS NOT NULL THEN 1 ELSE 0 END) * 1 +
            (CASE WHEN je.amount >= (rc.threshold_amount * 0.90) AND je.amount < rc.threshold_amount THEN 1 ELSE 0 END) * 2 +
            (CASE WHEN je.amount >= 10000.00 AND (je.amount % 10000.00 = 0) THEN 1 ELSE 0 END) * 1 +
            (CASE WHEN EXTRACT(HOUR FROM je.posting_time) < 6 OR EXTRACT(HOUR FROM je.posting_time) >= 22 THEN 1 ELSE 0 END) * 2 +
            (CASE WHEN dc.dup_count > 1 THEN 1 ELSE 0 END) * 3 +
            (CASE 
                WHEN je.amount >= rc.threshold_amount AND (je.approval_status != 'APPROVED' OR je.approver_id IS NULL) THEN 1
                WHEN je.approval_status = 'REJECTED' THEN 1
                WHEN je.approval_status NOT IN ('APPROVED', 'AUTO_APPROVED', 'SYSTEM') AND je.amount >= 100000.00 THEN 1
                ELSE 0 
            END) * 3
        ) >= 3 THEN 'Medium'
        WHEN (
            (CASE WHEN EXTRACT(DOW FROM je.posting_date) IN (0, 6) THEN 1 ELSE 0 END) * 1 +
            (CASE WHEN h.holiday_date IS NOT NULL THEN 1 ELSE 0 END) * 1 +
            (CASE WHEN je.amount >= (rc.threshold_amount * 0.90) AND je.amount < rc.threshold_amount THEN 1 ELSE 0 END) * 2 +
            (CASE WHEN je.amount >= 10000.00 AND (je.amount % 10000.00 = 0) THEN 1 ELSE 0 END) * 1 +
            (CASE WHEN EXTRACT(HOUR FROM je.posting_time) < 6 OR EXTRACT(HOUR FROM je.posting_time) >= 22 THEN 1 ELSE 0 END) * 2 +
            (CASE WHEN dc.dup_count > 1 THEN 1 ELSE 0 END) * 3 +
            (CASE 
                WHEN je.amount >= rc.threshold_amount AND (je.approval_status != 'APPROVED' OR je.approver_id IS NULL) THEN 1
                WHEN je.approval_status = 'REJECTED' THEN 1
                WHEN je.approval_status NOT IN ('APPROVED', 'AUTO_APPROVED', 'SYSTEM') AND je.amount >= 100000.00 THEN 1
                ELSE 0 
            END) * 3
        ) >= 1 THEN 'Low'
        ELSE 'None'
    END AS risk_category

FROM journal_entries je
LEFT JOIN users u ON je.user_id = u.user_id
LEFT JOIN departments d ON je.department_id = d.department_id
LEFT JOIN accounts a ON je.account_code = a.account_code
LEFT JOIN holidays h ON je.posting_date = h.holiday_date
CROSS JOIN rule_ref rc;
