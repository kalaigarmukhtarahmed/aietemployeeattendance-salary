"""
Excel Import & Batch Calculation Engine for AIET Employee Attendance & Salary Processing System.
Allows importing Excel sheets (.xlsx, .xls) and CSVs containing monthly attendance data,
auto-calculates attendance salaries, overtime pay, gross salary, deductions, and net pay,
and batch-saves records to SQLite.
"""

import os
import csv
import re
from datetime import datetime
import models
from utils import get_reports_dir, get_month_name

def generate_excel_import_template(output_path=None):
    """
    Generate a standardized Excel import template with sample AIET records
    and column formatting.
    """
    if not output_path:
        output_path = os.path.join(get_reports_dir(), "AIET_Attendance_Salary_Import_Template.xlsx")

    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance_Import"
        ws.views.sheetView[0].showGridLines = True

        # Header Title
        ws.merge_cells("A1:K1")
        ws["A1"] = "ALVAS INSTITUTE OF ENGINEERING AND TECHNOLOGY (AIET) — ATTENDANCE & SALARY IMPORT SHEET"
        ws["A1"].font = Font(name="Calibri", size=13, bold=True, color="1E3A8A")
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("A2:K2")
        ws["A2"] = "Instructions: Fill in monthly attendance figures. Basic salary, allowances & deductions will auto-load from master if left blank."
        ws["A2"].font = Font(name="Calibri", size=9, italic=True, color="64748B")
        ws["A2"].alignment = Alignment(horizontal="center", vertical="center")

        headers = [
            "Employee ID", "Month (1-12)", "Year", "Total Working Days",
            "Days Present", "Leave Days", "Overtime Hours",
            "Basic Salary (Optional)", "OT Rate (Optional)",
            "Allowances (Optional)", "Deductions (Optional)"
        ]

        fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        ws.row_dimensions[4].height = 26
        for col_num, h_text in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_num, value=h_text)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border

        # Add all employees from database or 500-employee roster
        all_emps = models.get_all_employees()
        sample_rows = []
        if all_emps:
            for idx, emp in enumerate(all_emps):
                tot_days = 25
                leave = 25 if emp.get("status") == "Inactive" else (3 if idx % 11 == 0 else 2 if idx % 7 == 0 else 1 if idx % 5 == 0 else 0)
                pres = tot_days - leave
                ot_h = 0.0 if emp.get("status") == "Inactive" else (12.0 if idx % 6 == 0 else 8.0 if idx % 4 == 0 else 6.0 if idx % 3 == 0 else 4.0 if idx % 2 == 0 else 0.0)
                sample_rows.append([emp["employee_id"], 9, 2026, tot_days, pres, leave, ot_h, "", "", "", ""])
        else:
            sample_rows = [
                ["AIET-CSE-101", 9, 2026, 25, 25, 0, 8.0, "", "", "", ""],
                ["AIET-CSE-102", 9, 2026, 25, 23, 2, 4.0, "", "", "", ""],
                ["AIET-ISE-201", 9, 2026, 25, 24, 1, 6.0, "", "", "", ""],
                ["AIET-ECE-301", 9, 2026, 25, 22, 3, 2.0, "", "", "", ""],
                ["AIET-ME-401",  9, 2026, 25, 25, 0, 10.0, "", "", "", ""],
                ["AIET-AIML-501", 9, 2026, 25, 24, 1, 5.0, "", "", "", ""],
                ["AIET-ADM-001", 9, 2026, 25, 25, 0, 12.0, "", "", "", ""],
                ["AIET-LAB-012", 9, 2026, 25, 24, 1, 6.0, "", "", "", ""],
            ]

        for r_idx, row_data in enumerate(sample_rows, 5):
            ws.row_dimensions[r_idx].height = 20
            bg_color = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
            row_fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid")
            for c_idx, val in enumerate(row_data, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                cell.fill = row_fill
                cell.border = thin_border
                cell.font = Font(name="Calibri", size=10)
                if c_idx == 1:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="center", vertical="center")

        # Column widths
        widths = [16, 14, 10, 18, 14, 12, 16, 20, 18, 20, 20]
        for col_idx, width in enumerate(widths, 1):
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = width

        wb.save(output_path)
        return True, output_path

    except ImportError:
        # Fallback to CSV
        csv_path = output_path.replace(".xlsx", ".csv")
        headers = [
            "Employee ID", "Month", "Year", "Total Working Days",
            "Days Present", "Leave Days", "Overtime Hours",
            "Basic Salary", "OT Rate", "Allowances", "Deductions"
        ]
        sample_rows = [
            ["AIET-CSE-101", 9, 2026, 25, 25, 0, 8.0, "", "", "", ""],
            ["AIET-CSE-102", 9, 2026, 25, 23, 2, 4.0, "", "", "", ""],
            ["AIET-ISE-201", 9, 2026, 25, 24, 1, 6.0, "", "", "", ""],
            ["AIET-ECE-301", 9, 2026, 25, 22, 3, 2.0, "", "", "", ""],
            ["AIET-ME-401",  9, 2026, 25, 25, 0, 10.0, "", "", "", ""],
            ["AIET-AIML-501", 9, 2026, 25, 24, 1, 5.0, "", "", "", ""],
            ["AIET-ADM-001", 9, 2026, 25, 25, 0, 12.0, "", "", "", ""],
            ["AIET-LAB-012", 9, 2026, 25, 24, 1, 6.0, "", "", "", ""],
        ]
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(sample_rows)
        return True, csv_path


def normalize_header(h):
    """Normalize column header strings for flexible matching."""
    if not h:
        return ""
    h = str(h).lower().strip()
    h = re.sub(r'[^a-z0-9]', '', h)
    return h


def parse_and_calculate_excel(file_path):
    """
    Parse an Excel (.xlsx, .xls) or CSV file, look up employee master details if omitted,
    and compute:
        Attendance Salary = (Basic / Total Working Days) * Days Present
        Overtime Pay = Overtime Hours * Overtime Rate
        Gross Salary = Attendance Salary + Overtime Pay + Allowances
        Net Salary = Gross Salary - Deductions
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File does not exist: {file_path}", "records": []}

    rows_data = []

    # 1. Read file rows
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".xlsx", ".xlsm", ".xltx"]:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(values_only=True):
                if row and any(c is not None and str(c).strip() != "" for c in row):
                    rows_data.append([str(c).strip() if c is not None else "" for c in row])
        except ImportError:
            return {"success": False, "error": "openpyxl is not installed. Please install openpyxl or upload a CSV file.", "records": []}
        except Exception as e:
            return {"success": False, "error": f"Error reading Excel file: {str(e)}", "records": []}
    else:
        # Assume CSV or TSV
        try:
            with open(file_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
                delimiter = "\t" if ext == ".tsv" else ","
                reader = csv.reader(f, delimiter=delimiter)
                for row in reader:
                    if row and any(c.strip() != "" for c in row):
                        rows_data.append([c.strip() for c in row])
        except Exception as e:
            return {"success": False, "error": f"Error reading CSV file: {str(e)}", "records": []}

    if not rows_data:
        return {"success": False, "error": "The uploaded file is empty.", "records": []}

    # 2. Locate header row
    header_idx = -1
    col_map = {}

    for idx, row in enumerate(rows_data[:10]):
        norm_row = [normalize_header(c) for c in row]
        # Look for indicators of an employee attendance row
        has_emp = any(k in norm_row for k in ["employeeid", "empid", "id", "employee", "staffid"])
        has_att = any(k in norm_row for k in ["dayspresent", "present", "workingdays", "totalworkingdays", "presentdays"])
        if has_emp or has_att:
            header_idx = idx
            break

    if header_idx == -1:
        # Default to row 0
        header_idx = 0

    header_row = rows_data[header_idx]

    # Map column names
    field_keywords = {
        "emp_id": ["employeeid", "empid", "id", "employee", "facultyid", "staffid"],
        "month": ["month", "m", "paymonth", "monthnumber", "periodmonth"],
        "year": ["year", "y", "payyear", "periodyear"],
        "total_working_days": ["totalworkingdays", "workingdays", "totaldays", "workdays", "daysinmonth"],
        "days_present": ["dayspresent", "presentdays", "present", "attendeddays", "daysattended", "attended"],
        "leave_days": ["leavedays", "leaves", "leave", "absentdays", "absent"],
        "overtime_hours": ["overtimehours", "overtime", "othours", "ot", "extrahours", "othrs"],
        "basic_salary": ["basicsalary", "basic", "basicsal"],
        "overtime_rate": ["overtimerate", "otrate", "rateperhour", "hourlyrate"],
        "allowances": ["allowances", "allowance", "da", "hra"],
        "deductions": ["deductions", "deduction", "pf", "tax"]
    }

    for col_i, h in enumerate(header_row):
        norm = normalize_header(h)
        for field, keywords in field_keywords.items():
            if field not in col_map and norm in keywords:
                col_map[field] = col_i

    # Fallback to positional columns if essential headers not recognized
    if "emp_id" not in col_map and len(header_row) > 0:
        col_map["emp_id"] = 0
    if "month" not in col_map and len(header_row) > 1:
        col_map["month"] = 1
    if "year" not in col_map and len(header_row) > 2:
        col_map["year"] = 2
    if "total_working_days" not in col_map and len(header_row) > 3:
        col_map["total_working_days"] = 3
    if "days_present" not in col_map and len(header_row) > 4:
        col_map["days_present"] = 4
    if "leave_days" not in col_map and len(header_row) > 5:
        col_map["leave_days"] = 5
    if "overtime_hours" not in col_map and len(header_row) > 6:
        col_map["overtime_hours"] = 6

    # 3. Process data rows
    all_employees_cache = {e["employee_id"].strip().upper(): e for e in models.get_all_employees()}

    records = []
    now = datetime.now()
    default_month = now.month
    default_year = now.year

    for r_idx, row in enumerate(rows_data[header_idx + 1:], start=header_idx + 2):
        if not any(row):
            continue

        def get_val(field, default=""):
            idx = col_map.get(field)
            if idx is not None and idx < len(row):
                return str(row[idx]).strip()
            return default

        raw_emp_id = get_val("emp_id").upper()
        if not raw_emp_id:
            continue

        raw_m = get_val("month", str(default_month))
        raw_y = get_val("year", str(default_year))
        raw_tot = get_val("total_working_days", "25")
        raw_pres = get_val("days_present", "25")
        raw_leave = get_val("leave_days", "0")
        raw_ot = get_val("overtime_hours", "0.0")

        # Parsing numeric fields with error safeguards
        try:
            # Handle month text like "September" or "9"
            if raw_m.isdigit():
                m_val = int(raw_m)
            else:
                import calendar
                m_val = default_month
                for mi, mname in enumerate(calendar.month_name):
                    if mname.lower() == raw_m.lower():
                        m_val = mi
                        break
            if not (1 <= m_val <= 12):
                m_val = default_month
        except Exception:
            m_val = default_month

        try:
            y_val = int(raw_y) if raw_y.isdigit() else default_year
        except Exception:
            y_val = default_year

        try:
            tot_days = max(1, int(float(raw_tot)))
        except Exception:
            tot_days = 25

        try:
            pres_days = max(0, int(float(raw_pres)))
        except Exception:
            pres_days = 0

        try:
            leave_days = max(0, int(float(raw_leave)))
        except Exception:
            leave_days = 0

        try:
            ot_hours = max(0.0, float(raw_ot))
        except Exception:
            ot_hours = 0.0

        # Look up employee
        emp = all_employees_cache.get(raw_emp_id)
        is_valid = True
        status_msg = "Ready to Calculate"

        if not emp:
            is_valid = False
            status_msg = f"Employee ID '{raw_emp_id}' not found in database."
            emp_name = "Unknown Staff"
            dept = "Unknown Department"
            desig = "Unknown Designation"
            basic = 0.0
            ot_rate = 0.0
            allow = 0.0
            deduct = 0.0
        else:
            emp_name = emp["name"]
            dept = emp["department"]
            desig = emp["designation"]
            basic = float(emp["basic_salary"])
            ot_rate = float(emp["overtime_rate"])
            allow = float(emp["allowances"])
            deduct = float(emp["deductions"])

        # Check optional overrides from sheet
        raw_basic = get_val("basic_salary")
        if raw_basic:
            try:
                basic = float(raw_basic)
            except Exception:
                pass

        raw_ot_rate = get_val("overtime_rate")
        if raw_ot_rate:
            try:
                ot_rate = float(raw_ot_rate)
            except Exception:
                pass

        raw_allow = get_val("allowances")
        if raw_allow:
            try:
                allow = float(raw_allow)
            except Exception:
                pass

        raw_deduct = get_val("deductions")
        if raw_deduct:
            try:
                deduct = float(raw_deduct)
            except Exception:
                pass

        # Validation: Present + Leaves <= Total Working Days
        if pres_days + leave_days > tot_days:
            is_valid = False
            status_msg = f"Present ({pres_days}) + Leave ({leave_days}) exceeds Total Days ({tot_days})."
        elif is_valid:
            status_msg = "Calculated & Verified"

        # Formulas
        att_salary = round((basic / tot_days) * pres_days, 2)
        ot_pay = round(ot_hours * ot_rate, 2)
        gross_salary = round(att_salary + ot_pay + allow, 2)
        net_salary = round(gross_salary - deduct, 2)

        record = {
            "row_num": r_idx,
            "employee_id": raw_emp_id,
            "name": emp_name,
            "department": dept,
            "designation": desig,
            "month": m_val,
            "year": y_val,
            "month_name": get_month_name(m_val),
            "total_working_days": tot_days,
            "days_present": pres_days,
            "leave_days": leave_days,
            "overtime_hours": ot_hours,
            "overtime_rate": ot_rate,
            "basic_salary": basic,
            "attendance_salary": att_salary,
            "overtime_pay": ot_pay,
            "allowances": allow,
            "gross_salary": gross_salary,
            "deductions": deduct,
            "net_salary": net_salary,
            "is_valid": is_valid,
            "status": status_msg
        }
        records.append(record)

    valid_count = sum(1 for r in records if r["is_valid"])
    error_count = len(records) - valid_count
    total_gross = sum(r["gross_salary"] for r in records if r["is_valid"])
    total_net = sum(r["net_salary"] for r in records if r["is_valid"])

    return {
        "success": True,
        "total_rows": len(records),
        "valid_rows": valid_count,
        "error_rows": error_count,
        "total_gross": total_gross,
        "total_net": total_net,
        "records": records
    }


def save_batch_to_database(records):
    """
    Batch-save all valid calculated records into attendance and salary_records tables.
    Returns (saved_count, error_count, list_of_errors).
    """
    saved_count = 0
    errors = []

    for r in records:
        if not r["is_valid"]:
            errors.append(f"Skipped row {r['row_num']} ({r['employee_id']}): {r['status']}")
            continue

        # 1. Save Attendance
        att_data = (
            r["employee_id"],
            r["month"],
            r["year"],
            r["total_working_days"],
            r["days_present"],
            r["leave_days"],
            r["overtime_hours"]
        )
        ok_att, msg_att = models.save_or_update_attendance(att_data)
        if not ok_att:
            errors.append(f"Row {r['row_num']} attendance error: {msg_att}")
            continue

        # 2. Save Salary Record
        sal_dict = {
            "employee_id": r["employee_id"],
            "month": r["month"],
            "year": r["year"],
            "basic_salary": r["basic_salary"],
            "total_working_days": r["total_working_days"],
            "days_present": r["days_present"],
            "leave_days": r["leave_days"],
            "overtime_hours": r["overtime_hours"],
            "overtime_rate": r["overtime_rate"],
            "attendance_salary": r["attendance_salary"],
            "overtime_pay": r["overtime_pay"],
            "allowances": r["allowances"],
            "gross_salary": r["gross_salary"],
            "deductions": r["deductions"],
            "net_salary": r["net_salary"]
        }
        ok_sal, msg_sal = models.save_or_update_salary_record(sal_dict)
        if not ok_sal:
            errors.append(f"Row {r['row_num']} salary error: {msg_sal}")
            continue

        saved_count += 1

    return saved_count, len(errors), errors


def export_calculated_to_excel(records, output_path=None):
    """
    Export the calculated attendance and salary sheet into Excel or CSV with full calculations.
    """
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(get_reports_dir(), f"AIET_Calculated_Payroll_Batch_{timestamp}.xlsx")

    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Calculated_Payroll"
        ws.views.sheetView[0].showGridLines = True

        # Header
        ws.merge_cells("A1:Q1")
        ws["A1"] = "ALVAS INSTITUTE OF ENGINEERING AND TECHNOLOGY (AIET) — BATCH CALCULATED PAYROLL"
        ws["A1"].font = Font(name="Calibri", size=13, bold=True, color="1E3A8A")
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells("A2:Q2")
        ws["A2"] = f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Records: {len(records)}"
        ws["A2"].font = Font(name="Calibri", size=9, italic=True, color="64748B")
        ws["A2"].alignment = Alignment(horizontal="center", vertical="center")

        headers = [
            "Emp ID", "Employee Name", "Department", "Designation",
            "Period", "Total Days", "Present Days", "Leave Days", "OT Hours",
            "Basic Salary", "Att. Salary", "OT Pay", "Allowances", "Gross Salary",
            "Deductions", "Net Salary", "Status"
        ]

        fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        ws.row_dimensions[4].height = 25
        for col_num, h_text in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_num, value=h_text)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        for r_idx, r in enumerate(records, 5):
            ws.row_dimensions[r_idx].height = 20
            bg_color = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
            row_fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid")
            period_str = f"{r['month_name']} {r['year']}"

            row_data = [
                r["employee_id"], r["name"], r["department"], r["designation"],
                period_str, r["total_working_days"], r["days_present"], r["leave_days"], r["overtime_hours"],
                f"₹ {r['basic_salary']:,.2f}", f"₹ {r['attendance_salary']:,.2f}", f"₹ {r['overtime_pay']:,.2f}",
                f"₹ {r['allowances']:,.2f}", f"₹ {r['gross_salary']:,.2f}", f"₹ {r['deductions']:,.2f}",
                f"₹ {r['net_salary']:,.2f}", r["status"]
            ]

            for c_idx, val in enumerate(row_data, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                cell.fill = row_fill
                cell.border = thin_border
                cell.font = Font(name="Calibri", size=9)
                if c_idx in [1, 2, 3, 4, 5]:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                elif c_idx in [6, 7, 8, 9]:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif c_idx == 17:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    if r["is_valid"]:
                        cell.font = Font(name="Calibri", size=9, color="16A34A", bold=True)
                    else:
                        cell.font = Font(name="Calibri", size=9, color="DC2626", bold=True)
                else:
                    cell.alignment = Alignment(horizontal="right", vertical="center")

        widths = [14, 22, 22, 18, 14, 11, 11, 11, 10, 14, 14, 12, 13, 15, 13, 16, 20]
        for col_idx, width in enumerate(widths, 1):
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = width

        wb.save(output_path)
        return True, output_path

    except ImportError:
        csv_path = output_path.replace(".xlsx", ".csv")
        headers = [
            "Emp ID", "Employee Name", "Department", "Designation",
            "Period", "Total Days", "Present Days", "Leave Days", "OT Hours",
            "Basic Salary", "Att Salary", "OT Pay", "Allowances", "Gross Salary",
            "Deductions", "Net Salary", "Status"
        ]
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in records:
                writer.writerow([
                    r["employee_id"], r["name"], r["department"], r["designation"],
                    f"{r['month_name']} {r['year']}", r["total_working_days"], r["days_present"],
                    r["leave_days"], r["overtime_hours"], r["basic_salary"], r["attendance_salary"],
                    r["overtime_pay"], r["allowances"], r["gross_salary"], r["deductions"],
                    r["net_salary"], r["status"]
                ])
        return True, csv_path
