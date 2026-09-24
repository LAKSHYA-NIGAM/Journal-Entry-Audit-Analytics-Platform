-- ==============================================================================
-- SQL Audit Test 4: Round-Number Posting Exception
-- Objective: Identify unusually clean round transaction amounts (multiples of 10k, 50k, 100k, 500k, 1M).
-- Interpretation: Estimates, manual provisions, or uncalculated arbitrary amounts
-- frequently exhibit round sums rather than precise invoiced amounts.
-- ==============================================================================

SELECT 
    je.journal_id,
    je.posting_date,
    je.user_id,
    je.account_code,
    je.amount,
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
    END AS rounding_level
FROM journal_entries je;
