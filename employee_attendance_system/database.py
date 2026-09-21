"""
Database setup and operations for AIET Employee Attendance & Salary Processing System.
Uses SQLite 3 with parameterized queries and foreign key constraints.
"""

import sqlite3
import os
from utils import get_db_path

def get_connection():
    """Establish and return a connection to the SQLite database."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Create the required database tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Employees Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            joining_date TEXT NOT NULL,
            basic_salary REAL NOT NULL DEFAULT 0.0,
            overtime_rate REAL NOT NULL DEFAULT 0.0,
            allowances REAL NOT NULL DEFAULT 0.0,
            deductions REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'Active'
        )
    """)

    # 2. Attendance Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            total_working_days INTEGER NOT NULL,
            days_present INTEGER NOT NULL,
            leave_days INTEGER NOT NULL,
            overtime_hours REAL NOT NULL DEFAULT 0.0,
            UNIQUE(employee_id, month, year),
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
        )
    """)

    # 3. Salary Records Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salary_records (
            salary_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            basic_salary REAL NOT NULL,
            total_working_days INTEGER NOT NULL,
            days_present INTEGER NOT NULL,
            leave_days INTEGER NOT NULL,
            overtime_hours REAL NOT NULL,
            overtime_rate REAL NOT NULL,
            attendance_salary REAL NOT NULL,
            overtime_pay REAL NOT NULL,
            allowances REAL NOT NULL,
            gross_salary REAL NOT NULL,
            deductions REAL NOT NULL,
            net_salary REAL NOT NULL,
            calculated_date TEXT NOT NULL,
            UNIQUE(employee_id, month, year),
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

def generate_500_sample_employees():
    """Generate 500 realistic employees across AIET departments."""
    m_names = [
        'Rajesh', 'Manoj', 'Suresh', 'Karthik', 'Prabhakar', 'Ramesh', 'Sandeep', 'Arvind',
        'Vinay', 'Gautham', 'Harish', 'Naveen', 'Chethan', 'Rakshith', 'Ashish', 'Praveen',
        'Santosh', 'Bharath', 'Vikram', 'Sudhir', 'Sharath', 'Raghav', 'Vijay', 'Kiran',
        'Prasad', 'Mohan', 'Satish', 'Ganesh', 'Umesh', 'Jagadish', 'Mahesh', 'Anand'
    ]
    f_names = [
        'Ananya', 'Sneha', 'Divya', 'Priya', 'Pooja', 'Deepa', 'Shweta', 'Rohini',
        'Meghana', 'Shilpa', 'Bhavya', 'Sushmitha', 'Kavya', 'Swathi', 'Manjula', 'Rashmi',
        'Keerthi', 'Archana', 'Jyothi', 'Usha', 'Sunitha', 'Pallavi', 'Radhika', 'Geetha'
    ]
    surnames = [
        'Shetty', 'Bhat', 'Hegde', 'Rao', 'Poojary', 'Alva', 'Mendon', 'Naik',
        'Shenoy', 'Acharya', 'Kulal', 'Prabhu', 'Kamath', 'Pai', 'Nayak', 'Kotian',
        'Bangera', 'Salian', 'Karkera', 'Devadiga', 'Rai', 'Ballal', 'Kumble', 'Kadri',
        'Suvarna', 'Karanth', 'Soans', 'Kunder', 'Anchan', 'Amin', 'Somayaji', 'Kudva'
    ]

    dept_configs = [
        {"dept": "Computer Science & Eng", "prefix": "AIET-CSE", "base": 101, "count": 65, "tech": True},
        {"dept": "Information Science & Eng", "prefix": "AIET-ISE", "base": 201, "count": 45, "tech": True},
        {"dept": "Electronics & Communication", "prefix": "AIET-ECE", "base": 301, "count": 55, "tech": True},
        {"dept": "Mechanical Engineering", "prefix": "AIET-ME", "base": 401, "count": 45, "tech": True},
        {"dept": "Civil Engineering", "prefix": "AIET-CV", "base": 501, "count": 40, "tech": True},
        {"dept": "Artificial Intelligence & ML", "prefix": "AIET-AIML", "base": 601, "count": 45, "tech": True},
        {"dept": "Data Science & Analytics", "prefix": "AIET-AIDS", "base": 701, "count": 35, "tech": True},
        {"dept": "Basic Science & Humanities", "prefix": "AIET-BSH", "base": 801, "count": 50, "tech": True},
        {"dept": "Management Studies (MBA)", "prefix": "AIET-MBA", "base": 901, "count": 25, "tech": False},
        {"dept": "Administration & Accounts", "prefix": "AIET-ADM", "base": 1, "count": 25, "tech": False},
        {"dept": "Examination & Academic Cell", "prefix": "AIET-EXAM", "base": 1, "count": 15, "tech": False},
        {"dept": "Library & Information Center", "prefix": "AIET-LIB", "base": 1, "count": 12, "tech": False},
        {"dept": "Training & Placement Cell", "prefix": "AIET-TPO", "base": 1, "count": 13, "tech": False},
        {"dept": "Laboratory & Technical Support", "prefix": "AIET-LAB", "base": 1, "count": 30, "tech": True},
    ]

    employees = []
    g_idx = 0
    for cfg in dept_configs:
        for i in range(cfg["count"]):
            g_idx += 1
            is_female = (g_idx * 7 + i * 3) % 2 == 0
            fname = f_names[(g_idx + i) % len(f_names)] if is_female else m_names[(g_idx + i) % len(m_names)]
            sname = surnames[(g_idx * 3 + i * 2) % len(surnames)]

            num_str = str(cfg["base"] + i) if cfg["base"] >= 100 else str(cfg["base"] + i).zfill(3)
            emp_id = f"{cfg['prefix']}-{num_str}"

            if i == 0 and cfg["tech"]:
                name = f"Dr. {fname} {sname}"
                desig = "Professor & HOD"
                basic = 85000.0 + (g_idx % 5) * 2000.0
                ot_rate = 500.0
                allow = 12000.0
                deduct = 8500.0
            elif i < 4 and cfg["tech"]:
                name = f"Dr. {fname} {sname}"
                desig = "Professor"
                basic = 75000.0 + (g_idx % 4) * 2000.0
                ot_rate = 450.0
                allow = 10000.0
                deduct = 7200.0
            elif i < 10 and cfg["tech"]:
                prefix_t = "Dr. " if i % 2 == 0 else "Prof. "
                name = f"{prefix_t}{fname} {sname}"
                desig = "Associate Professor"
                basic = 60000.0 + (g_idx % 5) * 1500.0
                ot_rate = 400.0
                allow = 8000.0
                deduct = 5500.0
            elif cfg["tech"] and i < cfg["count"] - 4:
                name = f"Prof. {fname} {sname}"
                desig = "Assistant Professor"
                basic = 45000.0 + (g_idx % 7) * 1500.0
                ot_rate = 350.0
                allow = 6000.0
                deduct = 4200.0
            elif cfg["tech"]:
                prefix_t = "Ms. " if is_female else "Mr. "
                name = f"{prefix_t}{fname} {sname}"
                desig = "Lab Instructor"
                basic = 30000.0 + (g_idx % 4) * 1200.0
                ot_rate = 250.0
                allow = 3500.0
                deduct = 2600.0
            elif "Administration" in cfg["dept"]:
                prefix_t = "Ms. " if is_female else "Mr. "
                name = f"{prefix_t}{fname} {sname}"
                desig = "Administrative Officer" if i == 0 else "Superintendent" if i < 4 else "Office Executive"
                basic = 55000.0 if i == 0 else 35000.0 + (g_idx % 4) * 1500.0
                ot_rate = 300.0
                allow = 5000.0
                deduct = 3800.0
            elif "Library" in cfg["dept"]:
                prefix_t = "Ms. " if is_female else "Mr. "
                name = f"{prefix_t}{fname} {sname}"
                desig = "Chief Librarian" if i == 0 else "Assistant Librarian"
                basic = 52000.0 if i == 0 else 32000.0 + (g_idx % 3) * 1200.0
                ot_rate = 280.0
                allow = 4500.0
                deduct = 3200.0
            elif "Placement" in cfg["dept"]:
                prefix_t = "Ms. " if is_female else "Mr. "
                name = f"{prefix_t}{fname} {sname}"
                desig = "Head - Training & Placement" if i == 0 else "Placement Coordinator"
                basic = 65000.0 if i == 0 else 42000.0 + (g_idx % 4) * 1500.0
                ot_rate = 350.0
                allow = 7000.0
                deduct = 4500.0
            else:
                name = f"Prof. {fname} {sname}"
                desig = "Associate Professor" if i < 3 else "Assistant Professor"
                basic = 48000.0 + (g_idx % 5) * 1500.0
                ot_rate = 350.0
                allow = 6500.0
                deduct = 4300.0

            email = f"{fname.lower()}.{sname.lower()}{i if i > 0 and i % 5 == 0 else ''}@aiet.org.in"
            ph_prefix = ["9845", "9741", "9611", "9900", "9880"][g_idx % 5]
            phone = f"{ph_prefix}{str(100000 + ((g_idx * 1337 + i * 29) % 900000))[:6]}"
            join_date = f"{2015 + (g_idx % 10)}-{str(1 + (g_idx % 12)).zfill(2)}-{str(1 + ((g_idx * 3) % 28)).zfill(2)}"
            status = "Inactive" if (g_idx % 33 == 0) else "Active"

            employees.append((
                emp_id, name, cfg["dept"], desig, phone, email,
                join_date, basic, ot_rate, allow, deduct, status
            ))

    return employees

def insert_sample_data():
    """
    Populate realistic demo records for Alvas Institute of Engineering & Technology (AIET).
    Generates all 500 faculty and administrative staff.
    """
    init_database()
    conn = get_connection()
    cursor = conn.cursor()

    sample_employees = generate_500_sample_employees()

    inserted_count = 0
    for emp in sample_employees:
        try:
            cursor.execute("""
                INSERT INTO employees (
                    employee_id, name, department, designation, phone, email,
                    joining_date, basic_salary, overtime_rate, allowances, deductions, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, emp)
            inserted_count += 1
        except sqlite3.IntegrityError:
            pass  # Already exists

    from datetime import datetime, date
    now = datetime.now()
    cur_m = 9
    cur_y = 2026

    # Generate attendance for all 500 employees
    sample_attendance = []
    for idx, emp in enumerate(sample_employees):
        emp_id = emp[0]
        status = emp[11]
        tot_days = 25
        leave = 25 if status == "Inactive" else (3 if idx % 11 == 0 else 2 if idx % 7 == 0 else 1 if idx % 5 == 0 else 0)
        pres = tot_days - leave
        ot_h = 0.0 if status == "Inactive" else (12.0 if idx % 6 == 0 else 8.0 if idx % 4 == 0 else 6.0 if idx % 3 == 0 else 4.0 if idx % 2 == 0 else 0.0)
        sample_attendance.append((emp_id, cur_m, cur_y, tot_days, pres, leave, ot_h))

    for att in sample_attendance:
        try:
            cursor.execute("""
                INSERT INTO attendance (
                    employee_id, month, year, total_working_days, days_present, leave_days, overtime_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, att)
        except sqlite3.IntegrityError:
            pass

    # Sample processed salary records
    today_str = date.today().isoformat()

    cursor.execute("SELECT * FROM employees")
    all_emps = {row["employee_id"]: dict(row) for row in cursor.fetchall()}

    cursor.execute("SELECT * FROM attendance")
    all_atts = cursor.fetchall()

    for att_row in all_atts:
        emp_id = att_row["employee_id"]
        if emp_id in all_emps:
            emp = all_emps[emp_id]
            basic = emp["basic_salary"]
            ot_rate = emp["overtime_rate"]
            allowances = emp["allowances"]
            deductions = emp["deductions"]

            tot_days = att_row["total_working_days"]
            days_pres = att_row["days_present"]
            ot_hours = att_row["overtime_hours"]
            m_val = att_row["month"]
            y_val = att_row["year"]

            # Calculation formulas according to prompt specification
            att_sal = round((basic / tot_days) * days_pres, 2)
            ot_pay = round(ot_hours * ot_rate, 2)
            gross = round(att_sal + ot_pay + allowances, 2)
            net = round(gross - deductions, 2)

            try:
                cursor.execute("""
                    INSERT INTO salary_records (
                        employee_id, month, year, basic_salary, total_working_days,
                        days_present, leave_days, overtime_hours, overtime_rate,
                        attendance_salary, overtime_pay, allowances, gross_salary,
                        deductions, net_salary, calculated_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    emp_id, m_val, y_val, basic, tot_days,
                    days_pres, att_row["leave_days"], ot_hours, ot_rate,
                    att_sal, ot_pay, allowances, gross,
                    deductions, net, today_str
                ))
            except sqlite3.IntegrityError:
                pass

    conn.commit()
    conn.close()
    return inserted_count
