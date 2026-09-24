"""
Enterprise Users and Organization Hierarchy Generator.
"""
from typing import Dict, Any, List
import pandas as pd
from faker import Faker

DEPARTMENT_ROLES = {
    "DEP_FIN": ["Finance Director", "Treasury Manager", "Senior Financial Analyst", "Financial Analyst"],
    "DEP_ACC": ["Corporate Controller", "Assistant Controller", "Senior Accountant", "Staff Accountant", "AP Specialist", "GL Accountant"],
    "DEP_IT": ["IT Director", "ERP Systems Lead", "Database Administrator", "IT Support Specialist"],
    "DEP_OPS": ["Operations Director", "Logistics Manager", "Inventory Controller", "Supply Chain Analyst"],
    "DEP_MKT": ["Marketing VP", "Campaign Manager", "Media Buyer", "Brand Specialist"],
    "DEP_HR": ["HR Director", "Payroll Manager", "Compensation Specialist", "HR Generalist"],
    "DEP_LGL": ["General Counsel", "Compliance Manager", "Legal Counsel"],
    "DEP_PROC": ["Head of Procurement", "Senior Buyer", "Procurement Specialist", "Vendor Relations Officer"]
}

DEPARTMENTS = [
    {"department_id": "DEP_FIN", "department_name": "Finance & Treasury"},
    {"department_id": "DEP_ACC", "department_name": "Corporate Accounting"},
    {"department_id": "DEP_IT", "department_name": "Information Technology"},
    {"department_id": "DEP_OPS", "department_name": "Operations & Logistics"},
    {"department_id": "DEP_MKT", "department_name": "Marketing & Sales"},
    {"department_id": "DEP_HR", "department_name": "Human Resources & Payroll"},
    {"department_id": "DEP_LGL", "department_name": "Legal & Compliance"},
    {"department_id": "DEP_PROC", "department_name": "Procurement & Vendor Management"}
]

def generate_departments() -> pd.DataFrame:
    """Returns department reference DataFrame."""
    return pd.DataFrame(DEPARTMENTS)

def generate_users(seed: int = 42, num_users: int = 60) -> pd.DataFrame:
    """
    Generates deterministic enterprise users with roles, departments, and manager IDs.
    """
    fake = Faker("en_IN")
    Faker.seed(seed)
    
    users: List[Dict[str, Any]] = []
    
    # 1. Executive CFO
    users.append({
        "user_id": "USR_1001",
        "user_name": "Rajesh Subramanian",
        "department_id": "DEP_FIN",
        "role": "Chief Financial Officer (CFO)",
        "manager_id": None,
        "active_status": True
    })
    
    dept_keys = list(DEPARTMENT_ROLES.keys())
    
    # 2. Department Heads / Managers (USR_1002 to USR_1009)
    dept_managers: Dict[str, str] = {}
    user_idx = 1002
    for dept_id in dept_keys:
        uid = f"USR_{user_idx}"
        dept_managers[dept_id] = uid
        role = DEPARTMENT_ROLES[dept_id][0]
        users.append({
            "user_id": uid,
            "user_name": fake.name(),
            "department_id": dept_id,
            "role": role,
            "manager_id": "USR_1001",
            "active_status": True
        })
        user_idx += 1
        
    # 3. Staff and Specialists (USR_1010 to USR_1060)
    for i in range(user_idx, 1001 + num_users):
        dept_id = dept_keys[(i - 1010) % len(dept_keys)]
        role_options = DEPARTMENT_ROLES[dept_id][1:]
        role = role_options[(i) % len(role_options)]
        mgr_id = dept_managers[dept_id]
        
        # 95% active, 5% inactive (historical users)
        is_active = (i % 20 != 0)
        
        users.append({
            "user_id": f"USR_{i}",
            "user_name": fake.name(),
            "department_id": dept_id,
            "role": role,
            "manager_id": mgr_id,
            "active_status": is_active
        })
        
    return pd.DataFrame(users)
