-- ==============================================================================
-- SQL Audit Test 1: Weekend Posting Exception
-- Objective: Identify journal entries posted on Saturdays or Sundays.
-- Interpretation: Weekend postings may indicate manual out-of-cycle adjustments
-- or off-hour entries requiring verification of business justification.
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
        WHEN EXTRACT(DOW FROM je.posting_date) IN (0, 6) THEN 1 
        ELSE 0 
    END AS weekend_flag,
    TO_CHAR(je.posting_date, 'Day') AS day_of_week
FROM journal_entries je;
