-- ==============================================================================
-- SQL Audit Test 5: Unusual Posting Time Exception
-- Objective: Flag transactions posted during off-hours (before 06:00 or after 22:00).
-- Interpretation: Entries posted late at night or early morning may indicate
-- non-standard manual interventions, automated script runs, or emergency override postings.
-- ==============================================================================

SELECT 
    je.journal_id,
    je.posting_date,
    je.posting_time,
    je.user_id,
    je.department_id,
    je.account_code,
    je.amount,
    CASE 
        WHEN EXTRACT(HOUR FROM je.posting_time) < 6 OR EXTRACT(HOUR FROM je.posting_time) >= 22 THEN 1
        ELSE 0 
    END AS unusual_time_flag,
    EXTRACT(HOUR FROM je.posting_time) AS posting_hour
FROM journal_entries je;
