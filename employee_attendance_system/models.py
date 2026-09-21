"""
Data models and database access layer for AIET Employee Attendance & Salary Processing System.
Provides clean abstraction for CRUD operations and calculations.
"""

import sqlite3
from datetime import datetime
from database import get_connection

# ==============================================================================
# Employee Data Access Operations
# ==============================================================================

def add_employee(emp_data):
    """
    Insert a new employee record.
    emp_data is a tuple: (employee_id, name, department, designation, phone, email,
                          joining_date, basic_salary, overtime_rate, allowances, deductions, status)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO employees (
                employee_id, name, department, designation, phone, email,
                joining_date, basic_salary, overtime_rate, allowances, deductions, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, emp_data)
        conn.commit()
        return True, "Employee added successfully."
    except sqlite3.IntegrityError:
        return False, f"Employee ID '{emp_data[0]}' already exists. Please choose a unique ID."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def update_employee(emp_data):
    """
    Update an existing employee record.
    emp_data is a tuple: (name, department, designation, phone, email, joining_date,
                          basic_salary, overtime_rate, allowances, deductions, status, employee_id)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE employees SET
                name = ?,
                department = ?,
                designation = ?,
                phone = ?,
                email = ?,
                joining_date = ?,
                basic_salary = ?,
                overtime_rate = ?,
                allowances = ?,
                deductions = ?,
                status = ?
            WHERE employee_id = ?
        """, emp_data)
        conn.commit()
        if cursor.rowcount == 0:
            return False, f"Employee with ID '{emp_data[-1]}' not found."
        return True, "Employee updated successfully."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def delete_employee(employee_id):
    """Delete employee and cascading records."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return False, f"Employee with ID '{employee_id}' not found."
        return True, "Employee and associated records deleted successfully."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def get_employee(employee_id):
    """Fetch a single employee record by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_employees():
    """Fetch all employees ordered by Employee ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees ORDER BY employee_id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_active_employees():
    """Fetch active employees list for selection in dropdowns."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, name, department, designation FROM employees WHERE status = 'Active' ORDER BY employee_id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_employees(query):
    """Search employees by ID, name, department, or designation."""
    conn = get_connection()
    cursor = conn.cursor()
    q = f"%{query}%"
    cursor.execute("""
        SELECT * FROM employees
        WHERE employee_id LIKE ? OR name LIKE ? OR department LIKE ? OR designation LIKE ?
        ORDER BY employee_id ASC
    """, (q, q, q, q))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==============================================================================
# Attendance Data Access Operations
# ==============================================================================

def save_or_update_attendance(att_data):
    """
    Insert or update attendance for an employee for a specific month and year.
    att_data: (employee_id, month, year, total_working_days, days_present, leave_days, overtime_hours)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if record exists
        cursor.execute("""
            SELECT attendance_id FROM attendance
            WHERE employee_id = ? AND month = ? AND year = ?
        """, (att_data[0], att_data[1], att_data[2]))
        existing = cursor.fetchone()

        if existing:
            # Update existing
            cursor.execute("""
                UPDATE attendance SET
                    total_working_days = ?,
                    days_present = ?,
                    leave_days = ?,
                    overtime_hours = ?
                WHERE attendance_id = ?
            """, (att_data[3], att_data[4], att_data[5], att_data[6], existing["attendance_id"]))
            conn.commit()
            return True, "Attendance record updated successfully."
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO attendance (
                    employee_id, month, year, total_working_days, days_present, leave_days, overtime_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, att_data)
            conn.commit()
            return True, "Attendance record saved successfully."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def get_attendance(employee_id, month, year):
    """Fetch attendance for a specific employee, month, and year."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, e.name, e.department
        FROM attendance a
        JOIN employees e ON a.employee_id = e.employee_id
        WHERE a.employee_id = ? AND a.month = ? AND a.year = ?
    """, (employee_id, month, year))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_attendance(month=None, year=None):
    """Fetch all attendance records, optionally filtered by month and year."""
    conn = get_connection()
    cursor = conn.cursor()
    if month is not None and year is not None:
        cursor.execute("""
            SELECT a.*, e.name, e.department, e.designation
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE a.month = ? AND a.year = ?
            ORDER BY a.year DESC, a.month DESC, a.employee_id ASC
        """, (month, year))
    else:
        cursor.execute("""
            SELECT a.*, e.name, e.department, e.designation
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            ORDER BY a.year DESC, a.month DESC, a.employee_id ASC
        """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_attendance(query, month=None, year=None):
    """Search attendance records with optional month and year filters."""
    conn = get_connection()
    cursor = conn.cursor()
    q = f"%{query}%"
    base_query = """
        SELECT a.*, e.name, e.department, e.designation
        FROM attendance a
        JOIN employees e ON a.employee_id = e.employee_id
        WHERE (a.employee_id LIKE ? OR e.name LIKE ? OR e.department LIKE ?)
    """
    params = [q, q, q]

    if month is not None and str(month).strip() != "":
        base_query += " AND a.month = ?"
        params.append(int(month))
    if year is not None and str(year).strip() != "":
        base_query += " AND a.year = ?"
        params.append(int(year))

    base_query += " ORDER BY a.year DESC, a.month DESC, a.employee_id ASC"

    cursor.execute(base_query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_attendance(attendance_id):
    """Delete an attendance record."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM attendance WHERE attendance_id = ?", (attendance_id,))
        conn.commit()
        return True, "Attendance record deleted."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# ==============================================================================
# Salary Calculation and Processing Operations
# ==============================================================================

def calculate_salary_components(basic_salary, total_working_days, days_present, overtime_hours, overtime_rate, allowances, deductions):
    """
    Perform exact formulas defined in specifications:
    Attendance Salary = (Basic Salary / Total Working Days) * Days Present
    Overtime Pay = Overtime Hours * Overtime Rate
    Gross Salary = Attendance Salary + Overtime Pay + Allowances
    Net Salary = Gross Salary - Deductions
    """
    basic = float(basic_salary)
    total_days = max(1, int(total_working_days))
    present = int(days_present)
    ot_hrs = float(overtime_hours)
    ot_rt = float(overtime_rate)
    allow = float(allowances)
    deduct = float(deductions)

    attendance_salary = round((basic / total_days) * present, 2)
    overtime_pay = round(ot_hrs * ot_rt, 2)
    gross_salary = round(attendance_salary + overtime_pay + allow, 2)
    net_salary = round(gross_salary - deduct, 2)

    return {
        "basic_salary": basic,
        "total_working_days": total_days,
        "days_present": present,
        "overtime_hours": ot_hrs,
        "overtime_rate": ot_rt,
        "attendance_salary": attendance_salary,
        "overtime_pay": overtime_pay,
        "allowances": allow,
        "gross_salary": gross_salary,
        "deductions": deduct,
        "net_salary": net_salary
    }

def save_or_update_salary_record(salary_dict):
    """Save or update processed monthly salary in salary_records table."""
    conn = get_connection()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor.execute("""
            INSERT INTO salary_records (
                employee_id, month, year, basic_salary, total_working_days,
                days_present, leave_days, overtime_hours, overtime_rate,
                attendance_salary, overtime_pay, allowances, gross_salary,
                deductions, net_salary, calculated_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(employee_id, month, year) DO UPDATE SET
                basic_salary = excluded.basic_salary,
                total_working_days = excluded.total_working_days,
                days_present = excluded.days_present,
                leave_days = excluded.leave_days,
                overtime_hours = excluded.overtime_hours,
                overtime_rate = excluded.overtime_rate,
                attendance_salary = excluded.attendance_salary,
                overtime_pay = excluded.overtime_pay,
                allowances = excluded.allowances,
                gross_salary = excluded.gross_salary,
                deductions = excluded.deductions,
                net_salary = excluded.net_salary,
                calculated_date = excluded.calculated_date
        """, (
            salary_dict["employee_id"],
            salary_dict["month"],
            salary_dict["year"],
            salary_dict["basic_salary"],
            salary_dict["total_working_days"],
            salary_dict["days_present"],
            salary_dict["leave_days"],
            salary_dict["overtime_hours"],
            salary_dict["overtime_rate"],
            salary_dict["attendance_salary"],
            salary_dict["overtime_pay"],
            salary_dict["allowances"],
            salary_dict["gross_salary"],
            salary_dict["deductions"],
            salary_dict["net_salary"],
            today_str
        ))
        conn.commit()
        return True, "Salary record successfully processed and saved."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def get_salary_record(employee_id, month, year):
    """Get salary record for an employee for a specific month and year."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, e.name, e.department, e.designation, e.phone, e.email
        FROM salary_records s
        JOIN employees e ON s.employee_id = e.employee_id
        WHERE s.employee_id = ? AND s.month = ? AND s.year = ?
    """, (employee_id, month, year))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_salary_records(month=None, year=None):
    """Get all processed salary records, optionally filtered by month and year."""
    conn = get_connection()
    cursor = conn.cursor()
    if month is not None and year is not None:
        cursor.execute("""
            SELECT s.*, e.name, e.department, e.designation
            FROM salary_records s
            JOIN employees e ON s.employee_id = e.employee_id
            WHERE s.month = ? AND s.year = ?
            ORDER BY s.year DESC, s.month DESC, s.employee_id ASC
        """, (month, year))
    else:
        cursor.execute("""
            SELECT s.*, e.name, e.department, e.designation
            FROM salary_records s
            JOIN employees e ON s.employee_id = e.employee_id
            ORDER BY s.year DESC, s.month DESC, s.employee_id ASC
        """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==============================================================================
# Dashboard Metrics & Statistics
# ==============================================================================

def get_dashboard_metrics(current_month=None, current_year=None):
    """
    Fetch consolidated key metrics for dashboard cards:
    - Total Employees
    - Active Employees
    - Employees Present (current month)
    - Employees on Leave (current month)
    - Total Salary for Current Month
    - Total Overtime Hours
    """
    now = datetime.now()
    month = current_month if current_month is not None else now.month
    year = current_year if current_year is not None else now.year

    conn = get_connection()
    cursor = conn.cursor()

    # Total employees
    cursor.execute("SELECT COUNT(*) AS total FROM employees")
    tot_emp = cursor.fetchone()["total"]

    # Active employees
    cursor.execute("SELECT COUNT(*) AS active FROM employees WHERE status = 'Active'")
    act_emp = cursor.fetchone()["active"]

    # Attendance stats for the specified month/year
    cursor.execute("""
        SELECT
            SUM(days_present) AS sum_present,
            SUM(leave_days) AS sum_leave,
            SUM(overtime_hours) AS sum_ot
        FROM attendance
        WHERE month = ? AND year = ?
    """, (month, year))
    att_stats = cursor.fetchone()

    # Salary stats for the specified month/year
    cursor.execute("""
        SELECT
            COUNT(*) AS processed_count,
            SUM(net_salary) AS total_net,
            SUM(gross_salary) AS total_gross
        FROM salary_records
        WHERE month = ? AND year = ?
    """, (month, year))
    sal_stats = cursor.fetchone()

    # Department breakdown
    cursor.execute("""
        SELECT department, COUNT(*) as count
        FROM employees
        GROUP BY department
        ORDER BY count DESC
    """)
    dept_breakdown = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "month": month,
        "year": year,
        "total_employees": tot_emp or 0,
        "active_employees": act_emp or 0,
        "total_days_present": att_stats["sum_present"] if att_stats and att_stats["sum_present"] else 0,
        "total_leave_days": att_stats["sum_leave"] if att_stats and att_stats["sum_leave"] else 0,
        "total_overtime_hours": att_stats["sum_ot"] if att_stats and att_stats["sum_ot"] else 0.0,
        "processed_salaries_count": sal_stats["processed_count"] if sal_stats and sal_stats["processed_count"] else 0,
        "total_monthly_salary": sal_stats["total_net"] if sal_stats and sal_stats["total_net"] else 0.0,
        "total_monthly_gross": sal_stats["total_gross"] if sal_stats and sal_stats["total_gross"] else 0.0,
        "department_breakdown": dept_breakdown
    }
