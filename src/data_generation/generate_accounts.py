"""
General Ledger Chart of Accounts Generator.
"""
from typing import Dict, Any, List
import pandas as pd

DEFAULT_ACCOUNTS: List[Dict[str, str]] = [
    {"account_code": "1010", "account_name": "Cash and Cash Equivalents", "account_category": "Assets"},
    {"account_code": "1020", "account_name": "Accounts Receivable - Trade", "account_category": "Assets"},
    {"account_code": "1050", "account_name": "Prepaid Expenses & Advances", "account_category": "Assets"},
    {"account_code": "1510", "account_name": "Property, Plant and Equipment", "account_category": "Assets"},
    {"account_code": "1520", "account_name": "IT Infrastructure & Software", "account_category": "Assets"},
    {"account_code": "2010", "account_name": "Accounts Payable - Vendors", "account_category": "Liabilities"},
    {"account_code": "2020", "account_name": "Accrued Expenses & Provisions", "account_category": "Liabilities"},
    {"account_code": "2030", "account_name": "Statutory Dues Payable (GST/TDS)", "account_category": "Liabilities"},
    {"account_code": "3010", "account_name": "Common Share Capital", "account_category": "Equity"},
    {"account_code": "3020", "account_name": "Retained Earnings", "account_category": "Equity"},
    {"account_code": "4010", "account_name": "Revenue from Core Operations", "account_category": "Revenue"},
    {"account_code": "4020", "account_name": "Consulting & Services Revenue", "account_category": "Revenue"},
    {"account_code": "5010", "account_name": "Cost of Goods Sold (Direct Costs)", "account_category": "COGS"},
    {"account_code": "6010", "account_name": "Salaries and Employee Benefits", "account_category": "Operating Expenses"},
    {"account_code": "6020", "account_name": "Rent, Rates and Taxes", "account_category": "Operating Expenses"},
    {"account_code": "6030", "account_name": "Travel and Conveyance", "account_category": "Operating Expenses"},
    {"account_code": "6040", "account_name": "Legal and Professional Fees", "account_category": "Operating Expenses"},
    {"account_code": "6050", "account_name": "Marketing, Advertising & Branding", "account_category": "Operating Expenses"},
    {"account_code": "6060", "account_name": "Office Supplies and Administration", "account_category": "Operating Expenses"},
    {"account_code": "6070", "account_name": "IT Subscriptions & Cloud Hosting", "account_category": "Operating Expenses"},
    {"account_code": "6080", "account_name": "Utilities (Electricity, Internet)", "account_category": "Operating Expenses"},
    {"account_code": "6090", "account_name": "Depreciation and Amortization", "account_category": "Operating Expenses"},
]

def generate_accounts() -> pd.DataFrame:
    """
    Returns the standard General Ledger Chart of Accounts as a DataFrame.
    """
    return pd.DataFrame(DEFAULT_ACCOUNTS)
