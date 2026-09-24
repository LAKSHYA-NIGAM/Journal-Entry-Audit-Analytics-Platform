-- ==============================================================================
-- SQL Audit Test 3: Near Approval Threshold Exception
-- Objective: Detect transactions structured just below approval governance thresholds (90%-100%).
-- Threshold: Default ₹500,000 (Window: >= ₹450,000 and < ₹500,000).
-- Interpretation: Repeated transactions clustered just beneath mandatory approval thresholds
-- warrant review for potential threshold-splitting or circumvention of control tiers.
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
    je.posting_time,
    je.user_id,
    je.department_id,
    je.account_code,
    je.amount,
    rc.threshold_amount,
    (rc.threshold_amount - je.amount) AS distance_from_threshold,
    CASE 
        WHEN je.amount >= (rc.threshold_amount * 0.90) AND je.amount < rc.threshold_amount THEN 1
        ELSE 0 
    END AS threshold_flag
FROM journal_entries je
CROSS JOIN rule_context rc;
