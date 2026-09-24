-- ==============================================================================
-- SQL Audit Test 2: Holiday Posting Exception
-- Objective: Identify journal entries posted on official statutory/company holidays.
-- Interpretation: Postings on recognized business holidays require substantiation
-- to confirm authorization and emergency processing protocols.
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
        WHEN h.holiday_date IS NOT NULL THEN 1 
        ELSE 0 
    END AS holiday_flag,
    COALESCE(h.holiday_name, 'None') AS holiday_name
FROM journal_entries je
LEFT JOIN holidays h ON je.posting_date = h.holiday_date;
