-- ==============================================================================
-- Summary Analytical Views for Auditor Executive Reporting
-- ==============================================================================

-- 1. Department Risk Summary
CREATE OR REPLACE VIEW view_department_risk_summary AS
SELECT 
    department_id,
    department_name,
    COUNT(*) AS total_journal_entries,
    SUM(amount) AS total_amount,
    SUM(CASE WHEN exception_count > 0 THEN 1 ELSE 0 END) AS total_exceptions,
    SUM(CASE WHEN risk_category = 'High' THEN 1 ELSE 0 END) AS high_risk_exceptions,
    SUM(CASE WHEN risk_category = 'Medium' THEN 1 ELSE 0 END) AS medium_risk_exceptions,
    SUM(CASE WHEN risk_category = 'Low' THEN 1 ELSE 0 END) AS low_risk_exceptions,
    ROUND(CAST(SUM(CASE WHEN exception_count > 0 THEN 1 ELSE 0 END) AS NUMERIC) / COUNT(*) * 100.0, 2) AS exception_rate_pct,
    SUM(CASE WHEN exception_count > 0 THEN amount ELSE 0 END) AS total_exception_amount
FROM audit_exception_results
GROUP BY department_id, department_name;

-- 2. User Risk Summary
CREATE OR REPLACE VIEW view_user_risk_summary AS
SELECT 
    user_id,
    user_name,
    department_name,
    COUNT(*) AS total_entries_posted,
    SUM(amount) AS total_amount_posted,
    SUM(CASE WHEN exception_count > 0 THEN 1 ELSE 0 END) AS total_exceptions,
    SUM(CASE WHEN risk_category = 'High' THEN 1 ELSE 0 END) AS high_risk_count,
    SUM(CASE WHEN risk_category = 'Medium' THEN 1 ELSE 0 END) AS medium_risk_count,
    SUM(CASE WHEN risk_category = 'Low' THEN 1 ELSE 0 END) AS low_risk_count,
    SUM(threshold_flag) AS near_threshold_count,
    SUM(approval_exception_flag) AS approval_exceptions_count,
    SUM(duplicate_flag) AS duplicate_entries_count,
    ROUND(CAST(SUM(CASE WHEN exception_count > 0 THEN 1 ELSE 0 END) AS NUMERIC) / COUNT(*) * 100.0, 2) AS user_exception_rate_pct
FROM audit_exception_results
GROUP BY user_id, user_name, department_name;

-- 3. Account Risk Summary
CREATE OR REPLACE VIEW view_account_risk_summary AS
SELECT 
    account_code,
    account_name,
    account_category,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_account_volume,
    SUM(CASE WHEN exception_count > 0 THEN 1 ELSE 0 END) AS exception_transactions,
    SUM(CASE WHEN risk_category = 'High' THEN 1 ELSE 0 END) AS high_risk_transactions,
    ROUND(CAST(SUM(CASE WHEN exception_count > 0 THEN 1 ELSE 0 END) AS NUMERIC) / COUNT(*) * 100.0, 2) AS account_exception_rate_pct
FROM audit_exception_results
GROUP BY account_code, account_name, account_category;
