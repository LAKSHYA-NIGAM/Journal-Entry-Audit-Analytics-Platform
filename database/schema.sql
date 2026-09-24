-- ==============================================================================
-- Journal Entry Audit Analytics Platform Database Schema (PostgreSQL)
-- ==============================================================================

DROP TABLE IF EXISTS injected_anomalies CASCADE;
DROP TABLE IF EXISTS audit_exception_results CASCADE;
DROP TABLE IF EXISTS journal_entries CASCADE;
DROP TABLE IF EXISTS approval_rules CASCADE;
DROP TABLE IF EXISTS holidays CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- 1. Departments Reference Table
CREATE TABLE departments (
    department_id VARCHAR(32) PRIMARY KEY,
    department_name VARCHAR(128) NOT NULL
);

-- 2. Users Reference Table
CREATE TABLE users (
    user_id VARCHAR(32) PRIMARY KEY,
    user_name VARCHAR(128) NOT NULL,
    department_id VARCHAR(32) NOT NULL REFERENCES departments(department_id),
    role VARCHAR(64) NOT NULL,
    manager_id VARCHAR(32),
    active_status BOOLEAN NOT NULL DEFAULT TRUE
);

-- 3. General Ledger Chart of Accounts Table
CREATE TABLE accounts (
    account_code VARCHAR(32) PRIMARY KEY,
    account_name VARCHAR(128) NOT NULL,
    account_category VARCHAR(64) NOT NULL
);

-- 4. Corporate & Statutory Holidays Table
CREATE TABLE holidays (
    holiday_date DATE PRIMARY KEY,
    holiday_name VARCHAR(128) NOT NULL
);

-- 5. Approval Rules Table
CREATE TABLE approval_rules (
    rule_id VARCHAR(32) PRIMARY KEY,
    transaction_type VARCHAR(64) NOT NULL,
    threshold_amount NUMERIC(15,2) NOT NULL,
    required_approval_level VARCHAR(64) NOT NULL
);

-- 6. Journal Entries Core Transaction Table
CREATE TABLE journal_entries (
    journal_id VARCHAR(64) PRIMARY KEY,
    posting_date DATE NOT NULL,
    posting_time TIME NOT NULL,
    user_id VARCHAR(32) NOT NULL REFERENCES users(user_id),
    department_id VARCHAR(32) NOT NULL REFERENCES departments(department_id),
    account_code VARCHAR(32) NOT NULL REFERENCES accounts(account_code),
    account_name VARCHAR(128) NOT NULL,
    entry_type VARCHAR(10) NOT NULL CHECK (entry_type IN ('DEBIT', 'CREDIT')),
    debit_amount NUMERIC(15,2) NOT NULL DEFAULT 0.00 CHECK (debit_amount >= 0),
    credit_amount NUMERIC(15,2) NOT NULL DEFAULT 0.00 CHECK (credit_amount >= 0),
    amount NUMERIC(15,2) NOT NULL CHECK (amount >= 0),
    description TEXT NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    approval_status VARCHAR(32) NOT NULL,
    approver_id VARCHAR(32),
    source_system VARCHAR(64) NOT NULL,
    vendor_id VARCHAR(32),
    invoice_id VARCHAR(64),
    created_timestamp TIMESTAMP NOT NULL
);

-- 7. Ground Truth Injected Anomalies (Internal Evaluation Table)
CREATE TABLE injected_anomalies (
    id SERIAL PRIMARY KEY,
    journal_id VARCHAR(64) NOT NULL,
    anomaly_type VARCHAR(64) NOT NULL,
    injected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

-- High-Performance Indexes for 500k+ Transactions Audit Queries
CREATE INDEX idx_je_posting_date ON journal_entries(posting_date);
CREATE INDEX idx_je_posting_time ON journal_entries(posting_time);
CREATE INDEX idx_je_user_id ON journal_entries(user_id);
CREATE INDEX idx_je_department_id ON journal_entries(department_id);
CREATE INDEX idx_je_account_code ON journal_entries(account_code);
CREATE INDEX idx_je_amount ON journal_entries(amount);
CREATE INDEX idx_je_approval_status ON journal_entries(approval_status);
CREATE INDEX idx_je_duplicate_lookup ON journal_entries(user_id, posting_date, account_code, amount, vendor_id, invoice_id);
CREATE INDEX idx_anomalies_journal_id ON injected_anomalies(journal_id);
CREATE INDEX idx_anomalies_type ON injected_anomalies(anomaly_type);
