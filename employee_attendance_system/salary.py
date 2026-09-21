"""
Salary Processing Screen for AIET Employee Attendance & Salary Processing System.
Handles automatic payroll calculation based on attendance, overtime, allowances, and deductions.
Calculated fields are strictly read-only to prevent tampering.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import models
from utils import format_currency, get_month_name
from pdf_generator import generate_salary_slip_pdf

class SalaryScreen(ttk.Frame):
    def __init__(self, parent, on_data_changed_callback=None):
        super().__init__(parent)
        self.on_data_changed_callback = on_data_changed_callback
        self.employees_map = {}
        self.calculated_cache = None

        self.init_ui()
        self.refresh_employees_list()
        self.load_salary_records()

    def init_ui(self):
        # Header banner
        header_frame = tk.Frame(self, bg="#1e3a8a", height=50)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(
            header_frame,
            text="Salary Processing & Payroll Engine — AIET",
            font=("Segoe UI", 13, "bold"),
            bg="#1e3a8a",
            fg="white"
        )
        title_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        # Main Layout
        main_content = ttk.Frame(self, padding=15)
        main_content.pack(fill=tk.BOTH, expand=True)

        # Left Column: Selection & Calculation Panel
        left_panel = ttk.Frame(main_content)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 15), expand=False)

        # 1. Selection Box
        sel_box = ttk.LabelFrame(left_panel, text=" Select Employee & Pay Period ", padding=12)
        sel_box.pack(fill=tk.X, pady=(0, 10))

        now = datetime.now()
        self.var_emp_selection = tk.StringVar()
        self.var_month = tk.IntVar(value=now.month)
        self.var_year = tk.IntVar(value=now.year)

        ttk.Label(sel_box, text="Employee *:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.combo_employee = ttk.Combobox(sel_box, textvariable=self.var_emp_selection, width=28, font=("Segoe UI", 9))
        self.combo_employee.grid(row=0, column=1, sticky=tk.W, pady=3)
        self.combo_employee.bind("<<ComboboxSelected>>", self.on_selection_changed)

        ttk.Label(sel_box, text="Month *:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky=tk.W, pady=3)
        month_names = [f"{i} - {get_month_name(i)}" for i in range(1, 13)]
        self.combo_month = ttk.Combobox(sel_box, values=month_names, state="readonly", width=28, font=("Segoe UI", 9))
        self.combo_month.current(now.month - 1)
        self.combo_month.grid(row=1, column=1, sticky=tk.W, pady=3)
        self.combo_month.bind("<<ComboboxSelected>>", self.on_selection_changed)

        ttk.Label(sel_box, text="Year *:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky=tk.W, pady=3)
        self.spin_year = ttk.Spinbox(sel_box, from_=2020, to=2035, textvariable=self.var_year, width=28, font=("Segoe UI", 9))
        self.spin_year.grid(row=2, column=1, sticky=tk.W, pady=3)
        self.spin_year.bind("<KeyRelease>", lambda e: self.on_selection_changed())

        # 2. Information & Calculations Panel
        calc_box = ttk.LabelFrame(left_panel, text=" Salary Breakdown & Calculation ", padding=12)
        calc_box.pack(fill=tk.BOTH, expand=True)

        # Variables for display
        self.lbl_val_id = tk.StringVar(value="-")
        self.lbl_val_name = tk.StringVar(value="-")
        self.lbl_val_dept = tk.StringVar(value="-")
        self.lbl_val_basic = tk.StringVar(value="₹ 0.00")
        self.lbl_val_work_days = tk.StringVar(value="0")
        self.lbl_val_present = tk.StringVar(value="0")
        self.lbl_val_leave = tk.StringVar(value="0")
        self.lbl_val_ot_hrs = tk.StringVar(value="0.0")
        self.lbl_val_ot_rate = tk.StringVar(value="₹ 0.00")

        # Calculated outputs (Read Only)
        self.lbl_val_att_sal = tk.StringVar(value="₹ 0.00")
        self.lbl_val_ot_pay = tk.StringVar(value="₹ 0.00")
        self.lbl_val_allowances = tk.StringVar(value="₹ 0.00")
        self.lbl_val_gross = tk.StringVar(value="₹ 0.00")
        self.lbl_val_deductions = tk.StringVar(value="₹ 0.00")
        self.lbl_val_net = tk.StringVar(value="₹ 0.00")

        grid_items = [
            ("Employee ID:", self.lbl_val_id, "#1e293b", False),
            ("Employee Name:", self.lbl_val_name, "#1e293b", False),
            ("Department:", self.lbl_val_dept, "#1e293b", False),
            ("Basic Salary:", self.lbl_val_basic, "#1e293b", False),
            ("Total Working Days:", self.lbl_val_work_days, "#1e293b", False),
            ("Days Present:", self.lbl_val_present, "#15803d", True),
            ("Leave Days:", self.lbl_val_leave, "#b91c1c", False),
            ("Overtime Hours:", self.lbl_val_ot_hrs, "#1e293b", False),
            ("Overtime Rate:", self.lbl_val_ot_rate, "#1e293b", False),
            ("------------------------", None, "#cbd5e1", False),
            ("Attendance Salary:", self.lbl_val_att_sal, "#0369a1", True),
            ("Overtime Pay:", self.lbl_val_ot_pay, "#0369a1", True),
            ("Allowances (+):", self.lbl_val_allowances, "#15803d", False),
            ("Gross Salary:", self.lbl_val_gross, "#1e3a8a", True),
            ("Deductions (-):", self.lbl_val_deductions, "#b91c1c", False),
            ("Net Payable Salary:", self.lbl_val_net, "#15803d", True),
        ]

        r = 0
        for label_text, var, color, is_bold in grid_items:
            if var is None:
                div = ttk.Separator(calc_box, orient=tk.HORIZONTAL)
                div.grid(row=r, column=0, columnspan=2, sticky=tk.EW, pady=6)
            else:
                font_desc = ("Segoe UI", 9, "bold" if is_bold else "normal")
                lbl_tag = ttk.Label(calc_box, text=label_text, font=font_desc)
                lbl_tag.grid(row=r, column=0, sticky=tk.W, pady=2)

                val_tag = tk.Label(calc_box, textvariable=var, font=font_desc, fg=color, anchor=tk.E)
                val_tag.grid(row=r, column=1, sticky=tk.E, pady=2, padx=(15, 0))
            r += 1

        # Prominent Action Buttons
        btn_box = ttk.Frame(calc_box)
        btn_box.grid(row=r, column=0, columnspan=2, pady=(15, 0), sticky=tk.EW)

        # Prominent Calculate Salary button
        self.btn_calculate = tk.Button(
            btn_box,
            text="⚙ Calculate Salary",
            bg="#2563eb",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.calculate_salary
        )
        self.btn_calculate.pack(fill=tk.X, pady=2)

        # Save record button
        self.btn_save = tk.Button(
            btn_box,
            text="💾 Save Salary Record",
            bg="#16a34a",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.save_salary
        )
        self.btn_save.pack(fill=tk.X, pady=2)

        # Generate slip button
        self.btn_slip = tk.Button(
            btn_box,
            text="📄 Generate PDF Salary Slip",
            bg="#7c3aed",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.generate_slip
        )
        self.btn_slip.pack(fill=tk.X, pady=2)

        # Right Column: History of Processed Salaries
        right_panel = ttk.Frame(main_content)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        hist_box = ttk.LabelFrame(right_panel, text=" Processed Monthly Salary Records ", padding=10)
        hist_box.pack(fill=tk.BOTH, expand=True)

        # Filter bar
        filt_frame = ttk.Frame(hist_box)
        filt_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(filt_frame, text="Filter Period:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.var_filter_month = tk.StringVar(value=f"{now.month} - {get_month_name(now.month)}")
        filter_months = ["All"] + [f"{i} - {get_month_name(i)}" for i in range(1, 13)]
        combo_filter = ttk.Combobox(filt_frame, textvariable=self.var_filter_month, values=filter_months, state="readonly", width=14, font=("Segoe UI", 9))
        combo_filter.pack(side=tk.LEFT, padx=(0, 8))

        self.var_filter_year = tk.StringVar(value=str(now.year))
        spin_yr = ttk.Spinbox(filt_frame, from_=2020, to=2035, textvariable=self.var_filter_year, width=6, font=("Segoe UI", 9))
        spin_yr.pack(side=tk.LEFT, padx=(0, 8))

        btn_filter = tk.Button(filt_frame, text="Filter", bg="#0284c7", fg="white", font=("Segoe UI", 9),
                               relief=tk.FLAT, padx=8, pady=1, cursor="hand2", command=self.apply_history_filter)
        btn_filter.pack(side=tk.LEFT, padx=2)

        btn_reset = tk.Button(filt_frame, text="Show All", bg="#64748b", fg="white", font=("Segoe UI", 9),
                              relief=tk.FLAT, padx=8, pady=1, cursor="hand2", command=self.load_salary_records)
        btn_reset.pack(side=tk.LEFT, padx=2)

        # Table
        tree_container = ttk.Frame(hist_box)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("emp_id", "name", "dept", "period", "basic", "att_sal", "ot_pay", "gross", "deduct", "net")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("emp_id", text="Emp ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("dept", text="Department")
        self.tree.heading("period", text="Period")
        self.tree.heading("basic", text="Basic (₹)")
        self.tree.heading("att_sal", text="Att. Sal (₹)")
        self.tree.heading("ot_pay", text="OT Pay (₹)")
        self.tree.heading("gross", text="Gross (₹)")
        self.tree.heading("deduct", text="Deductions (₹)")
        self.tree.heading("net", text="Net Salary (₹)")

        self.tree.column("emp_id", width=95, anchor=tk.W)
        self.tree.column("name", width=130, anchor=tk.W)
        self.tree.column("dept", width=130, anchor=tk.W)
        self.tree.column("period", width=100, anchor=tk.CENTER)
        self.tree.column("basic", width=85, anchor=tk.E)
        self.tree.column("att_sal", width=85, anchor=tk.E)
        self.tree.column("ot_pay", width=75, anchor=tk.E)
        self.tree.column("gross", width=90, anchor=tk.E)
        self.tree.column("deduct", width=85, anchor=tk.E)
        self.tree.column("net", width=95, anchor=tk.E)

        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_salary_row_selected)

    def refresh_employees_list(self):
        active_emps = models.get_active_employees()
        self.employees_map.clear()
        options = []
        for emp in active_emps:
            display_str = f"{emp['employee_id']} - {emp['name']}"
            self.employees_map[display_str] = emp['employee_id']
            options.append(display_str)

        self.combo_employee["values"] = options
        if options and not self.var_emp_selection.get():
            self.combo_employee.current(0)
            self.on_selection_changed()

    def get_selected_emp_id(self):
        selected_text = self.var_emp_selection.get().strip()
        if selected_text in self.employees_map:
            return self.employees_map[selected_text]
        return selected_text.split(" - ")[0].strip()

    def get_selected_month_number(self):
        idx = self.combo_month.current()
        return idx + 1 if idx >= 0 else datetime.now().month

    def on_selection_changed(self, event=None):
        """Fetch employee details and attendance record when user changes dropdown."""
        emp_id = self.get_selected_emp_id()
        if not emp_id:
            return

        emp = models.get_employee(emp_id)
        if not emp:
            return

        self.lbl_val_id.set(emp["employee_id"])
        self.lbl_val_name.set(emp["name"])
        self.lbl_val_dept.set(emp["department"])
        self.lbl_val_basic.set(format_currency(emp["basic_salary"]))
        self.lbl_val_ot_rate.set(format_currency(emp["overtime_rate"]))
        self.lbl_val_allowances.set(format_currency(emp["allowances"]))
        self.lbl_val_deductions.set(format_currency(emp["deductions"]))

        m = self.get_selected_month_number()
        try:
            y = int(self.var_year.get())
        except (ValueError, TypeError):
            y = datetime.now().year

        att = models.get_attendance(emp_id, m, y)
        if att:
            self.lbl_val_work_days.set(str(att["total_working_days"]))
            self.lbl_val_present.set(str(att["days_present"]))
            self.lbl_val_leave.set(str(att["leave_days"]))
            self.lbl_val_ot_hrs.set(str(att["overtime_hours"]))
        else:
            self.lbl_val_work_days.set("Not Recorded")
            self.lbl_val_present.set("0")
            self.lbl_val_leave.set("0")
            self.lbl_val_ot_hrs.set("0.0")

        # Check if already processed
        sal_rec = models.get_salary_record(emp_id, m, y)
        if sal_rec:
            self.lbl_val_att_sal.set(format_currency(sal_rec["attendance_salary"]))
            self.lbl_val_ot_pay.set(format_currency(sal_rec["overtime_pay"]))
            self.lbl_val_gross.set(format_currency(sal_rec["gross_salary"]))
            self.lbl_val_net.set(format_currency(sal_rec["net_salary"]))
            self.calculated_cache = sal_rec
        else:
            self.lbl_val_att_sal.set("₹ 0.00")
            self.lbl_val_ot_pay.set("₹ 0.00")
            self.lbl_val_gross.set("₹ 0.00")
            self.lbl_val_net.set("₹ 0.00")
            self.calculated_cache = None

    def calculate_salary(self):
        emp_id = self.get_selected_emp_id()
        if not emp_id:
            messagebox.showerror("Error", "Please select an employee.")
            return

        emp = models.get_employee(emp_id)
        if not emp:
            messagebox.showerror("Error", "Employee record not found.")
            return

        m = self.get_selected_month_number()
        try:
            y = int(self.var_year.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid year.")
            return

        att = models.get_attendance(emp_id, m, y)
        if not att:
            messagebox.showwarning(
                "Missing Attendance",
                f"No attendance record found for {emp['name']} for {get_month_name(m)} {y}.\n"
                "Please go to the Attendance screen and record attendance first."
            )
            return

        # Perform exact calculations
        comps = models.calculate_salary_components(
            basic_salary=emp["basic_salary"],
            total_working_days=att["total_working_days"],
            days_present=att["days_present"],
            overtime_hours=att["overtime_hours"],
            overtime_rate=emp["overtime_rate"],
            allowances=emp["allowances"],
            deductions=emp["deductions"]
        )

        self.lbl_val_att_sal.set(format_currency(comps["attendance_salary"]))
        self.lbl_val_ot_pay.set(format_currency(comps["overtime_pay"]))
        self.lbl_val_allowances.set(format_currency(comps["allowances"]))
        self.lbl_val_gross.set(format_currency(comps["gross_salary"]))
        self.lbl_val_deductions.set(format_currency(comps["deductions"]))
        self.lbl_val_net.set(format_currency(comps["net_salary"]))

        self.calculated_cache = {
            "employee_id": emp_id,
            "name": emp["name"],
            "department": emp["department"],
            "designation": emp["designation"],
            "phone": emp["phone"],
            "email": emp["email"],
            "month": m,
            "year": y,
            "leave_days": att["leave_days"],
            **comps
        }

        messagebox.showinfo(
            "Calculation Complete",
            f"Salary calculated for {emp['name']} ({get_month_name(m)} {y}):\n\n"
            f"Attendance Salary: {format_currency(comps['attendance_salary'])}\n"
            f"Overtime Pay:      {format_currency(comps['overtime_pay'])}\n"
            f"Allowances:        {format_currency(comps['allowances'])}\n"
            f"Gross Salary:      {format_currency(comps['gross_salary'])}\n"
            f"Deductions:        {format_currency(comps['deductions'])}\n"
            f"----------------------------------------\n"
            f"Net Payable Salary: {format_currency(comps['net_salary'])}\n\n"
            "Click 'Save Salary Record' to store in the database."
        )

    def save_salary(self):
        if not self.calculated_cache:
            messagebox.showwarning("Calculate First", "Please click 'Calculate Salary' before saving.")
            return

        success, msg = models.save_or_update_salary_record(self.calculated_cache)
        if success:
            messagebox.showinfo("Saved", msg)
            self.load_salary_records()
            if self.on_data_changed_callback:
                self.on_data_changed_callback()
        else:
            messagebox.showerror("Error", msg)

    def generate_slip(self):
        if not self.calculated_cache:
            messagebox.showwarning("Calculate First", "Please calculate or select a processed salary first.")
            return

        emp_id = self.calculated_cache["employee_id"]
        m = self.calculated_cache["month"]
        y = self.calculated_cache["year"]

        # Ensure complete record with employee info
        rec = models.get_salary_record(emp_id, m, y)
        data = rec if rec else self.calculated_cache

        success, pdf_path = generate_salary_slip_pdf(data)
        if success:
            msg = f"Salary Slip PDF generated successfully!\n\nSaved to:\n{pdf_path}"
            messagebox.showinfo("PDF Generated", msg)
            # Try to open with default system viewer on Windows
            import os
            try:
                os.startfile(pdf_path)
            except Exception:
                pass
        else:
            messagebox.showerror("PDF Generation Notice", f"Unable to generate PDF:\n{pdf_path}")

    def load_salary_records(self, month=None, year=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        records = models.get_all_salary_records(month, year)
        for r in records:
            m_name = get_month_name(r["month"])
            self.tree.insert("", tk.END, values=(
                r["employee_id"],
                r["name"],
                r["department"],
                f"{m_name} {r['year']}",
                f"{r['basic_salary']:,.2f}",
                f"{r['attendance_salary']:,.2f}",
                f"{r['overtime_pay']:,.2f}",
                f"{r['gross_salary']:,.2f}",
                f"{r['deductions']:,.2f}",
                f"{r['net_salary']:,.2f}"
            ))

    def apply_history_filter(self):
        m_str = self.var_filter_month.get()
        y_str = self.var_filter_year.get().strip()

        m_val = None
        if m_str != "All":
            m_val = int(m_str.split(" - ")[0])

        y_val = int(y_str) if y_str.isdigit() else None
        self.load_salary_records(m_val, y_val)

    def on_salary_row_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0])["values"]
        emp_id = vals[0]
        period_parts = str(vals[3]).split()

        for display_str, eid in self.employees_map.items():
            if eid == emp_id:
                self.var_emp_selection.set(display_str)
                break

        if len(period_parts) == 2:
            import calendar
            for i, name in enumerate(calendar.month_name):
                if name.lower() == period_parts[0].lower():
                    self.combo_month.current(i - 1)
                    break
            if period_parts[1].isdigit():
                self.var_year.set(int(period_parts[1]))

        self.on_selection_changed()
