# AIET Employee Attendance & Salary Processing System
**Alvas Institute of Engineering and Technology (AIET), Moodbidri**

A complete, professional desktop application built with Python 3, Tkinter with ttk, SQLite, openpyxl, ReportLab, and Matplotlib.

---

## 📌 Features

1. **Dashboard:**
   - 6 statistical metric cards (Total Employees, Active Employees, Days Present, Leaves, Total Monthly Salary, Overtime Hours).
   - Real-time Departmental Headcount breakdown table.
   - Quick action shortcuts.

2. **Employee Management:**
   - Full CRUD: Add, View, Search, Update, and Delete employees.
   - Fields: Employee ID, Full Name, Department, Designation, Phone, Email, Joining Date, Basic Salary, Overtime Rate (per hour), Allowances, Deductions, and Status (Active/Inactive).
   - Validations for phone number format, email format, positive salary values, and unique Employee IDs.

3. **Attendance & Overtime Logging:**
   - Record monthly attendance (Month, Year, Total Working Days, Days Present, Leave Days, Overtime Hours).
   - Automatic validation: `Days Present + Leave Days <= Total Working Days`.

4. **Automated Salary Processing:**
   - Exact mathematical formulas implemented:
     - **Attendance Salary** = `(Basic Salary / Total Working Days) × Days Present`
     - **Overtime Pay** = `Overtime Hours × Overtime Rate`
     - **Gross Salary** = `Attendance Salary + Overtime Pay + Allowances`
     - **Net Salary** = `Gross Salary - Deductions`
   - Real-time calculation preview and permanent database storage.

5. **Excel Sheet Upload & Batch Salary Calculator:**
   - Upload monthly attendance Excel spreadsheets (`.xlsx`, `.xls`, `.csv`).
   - Automatically parses rows, links employee master records, and calculates Attendance Salary, Overtime Pay, Gross and Net Pay for the entire faculty batch.
   - Built-in validation: flags unknown employee IDs and detects if `Days Present + Leave Days > Total Working Days`.
   - Generates and exports downloadable sample Excel templates and batch-calculated results.
   - One-click batch commit into SQLite database.

6. **Official Salary Slips (PDF):**
   - High-resolution, formal AIET salary slips generated with ReportLab.
   - Clean tabular layout with institutional header, employee particulars, earnings, deductions, net salary, and signature boxes.

7. **Reports & Exports:**
   - Excel export (`openpyxl`) with headers, borders, and auto-adjusted column widths.
   - Department-wise salary and attendance analytics with Matplotlib bar chart visualization.
   - Fallback to standard CSV exports when running in minimal environments.

---

## 🚀 How to Run on Windows

### Prerequisites
1. **Python 3.8+** installed on your Windows PC.
   - When installing Python from [python.org](https://www.python.org), ensure you check the box: **"Add Python to PATH"**.

### Steps to Run:
1. Open **Command Prompt** (`cmd`) or **PowerShell**.
2. Navigate to the project directory:
   ```cmd
   cd employee_attendance_system
   ```
3. Install the required dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
4. Start the application:
   ```cmd
   python main.py
   ```

---

## 📂 Project Structure

```
employee_attendance_system/
│
├── main.py              # Main Tkinter application & dashboard
├── database.py          # SQLite database connection, tables & sample data
├── models.py            # CRUD operations & business calculation logic
├── employee.py          # Employee management GUI screen
├── attendance.py        # Monthly attendance & overtime logging GUI screen
├── salary.py            # Salary calculation and processing GUI screen
├── excel_import.py      # Excel (.xlsx/.csv) parser & batch calculation engine
├── excel_upload_screen.py # Excel upload & batch calculation GUI screen
├── reports.py           # Reports & departmental visualization GUI screen
├── pdf_generator.py     # ReportLab salary slip PDF generator
├── excel_export.py      # openpyxl formatted Excel exporter
├── utils.py             # Validation helpers & currency formatting
├── requirements.txt     # Python libraries (openpyxl, reportlab, matplotlib)
└── README.md            # Installation & project documentation
```

---

## 🏫 Institution Details
- **Institution:** Alvas Institute of Engineering and Technology (AIET)
- **Location:** Shobhavana Campus, Mijar, Moodbidri, Karnataka - 574227
- **Affiliation:** Visvesvaraya Technological University (VTU), Belagavi
- **Approval:** AICTE, New Delhi
