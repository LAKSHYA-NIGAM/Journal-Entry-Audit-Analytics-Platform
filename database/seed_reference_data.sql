-- ==============================================================================
-- Reference Data Seeding: Departments, Accounts, Approval Rules, Holidays
-- ==============================================================================

-- 1. Departments
INSERT INTO departments (department_id, department_name) VALUES
('DEP_FIN', 'Finance & Treasury'),
('DEP_ACC', 'Corporate Accounting'),
('DEP_IT', 'Information Technology'),
('DEP_OPS', 'Operations & Logistics'),
('DEP_MKT', 'Marketing & Sales'),
('DEP_HR', 'Human Resources & Payroll'),
('DEP_LGL', 'Legal & Compliance'),
('DEP_PROC', 'Procurement & Vendor Management')
ON CONFLICT (department_id) DO NOTHING;

-- 2. General Ledger Chart of Accounts
INSERT INTO accounts (account_code, account_name, account_category) VALUES
('1010', 'Cash and Cash Equivalents', 'Assets'),
('1020', 'Accounts Receivable - Trade', 'Assets'),
('1050', 'Prepaid Expenses & Advances', 'Assets'),
('1510', 'Property, Plant and Equipment', 'Assets'),
('1520', 'IT Infrastructure & Software', 'Assets'),
('2010', 'Accounts Payable - Vendors', 'Liabilities'),
('2020', 'Accrued Expenses & Provisions', 'Liabilities'),
('2030', 'Statutory Dues Payable (GST/TDS)', 'Liabilities'),
('3010', 'Common Share Capital', 'Equity'),
('3020', 'Retained Earnings', 'Equity'),
('4010', 'Revenue from Core Operations', 'Revenue'),
('4020', 'Consulting & Services Revenue', 'Revenue'),
('5010', 'Cost of Goods Sold (Direct Costs)', 'COGS'),
('6010', 'Salaries and Employee Benefits', 'Operating Expenses'),
('6020', 'Rent, Rates and Taxes', 'Operating Expenses'),
('6030', 'Travel and Conveyance', 'Operating Expenses'),
('6040', 'Legal and Professional Fees', 'Operating Expenses'),
('6050', 'Marketing, Advertising & Branding', 'Operating Expenses'),
('6060', 'Office Supplies and Administration', 'Operating Expenses'),
('6070', 'IT Subscriptions & Cloud Hosting', 'Operating Expenses'),
('6080', 'Utilities (Electricity, Internet)', 'Operating Expenses'),
('6090', 'Depreciation and Amortization', 'Operating Expenses')
ON CONFLICT (account_code) DO NOTHING;

-- 3. Approval Rules & Governance Thresholds
INSERT INTO approval_rules (rule_id, transaction_type, threshold_amount, required_approval_level) VALUES
('RULE_STANDARD', 'GENERAL_GL', 500000.00, 'Finance Director'),
('RULE_EXPENSE', 'OPERATING_EXPENSE', 500000.00, 'Department Head & Controller'),
('RULE_CAPEX', 'CAPITAL_EXPENDITURE', 500000.00, 'CFO Approval'),
('RULE_MANUAL', 'MANUAL_JOURNAL', 500000.00, 'Senior Controller')
ON CONFLICT (rule_id) DO NOTHING;

-- 4. Corporate & Statutory Holidays (FY2024-25)
INSERT INTO holidays (holiday_date, holiday_name) VALUES
('2024-04-09', 'Gudi Padwa / Ugadi'),
('2024-04-11', 'Eid-ul-Fitr'),
('2024-04-17', 'Ram Navami'),
('2024-04-21', 'Mahavir Jayanti'),
('2024-05-01', 'Maharashtra Day / Labour Day'),
('2024-05-23', 'Buddha Purnima'),
('2024-06-17', 'Bakrid / Eid al-Adha'),
('2024-07-17', 'Muharram'),
('2024-08-15', 'Independence Day'),
('2024-08-26', 'Janmashtami'),
('2024-09-07', 'Ganesh Chaturthi'),
('2024-09-16', 'Milad-un-Nabi'),
('2024-10-02', 'Mahatma Gandhi Jayanti'),
('2024-10-12', 'Dussehra / Vijayadashami'),
('2024-10-31', 'Diwali / Deepavali'),
('2024-11-01', 'Diwali Balipratipada / New Year'),
('2024-11-15', 'Guru Nanak Jayanti'),
('2024-12-25', 'Christmas Day'),
('2025-01-01', 'New Year''s Day'),
('2025-01-26', 'Republic Day'),
('2025-02-26', 'Maha Shivratri'),
('2025-03-14', 'Holi'),
('2025-03-31', 'Financial Year End Close')
ON CONFLICT (holiday_date) DO NOTHING;
