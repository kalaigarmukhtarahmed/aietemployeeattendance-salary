"""
AIET Employee Attendance & Salary Processing System
Alvas Institute of Engineering and Technology (AIET), Moodbidri
Main Application Entry Point (Desktop GUI using Python 3, Tkinter, ttk, and SQLite)
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Ensure local imports work reliably
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
import models
from utils import format_currency, get_month_name, get_salary_slips_dir
from employee import EmployeeScreen
from attendance import AttendanceScreen
from salary import SalaryScreen
from reports import ReportsScreen
from pdf_generator import generate_salary_slip_pdf
from excel_upload_screen import ExcelUploadScreen

class AIETApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialize SQLite database and tables
        database.init_database()

        # Window Configuration
        self.title("AIET Employee Attendance & Salary Processing System")
        self.geometry("1200x720")
        self.minsize(1050, 650)

        # Apply Modern Clean Blue / White Institutional Theme
        self.configure(bg="#f8fafc")
        self.setup_ttk_styles()

        # Layout Containers
        self.create_header()
        self.create_main_container()
        self.create_sidebar()

        # Initialize screen containers
        self.screens = {}
        self.init_screens()

        # Show Dashboard by default
        self.show_screen("dashboard")

    def setup_ttk_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(".", font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#e2e8f0", foreground="#1e293b")
        style.configure("Treeview", rowheight=24, font=("Segoe UI", 9))
        style.map("Treeview", background=[("selected", "#0284c7")], foreground=[("selected", "#ffffff")])
        style.configure("TNotebook.Tab", font=("Segoe UI", 9, "bold"), padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", "#1e3a8a")], foreground=[("selected", "#ffffff")])

    def create_header(self):
        self.header_frame = tk.Frame(self, bg="#1e3a8a", height=65)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)
        self.header_frame.pack_propagate(False)

        # College Emblem / Name Branding
        brand_frame = tk.Frame(self.header_frame, bg="#1e3a8a")
        brand_frame.pack(side=tk.LEFT, padx=20, pady=8)

        lbl_college = tk.Label(
            brand_frame,
            text="ALVAS INSTITUTE OF ENGINEERING AND TECHNOLOGY",
            font=("Segoe UI", 13, "bold"),
            fg="#ffffff",
            bg="#1e3a8a"
        )
        lbl_college.pack(anchor=tk.W)

        lbl_subtitle = tk.Label(
            brand_frame,
            text="Employee Attendance & Salary Processing System | Moodbidri, Karnataka",
            font=("Segoe UI", 9),
            fg="#93c5fd",
            bg="#1e3a8a"
        )
        lbl_subtitle.pack(anchor=tk.W)

        # Right side status and current date
        now = datetime.now()
        date_str = now.strftime("%A, %d %B %Y")
        lbl_date = tk.Label(
            self.header_frame,
            text=f"📅 {date_str}   |   Admin Portal",
            font=("Segoe UI", 9, "bold"),
            fg="#f8fafc",
            bg="#1e3a8a"
        )
        lbl_date.pack(side=tk.RIGHT, padx=25, pady=20)

    def create_main_container(self):
        self.body_container = tk.Frame(self, bg="#f8fafc")
        self.body_container.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.body_container, bg="#0f172a", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Sidebar Title
        nav_lbl = tk.Label(
            self.sidebar,
            text="NAVIGATION",
            font=("Segoe UI", 8, "bold"),
            fg="#64748b",
            bg="#0f172a"
        )
        nav_lbl.pack(anchor=tk.W, padx=20, pady=(20, 10))

        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊 Dashboard"),
            ("employees", "👥 Employees"),
            ("attendance", "🕒 Attendance"),
            ("salary", "💰 Salary Processing"),
            ("excel_upload", "📥 Upload Excel & Calc"),
            ("salary_slips", "📄 Salary Slips"),
            ("reports", "📈 Reports"),
            ("settings", "⚙ Settings / Demo"),
            ("exit", "🚪 Exit System")
        ]

        for screen_key, label_text in nav_items:
            if screen_key == "exit":
                # Add separator before exit
                sep = tk.Frame(self.sidebar, bg="#1e293b", height=1)
                sep.pack(fill=tk.X, padx=15, pady=(20, 10))
                btn = tk.Button(
                    self.sidebar,
                    text=label_text,
                    font=("Segoe UI", 10, "bold"),
                    fg="#f87171",
                    bg="#0f172a",
                    activebackground="#450a0a",
                    activeforeground="#fca5a5",
                    relief=tk.FLAT,
                    anchor=tk.W,
                    padx=20,
                    pady=8,
                    cursor="hand2",
                    command=self.confirm_exit
                )
            else:
                btn = tk.Button(
                    self.sidebar,
                    text=label_text,
                    font=("Segoe UI", 10),
                    fg="#cbd5e1",
                    bg="#0f172a",
                    activebackground="#1e293b",
                    activeforeground="#ffffff",
                    relief=tk.FLAT,
                    anchor=tk.W,
                    padx=20,
                    pady=8,
                    cursor="hand2",
                    command=lambda k=screen_key: self.show_screen(k)
                )
            btn.pack(fill=tk.X, pady=1)
            self.nav_buttons[screen_key] = btn

        # Content area frame
        self.content_area = tk.Frame(self.body_container, bg="#f8fafc")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def init_screens(self):
        # 1. Dashboard Screen Frame
        self.screens["dashboard"] = self.create_dashboard_screen()

        # 2. Employees Screen
        self.screens["employees"] = EmployeeScreen(self.content_area, on_data_changed_callback=self.on_data_updated)

        # 3. Attendance Screen
        self.screens["attendance"] = AttendanceScreen(self.content_area, on_data_changed_callback=self.on_data_updated)

        # 4. Salary Processing Screen
        self.screens["salary"] = SalaryScreen(self.content_area, on_data_changed_callback=self.on_data_updated)

        # 4b. Excel Upload & Batch Calculation Screen
        self.screens["excel_upload"] = ExcelUploadScreen(self.content_area, on_data_changed_callback=self.on_data_updated)

        # 5. Salary Slips Screen
        self.screens["salary_slips"] = self.create_salary_slips_screen()

        # 6. Reports Screen
        self.screens["reports"] = ReportsScreen(self.content_area)

        # 7. Settings / Demo Screen
        self.screens["settings"] = self.create_settings_screen()

    def on_data_updated(self):
        """Callback to refresh metrics across screens when records change."""
        self.refresh_dashboard()
        if hasattr(self.screens.get("reports"), "refresh_all"):
            self.screens["reports"].refresh_all()
        if hasattr(self.screens.get("attendance"), "refresh_employees_list"):
            self.screens["attendance"].refresh_employees_list()
        if hasattr(self.screens.get("salary"), "refresh_employees_list"):
            self.screens["salary"].refresh_employees_list()

    def show_screen(self, screen_key):
        # Update sidebar button active state
        for key, btn in self.nav_buttons.items():
            if key == "exit":
                continue
            if key == screen_key:
                btn.configure(bg="#1e3a8a", fg="#ffffff", font=("Segoe UI", 10, "bold"))
            else:
                btn.configure(bg="#0f172a", fg="#cbd5e1", font=("Segoe UI", 10))

        # Hide all screens
        for frame in self.screens.values():
            frame.pack_forget()

        # Show target screen
        if screen_key in self.screens:
            if screen_key == "dashboard":
                self.refresh_dashboard()
            elif screen_key == "salary_slips":
                self.load_slips_table()
            self.screens[screen_key].pack(fill=tk.BOTH, expand=True)

    # --------------------------------------------------------------------------
    # Dashboard Screen Implementation
    # --------------------------------------------------------------------------
    def create_dashboard_screen(self):
        dash_frame = tk.Frame(self.content_area, bg="#f8fafc")

        # Top welcome banner
        banner = tk.Frame(dash_frame, bg="#ffffff", height=70, relief=tk.RIDGE, bd=1)
        banner.pack(fill=tk.X, padx=20, pady=(20, 15))
        banner.pack_propagate(False)

        tk.Label(
            banner,
            text="Administrative Overview & Payroll Summary",
            font=("Segoe UI", 14, "bold"),
            fg="#1e293b",
            bg="#ffffff"
        ).pack(side=tk.LEFT, padx=20, pady=(12, 0))

        now = datetime.now()
        tk.Label(
            banner,
            text=f"Current Pay Period: {get_month_name(now.month)} {now.year}",
            font=("Segoe UI", 10),
            fg="#64748b",
            bg="#ffffff"
        ).pack(side=tk.LEFT, padx=20, pady=(16, 0))

        # 6 Statistical Metric Cards Grid
        cards_frame = tk.Frame(dash_frame, bg="#f8fafc")
        cards_frame.pack(fill=tk.X, padx=20, pady=5)

        self.card_vars = {
            "total_emp": tk.StringVar(value="0"),
            "active_emp": tk.StringVar(value="0"),
            "days_present": tk.StringVar(value="0"),
            "days_leave": tk.StringVar(value="0"),
            "total_salary": tk.StringVar(value="₹ 0.00"),
            "total_ot": tk.StringVar(value="0.0 hrs")
        }

        cards_spec = [
            ("TOTAL EMPLOYEES", self.card_vars["total_emp"], "#0284c7", "Registered staff count"),
            ("ACTIVE EMPLOYEES", self.card_vars["active_emp"], "#16a34a", "Eligible for payroll"),
            ("EMPLOYEES PRESENT", self.card_vars["days_present"], "#0d9488", f"Recorded for {get_month_name(now.month)}"),
            ("EMPLOYEES ON LEAVE", self.card_vars["days_leave"], "#ea580c", f"Leaves in {get_month_name(now.month)}"),
            ("TOTAL SALARY (MONTH)", self.card_vars["total_salary"], "#2563eb", f"Processed net for {get_month_name(now.month)}"),
            ("TOTAL OVERTIME", self.card_vars["total_ot"], "#7c3aed", "Logged overtime hours")
        ]

        for i, (title, var, accent_color, subtitle) in enumerate(cards_spec):
            r = i // 3
            c = i % 3

            card = tk.Frame(cards_frame, bg="#ffffff", relief=tk.SOLID, bd=1, padx=16, pady=12)
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

            # Colored accent stripe on top of card
            stripe = tk.Frame(card, bg=accent_color, height=3)
            stripe.pack(fill=tk.X, side=tk.TOP, pady=(0, 8))

            tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), fg="#64748b", bg="#ffffff").pack(anchor=tk.W)
            tk.Label(card, textvariable=var, font=("Segoe UI", 18, "bold"), fg="#1e293b", bg="#ffffff").pack(anchor=tk.W, pady=4)
            tk.Label(card, text=subtitle, font=("Segoe UI", 8), fg="#94a3b8", bg="#ffffff").pack(anchor=tk.W)

        for col_idx in range(3):
            cards_frame.columnconfigure(col_idx, weight=1)

        # Lower Section: Quick Actions & Recent Processed Records
        bottom_frame = tk.Frame(dash_frame, bg="#f8fafc")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Left: Quick Actions
        qa_frame = tk.LabelFrame(bottom_frame, text=" Quick Actions ", font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=15, pady=15)
        qa_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        actions = [
            ("➕ Add New Employee", lambda: self.show_screen("employees"), "#16a34a"),
            ("🕒 Mark Attendance", lambda: self.show_screen("attendance"), "#0284c7"),
            ("📥 Upload Excel & Calculate", lambda: self.show_screen("excel_upload"), "#059669"),
            ("💰 Process Monthly Salary", lambda: self.show_screen("salary"), "#2563eb"),
            ("📄 View / Print Salary Slips", lambda: self.show_screen("salary_slips"), "#7c3aed"),
            ("📊 View Reports & Analytics", lambda: self.show_screen("reports"), "#0891b2"),
            ("📥 Load AIET Demo Records", self.quick_insert_sample_data, "#475569"),
        ]

        for text, cmd, color in actions:
            btn = tk.Button(
                qa_frame,
                text=text,
                font=("Segoe UI", 9, "bold"),
                bg=color,
                fg="#ffffff",
                relief=tk.FLAT,
                padx=12,
                pady=6,
                cursor="hand2",
                command=cmd
            )
            btn.pack(fill=tk.X, pady=4)

        # Right: Overview of AIET Departments and Recent Salaries
        right_frame = tk.LabelFrame(bottom_frame, text=" Departmental Headcount Summary ", font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=15, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.dash_tree = ttk.Treeview(right_frame, columns=("dept", "count"), show="headings", height=8)
        self.dash_tree.heading("dept", text="Department")
        self.dash_tree.heading("count", text="Total Employees")
        self.dash_tree.column("dept", width=320, anchor=tk.W)
        self.dash_tree.column("count", width=120, anchor=tk.CENTER)
        self.dash_tree.pack(fill=tk.BOTH, expand=True)

        return dash_frame

    def refresh_dashboard(self):
        """Query models and refresh all cards and departmental treeview."""
        metrics = models.get_dashboard_metrics()

        self.card_vars["total_emp"].set(str(metrics["total_employees"]))
        self.card_vars["active_emp"].set(str(metrics["active_employees"]))
        self.card_vars["days_present"].set(str(metrics["total_days_present"]))
        self.card_vars["days_leave"].set(str(metrics["total_leave_days"]))
        self.card_vars["total_salary"].set(format_currency(metrics["total_monthly_salary"]))
        self.card_vars["total_ot"].set(f"{metrics['total_overtime_hours']:.1f} hrs")

        # Refresh departments tree
        for item in self.dash_tree.get_children():
            self.dash_tree.delete(item)

        for d in metrics["department_breakdown"]:
            self.dash_tree.insert("", tk.END, values=(d["department"], d["count"]))

    def quick_insert_sample_data(self):
        count = database.insert_sample_data()
        messagebox.showinfo(
            "Demo Data Ready",
            f"Successfully checked and loaded sample AIET records ({count} added/updated).\n"
            "Dashboard, employees, attendance, and salary screens are now populated."
        )
        self.on_data_updated()

    # --------------------------------------------------------------------------
    # Salary Slips Screen Implementation
    # --------------------------------------------------------------------------
    def create_salary_slips_screen(self):
        slip_frame = tk.Frame(self.content_area, bg="#f8fafc")

        header = tk.Frame(slip_frame, bg="#1e3a8a", height=50)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Employee Salary Slips & PDF Dispatch — AIET",
            font=("Segoe UI", 13, "bold"),
            bg="#1e3a8a",
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=10)

        main_box = ttk.Frame(slip_frame, padding=15)
        main_box.pack(fill=tk.BOTH, expand=True)

        # Control Bar
        bar = ttk.Frame(main_box)
        bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(bar, text="Filter by Period:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        now = datetime.now()
        self.var_slip_month = tk.StringVar(value=f"{now.month} - {get_month_name(now.month)}")
        opts = ["All"] + [f"{i} - {get_month_name(i)}" for i in range(1, 13)]
        self.combo_slip_m = ttk.Combobox(bar, textvariable=self.var_slip_month, values=opts, state="readonly", width=14, font=("Segoe UI", 9))
        self.combo_slip_m.pack(side=tk.LEFT, padx=(0, 8))

        self.var_slip_year = tk.StringVar(value=str(now.year))
        spin_y = ttk.Spinbox(bar, from_=2020, to=2035, textvariable=self.var_slip_year, width=6, font=("Segoe UI", 9))
        spin_y.pack(side=tk.LEFT, padx=(0, 8))

        btn_filt = tk.Button(bar, text="Filter", bg="#0284c7", fg="white", font=("Segoe UI", 9),
                             relief=tk.FLAT, padx=10, pady=2, cursor="hand2", command=self.load_slips_table)
        btn_filt.pack(side=tk.LEFT, padx=3)

        btn_gen_single = tk.Button(bar, text="📄 Generate PDF Slip for Selected", bg="#7c3aed", fg="white", font=("Segoe UI", 9, "bold"),
                                   relief=tk.FLAT, padx=12, pady=2, cursor="hand2", command=self.generate_selected_slip)
        btn_gen_single.pack(side=tk.LEFT, padx=8)

        btn_open_folder = tk.Button(bar, text="📁 Open Slips Folder", bg="#475569", fg="white", font=("Segoe UI", 9),
                                    relief=tk.FLAT, padx=10, pady=2, cursor="hand2", command=self.open_slips_folder)
        btn_open_folder.pack(side=tk.LEFT, padx=3)

        # Table
        tree_container = ttk.Frame(main_box)
        tree_container.pack(fill=tk.BOTH, expand=True)

        cols = ("emp_id", "name", "dept", "designation", "period", "gross", "deduct", "net")
        self.tree_slips = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")

        self.tree_slips.heading("emp_id", text="Emp ID")
        self.tree_slips.heading("name", text="Employee Name")
        self.tree_slips.heading("dept", text="Department")
        self.tree_slips.heading("designation", text="Designation")
        self.tree_slips.heading("period", text="Pay Period")
        self.tree_slips.heading("gross", text="Gross Salary")
        self.tree_slips.heading("deduct", text="Deductions")
        self.tree_slips.heading("net", text="Net Payable")

        self.tree_slips.column("emp_id", width=95, anchor=tk.W)
        self.tree_slips.column("name", width=150, anchor=tk.W)
        self.tree_slips.column("dept", width=150, anchor=tk.W)
        self.tree_slips.column("designation", width=130, anchor=tk.W)
        self.tree_slips.column("period", width=110, anchor=tk.CENTER)
        self.tree_slips.column("gross", width=100, anchor=tk.E)
        self.tree_slips.column("deduct", width=100, anchor=tk.E)
        self.tree_slips.column("net", width=110, anchor=tk.E)

        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree_slips.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree_slips.xview)
        self.tree_slips.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree_slips.grid(row=0, column=0, sticky=tk.NSEW)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        return slip_frame

    def load_slips_table(self):
        for item in self.tree_slips.get_children():
            self.tree_slips.delete(item)

        m_str = self.var_slip_month.get()
        y_str = self.var_slip_year.get().strip()

        m_val = int(m_str.split(" - ")[0]) if m_str != "All" else None
        y_val = int(y_str) if y_str.isdigit() else None

        records = models.get_all_salary_records(m_val, y_val)
        for r in records:
            m_name = get_month_name(r["month"])
            self.tree_slips.insert("", tk.END, values=(
                r["employee_id"],
                r["name"],
                r["department"],
                r["designation"],
                f"{m_name} {r['year']}",
                format_currency(r["gross_salary"]),
                format_currency(r["deductions"]),
                format_currency(r["net_salary"])
            ))

    def generate_selected_slip(self):
        selected = self.tree_slips.selection()
        if not selected:
            messagebox.showwarning("Select Employee", "Please select a salary record from the list to generate its PDF slip.")
            return

        vals = self.tree_slips.item(selected[0])["values"]
        emp_id = vals[0]
        period_parts = str(vals[4]).split()

        m_num = datetime.now().month
        y_num = datetime.now().year
        if len(period_parts) == 2:
            import calendar
            for idx, name in enumerate(calendar.month_name):
                if name.lower() == period_parts[0].lower():
                    m_num = idx
                    break
            if period_parts[1].isdigit():
                y_num = int(period_parts[1])

        rec = models.get_salary_record(emp_id, m_num, y_num)
        if not rec:
            messagebox.showerror("Error", "Could not retrieve salary record from database.")
            return

        success, path = generate_salary_slip_pdf(rec)
        if success:
            messagebox.showinfo("PDF Generated", f"Official salary slip generated:\n\n{path}")
            try:
                os.startfile(path)
            except Exception:
                pass
        else:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{path}")

    def open_slips_folder(self):
        folder = get_salary_slips_dir()
        try:
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", folder])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showinfo("Folder Path", f"Salary slips are saved in:\n{folder}")

    # --------------------------------------------------------------------------
    # Settings / Demo Screen Implementation
    # --------------------------------------------------------------------------
    def create_settings_screen(self):
        settings_frame = tk.Frame(self.content_area, bg="#f8fafc")

        header = tk.Frame(settings_frame, bg="#1e3a8a", height=50)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="System Settings & Demonstration Tools — AIET",
            font=("Segoe UI", 13, "bold"),
            bg="#1e3a8a",
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=10)

        main_box = ttk.Frame(settings_frame, padding=25)
        main_box.pack(fill=tk.BOTH, expand=True)

        # Demo Data Management Box
        demo_box = ttk.LabelFrame(main_box, text=" Demonstration & Testing Data ", padding=20)
        demo_box.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(
            demo_box,
            text="Load realistic sample faculty and staff records for Alvas Institute of Engineering and Technology.\n"
                 "Includes departments like CSE, ISE, ECE, ME, AIML, Administration with attendance and processed salary slips.",
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W, pady=(0, 15))

        btn_box = ttk.Frame(demo_box)
        btn_box.pack(fill=tk.X)

        tk.Button(
            btn_box,
            text="📥 Insert AIET Sample Demonstration Data",
            bg="#16a34a",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.quick_insert_sample_data
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            btn_box,
            text="⚠️ Clear All Attendance & Salary Records",
            bg="#dc2626",
            fg="white",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.clear_attendance_and_salaries
        ).pack(side=tk.LEFT)

        # System Information Box
        info_box = ttk.LabelFrame(main_box, text=" System & Academic Project Information ", padding=20)
        info_box.pack(fill=tk.BOTH, expand=True)

        system_details = [
            ("Project Name:", "Employee Attendance & Salary Processing System"),
            ("Institution:", "Alvas Institute of Engineering and Technology (AIET), Moodbidri"),
            ("Affiliation:", "Visvesvaraya Technological University (VTU), Belagavi"),
            ("Approved by:", "AICTE, New Delhi"),
            ("Technology Stack:", "Python 3, Tkinter & ttk, SQLite 3, openpyxl, ReportLab, Matplotlib"),
            ("Primary Calculations:", "Attendance Salary = (Basic / Working Days) × Days Present\n"
                                      "Overtime Pay = Overtime Hours × Overtime Rate\n"
                                      "Gross Salary = Attendance Salary + Overtime Pay + Allowances\n"
                                      "Net Salary = Gross Salary - Deductions"),
            ("Database Location:", database.get_db_path())
        ]

        for r, (k, v) in enumerate(system_details):
            ttk.Label(info_box, text=k, font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky=tk.NW, pady=4, padx=(0, 15))
            ttk.Label(info_box, text=v, font=("Segoe UI", 9)).grid(row=r, column=1, sticky=tk.W, pady=4)

        return settings_frame

    def clear_attendance_and_salaries(self):
        confirm = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to clear all monthly attendance and salary records?\n"
            "Employee profiles will be kept intact."
        )
        if confirm:
            conn = database.get_connection()
            conn.execute("DELETE FROM salary_records;")
            conn.execute("DELETE FROM attendance;")
            conn.commit()
            conn.close()
            messagebox.showinfo("Reset Complete", "Attendance and salary records cleared.")
            self.on_data_updated()

    def confirm_exit(self):
        if messagebox.askyesno("Exit Application", "Are you sure you want to exit the AIET Employee System?"):
            self.destroy()

def main():
    app = AIETApplication()
    app.mainloop()

if __name__ == "__main__":
    main()
