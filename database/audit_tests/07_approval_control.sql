-- ==============================================================================
-- SQL Audit Test 7: Approval Control Exception
-- Objective: Identify transactions that exceed mandatory thresholds without proper approval,
-- have missing approvers, or possess invalid approval statuses.
-- Interpretation: Internal control governance dictates that material transactions require
-- verified multi-tier authorization prior to General Ledger posting.
-- ==============================================================================

WITH rule_context AS (
    SELECT threshold_amount 
    FROM approval_rules 
    WHERE rule_id = 'RULE_STANDARD'
    LIMIT 1
)
SELECT 
    je.journal_id,
    je.posting_date,
    je.user_id,
    je.amount,
    je.approval_status,
    je.approver_id,
    rc.threshold_amount,
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
    END AS approval_exception_reason
FROM journal_entries je
CROSS JOIN rule_context rc;
