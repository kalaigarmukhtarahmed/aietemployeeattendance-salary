"""
Utility functions and validation logic for AIET Employee Attendance & Salary Processing System.
"""

import os
import re
from datetime import datetime

def get_base_dir():
    """Return the base directory of the project."""
    return os.path.dirname(os.path.abspath(__file__))

def get_db_path():
    """Ensure database directory exists and return SQLite db file path."""
    db_dir = os.path.join(get_base_dir(), "database")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "employee_system.db")

def get_reports_dir():
    """Ensure reports directory exists and return directory path."""
    rep_dir = os.path.join(get_base_dir(), "reports")
    os.makedirs(rep_dir, exist_ok=True)
    return rep_dir

def get_salary_slips_dir():
    """Ensure salary slips directory exists and return directory path."""
    slips_dir = os.path.join(get_base_dir(), "salary_slips")
    os.makedirs(slips_dir, exist_ok=True)
    return slips_dir

def validate_employee_id(emp_id):
    """Validate that employee ID is not empty and follows alphanumeric pattern."""
    if not emp_id or not emp_id.strip():
        return False, "Employee ID is required."
    emp_id = emp_id.strip()
    if len(emp_id) < 2 or len(emp_id) > 20:
        return False, "Employee ID must be between 2 and 20 characters."
    if not re.match(r"^[A-Za-z0-9_-]+$", emp_id):
        return False, "Employee ID must only contain letters, numbers, hyphens, or underscores."
    return True, ""

def validate_phone(phone):
    """Validate phone number format (10-15 digits, optional + prefix)."""
    if not phone or not phone.strip():
        return False, "Phone number is required."
    clean_phone = phone.strip().replace(" ", "").replace("-", "")
    if not re.match(r"^\+?[0-9]{10,15}$", clean_phone):
        return False, "Enter a valid 10 to 15 digit phone number (e.g., 9876543210 or +919876543210)."
    return True, ""

def validate_email(email):
    """Validate email address format."""
    if not email or not email.strip():
        return False, "Email address is required."
    email = email.strip()
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        return False, "Enter a valid email address (e.g., faculty@aiet.org.in)."
    return True, ""

def validate_date(date_str):
    """Validate date format YYYY-MM-DD."""
    if not date_str or not date_str.strip():
        return False, "Date is required (Format: YYYY-MM-DD)."
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD (e.g., 2024-06-15)."

def validate_positive_number(val_str, field_name, allow_zero=True):
    """Validate that string represents a valid non-negative number."""
    if val_str is None or str(val_str).strip() == "":
        return False, f"{field_name} is required."
    try:
        num = float(val_str)
        if allow_zero and num < 0:
            return False, f"{field_name} cannot be negative."
        if not allow_zero and num <= 0:
            return False, f"{field_name} must be greater than zero."
        return True, ""
    except ValueError:
        return False, f"{field_name} must be a valid numeric value."

def validate_attendance_days(total_working_days, days_present, leave_days):
    """Validate that days present + leave days <= total working days."""
    try:
        total = int(total_working_days)
        present = int(days_present)
        leave = int(leave_days)
    except (ValueError, TypeError):
        return False, "Working days, present days, and leave days must be integers."

    if total <= 0:
        return False, "Total working days must be greater than zero."
    if present < 0 or leave < 0:
        return False, "Days present and leave days cannot be negative."
    if (present + leave) > total:
        return False, f"Days Present ({present}) + Leave Days ({leave}) = {present + leave}, which exceeds Total Working Days ({total})."
    return True, ""

def format_currency(amount):
    """Format a number into Indian Rupee currency string representation."""
    try:
        val = float(amount)
        return f"₹ {val:,.2f}"
    except (ValueError, TypeError):
        return "₹ 0.00"

def get_month_name(month_num):
    """Get month name from 1-indexed number."""
    import calendar
    try:
        return calendar.month_name[int(month_num)]
    except (IndexError, ValueError):
        return str(month_num)
