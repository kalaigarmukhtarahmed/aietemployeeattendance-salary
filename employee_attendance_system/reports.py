"""
Reports and Visual Analytics Screen for AIET Employee Attendance & Salary Processing System.
Provides 4 standard reports with Excel export and embedded Matplotlib visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import models
from utils import format_currency, get_month_name
from excel_export import (
    export_employees_to_excel,
    export_attendance_to_excel,
    export_salary_report_to_excel
)

class ReportsScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Header banner
        header_frame = tk.Frame(self, bg="#1e3a8a", height=50)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(
            header_frame,
            text="Reports & Administrative Analytics — AIET",
            font=("Segoe UI", 13, "bold"),
            bg="#1e3a8a",
            fg="white"
        )
        title_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        # Notebook for Tabbed Reports
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Tab 1: Employee Directory Report
        self.tab_emp = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_emp, text=" 1. Employee Report ")
        self.build_employee_report_tab()

        # Tab 2: Monthly Attendance Report
        self.tab_att = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_att, text=" 2. Monthly Attendance Report ")
        self.build_attendance_report_tab()

        # Tab 3: Monthly Salary Payroll Report
        self.tab_sal = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_sal, text=" 3. Monthly Salary Report ")
        self.build_salary_report_tab()

        # Tab 4: Overtime Report & Charts
        self.tab_ot = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_ot, text=" 4. Overtime & Department Chart ")
        self.build_overtime_chart_tab()

    # --------------------------------------------------------------------------
    # 1. Employee Report Tab
    # --------------------------------------------------------------------------
    def build_employee_report_tab(self):
        ctrl_bar = ttk.Frame(self.tab_emp)
        ctrl_bar.pack(fill=tk.X, pady=(0, 10))

        btn_refresh = tk.Button(ctrl_bar, text="🔄 Refresh", bg="#0284c7", fg="white", font=("Segoe UI", 9),
                                relief=tk.FLAT, padx=10, pady=3, cursor="hand2", command=self.load_emp_report)
        btn_refresh.pack(side=tk.LEFT, padx=3)

        btn_export = tk.Button(ctrl_bar, text="📊 Export Employees to Excel", bg="#16a34a", fg="white", font=("Segoe UI", 9, "bold"),
                               relief=tk.FLAT, padx=12, pady=3, cursor="hand2", command=self.export_emp_excel)
        btn_export.pack(side=tk.LEFT, padx=8)

        self.lbl_emp_summary = ttk.Label(ctrl_bar, text="", font=("Segoe UI", 9, "italic"))
        self.lbl_emp_summary.pack(side=tk.RIGHT, padx=5)

        # Table
        tree_container = ttk.Frame(self.tab_emp)
        tree_container.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "name", "dept", "desig", "phone", "email", "joining", "basic", "ot_rate", "status")
        self.tree_emp = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")

        self.tree_emp.heading("id", text="Emp ID")
        self.tree_emp.heading("name", text="Name")
        self.tree_emp.heading("dept", text="Department")
        self.tree_emp.heading("desig", text="Designation")
        self.tree_emp.heading("phone", text="Phone")
        self.tree_emp.heading("email", text="Email")
        self.tree_emp.heading("joining", text="Joining Date")
        self.tree_emp.heading("basic", text="Basic Salary")
        self.tree_emp.heading("ot_rate", text="OT Rate")
        self.tree_emp.heading("status", text="Status")

        self.tree_emp.column("id", width=95, anchor=tk.W)
        self.tree_emp.column("name", width=140, anchor=tk.W)
        self.tree_emp.column("dept", width=150, anchor=tk.W)
        self.tree_emp.column("desig", width=140, anchor=tk.W)
        self.tree_emp.column("phone", width=100, anchor=tk.CENTER)
        self.tree_emp.column("email", width=150, anchor=tk.W)
        self.tree_emp.column("joining", width=90, anchor=tk.CENTER)
        self.tree_emp.column("basic", width=95, anchor=tk.E)
        self.tree_emp.column("ot_rate", width=80, anchor=tk.E)
        self.tree_emp.column("status", width=70, anchor=tk.CENTER)

        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree_emp.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree_emp.xview)
        self.tree_emp.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree_emp.grid(row=0, column=0, sticky=tk.NSEW)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.load_emp_report()

    def load_emp_report(self):
        for item in self.tree_emp.get_children():
            self.tree_emp.delete(item)

        emps = models.get_all_employees()
        active = 0
        for e in emps:
            if e["status"] == "Active":
                active += 1
            self.tree_emp.insert("", tk.END, values=(
                e["employee_id"], e["name"], e["department"], e["designation"],
                e["phone"], e["email"], e["joining_date"],
                format_currency(e["basic_salary"]),
                format_currency(e["overtime_rate"]),
                e["status"]
            ))

        self.lbl_emp_summary.config(text=f"Total: {len(emps)} Employees ({active} Active, {len(emps) - active} Inactive)")

    def export_emp_excel(self):
        success, path = export_employees_to_excel()
        if success:
            messagebox.showinfo("Export Successful", f"Employee report successfully exported to:\n{path}")
        else:
            messagebox.showerror("Export Failed", f"Could not export employee report:\n{path}")

    # --------------------------------------------------------------------------
    # 2. Attendance Report Tab
    # --------------------------------------------------------------------------
    def build_attendance_report_tab(self):
        ctrl_bar = ttk.Frame(self.tab_att)
        ctrl_bar.pack(fill=tk.X, pady=(0, 10))

        now = datetime.now()
        ttk.Label(ctrl_bar, text="Month:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.var_att_m = tk.StringVar(value=f"{now.month} - {get_month_name(now.month)}")
        opts = ["All"] + [f"{i} - {get_month_name(i)}" for i in range(1, 13)]
        self.combo_att_m = ttk.Combobox(ctrl_bar, textvariable=self.var_att_m, values=opts, state="readonly", width=12, font=("Segoe UI", 9))
        self.combo_att_m.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(ctrl_bar, text="Year:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.var_att_y = tk.StringVar(value=str(now.year))
        spin_y = ttk.Spinbox(ctrl_bar, from_=2020, to=2035, textvariable=self.var_att_y, width=6, font=("Segoe UI", 9))
        spin_y.pack(side=tk.LEFT, padx=(0, 8))

        btn_view = tk.Button(ctrl_bar, text="Filter", bg="#0284c7", fg="white", font=("Segoe UI", 9),
                             relief=tk.FLAT, padx=10, pady=2, cursor="hand2", command=self.load_att_report)
        btn_view.pack(side=tk.LEFT, padx=3)

        btn_export = tk.Button(ctrl_bar, text="📊 Export Attendance to Excel", bg="#16a34a", fg="white", font=("Segoe UI", 9, "bold"),
                               relief=tk.FLAT, padx=12, pady=2, cursor="hand2", command=self.export_att_excel)
        btn_export.pack(side=tk.LEFT, padx=8)

        self.lbl_att_summary = ttk.Label(ctrl_bar, text="", font=("Segoe UI", 9, "italic"))
        self.lbl_att_summary.pack(side=tk.RIGHT, padx=5)

        # Table
        tree_container = ttk.Frame(self.tab_att)
        tree_container.pack(fill=tk.BOTH, expand=True)

        cols = ("emp_id", "name", "dept", "period", "work_days", "present", "leave", "attendance_pct", "ot_hours")
        self.tree_att = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")

        self.tree_att.heading("emp_id", text="Emp ID")
        self.tree_att.heading("name", text="Name")
        self.tree_att.heading("dept", text="Department")
        self.tree_att.heading("period", text="Period")
        self.tree_att.heading("work_days", text="Working Days")
        self.tree_att.heading("present", text="Days Present")
        self.tree_att.heading("leave", text="Leave Days")
        self.tree_att.heading("attendance_pct", text="Attendance %")
        self.tree_att.heading("ot_hours", text="OT Hours")

        self.tree_att.column("emp_id", width=95, anchor=tk.W)
        self.tree_att.column("name", width=140, anchor=tk.W)
        self.tree_att.column("dept", width=150, anchor=tk.W)
        self.tree_att.column("period", width=105, anchor=tk.CENTER)
        self.tree_att.column("work_days", width=90, anchor=tk.CENTER)
        self.tree_att.column("present", width=90, anchor=tk.CENTER)
        self.tree_att.column("leave", width=80, anchor=tk.CENTER)
        self.tree_att.column("attendance_pct", width=90, anchor=tk.CENTER)
        self.tree_att.column("ot_hours", width=80, anchor=tk.CENTER)

        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree_att.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree_att.xview)
        self.tree_att.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree_att.grid(row=0, column=0, sticky=tk.NSEW)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.load_att_report()

    def load_att_report(self):
        for item in self.tree_att.get_children():
            self.tree_att.delete(item)

        m_str = self.var_att_m.get()
        y_str = self.var_att_y.get().strip()

        m_val = int(m_str.split(" - ")[0]) if m_str != "All" else None
        y_val = int(y_str) if y_str.isdigit() else None

        records = models.get_all_attendance(m_val, y_val)
        tot_present = 0
        tot_working = 0
        tot_ot = 0.0

        for r in records:
            work = r["total_working_days"]
            pres = r["days_present"]
            pct = round((pres / work) * 100, 1) if work > 0 else 0.0
            tot_present += pres
            tot_working += work
            tot_ot += r["overtime_hours"]

            self.tree_att.insert("", tk.END, values=(
                r["employee_id"], r["name"], r["department"],
                f"{get_month_name(r['month'])} {r['year']}",
                work, pres, r["leave_days"], f"{pct}%", r["overtime_hours"]
            ))

        overall_pct = round((tot_present / tot_working) * 100, 1) if tot_working > 0 else 0.0
        self.lbl_att_summary.config(text=f"Total: {len(records)} Records | Avg Attendance: {overall_pct}% | Total OT: {tot_ot:.1f} hrs")

    def export_att_excel(self):
        m_str = self.var_att_m.get()
        y_str = self.var_att_y.get().strip()
        m_val = int(m_str.split(" - ")[0]) if m_str != "All" else None
        y_val = int(y_str) if y_str.isdigit() else None

        success, path = export_attendance_to_excel(m_val, y_val)
        if success:
            messagebox.showinfo("Export Successful", f"Attendance report exported to:\n{path}")
        else:
            messagebox.showerror("Export Failed", f"Could not export attendance report:\n{path}")

    # --------------------------------------------------------------------------
    # 3. Monthly Salary Report Tab
    # --------------------------------------------------------------------------
    def build_salary_report_tab(self):
        ctrl_bar = ttk.Frame(self.tab_sal)
        ctrl_bar.pack(fill=tk.X, pady=(0, 10))

        now = datetime.now()
        ttk.Label(ctrl_bar, text="Month:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.var_sal_m = tk.StringVar(value=f"{now.month} - {get_month_name(now.month)}")
        opts = ["All"] + [f"{i} - {get_month_name(i)}" for i in range(1, 13)]
        self.combo_sal_m = ttk.Combobox(ctrl_bar, textvariable=self.var_sal_m, values=opts, state="readonly", width=12, font=("Segoe UI", 9))
        self.combo_sal_m.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(ctrl_bar, text="Year:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.var_sal_y = tk.StringVar(value=str(now.year))
        spin_y = ttk.Spinbox(ctrl_bar, from_=2020, to=2035, textvariable=self.var_sal_y, width=6, font=("Segoe UI", 9))
        spin_y.pack(side=tk.LEFT, padx=(0, 8))

        btn_view = tk.Button(ctrl_bar, text="Filter", bg="#0284c7", fg="white", font=("Segoe UI", 9),
                             relief=tk.FLAT, padx=10, pady=2, cursor="hand2", command=self.load_salary_report)
        btn_view.pack(side=tk.LEFT, padx=3)

        btn_export = tk.Button(ctrl_bar, text="📊 Export Salary Report to Excel", bg="#16a34a", fg="white", font=("Segoe UI", 9, "bold"),
                               relief=tk.FLAT, padx=12, pady=2, cursor="hand2", command=self.export_salary_excel)
        btn_export.pack(side=tk.LEFT, padx=8)

        self.lbl_sal_summary = ttk.Label(ctrl_bar, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_sal_summary.pack(side=tk.RIGHT, padx=5)

        # Table
        tree_container = ttk.Frame(self.tab_sal)
        tree_container.pack(fill=tk.BOTH, expand=True)

        cols = ("emp_id", "name", "dept", "period", "basic", "att_sal", "ot_pay", "allow", "gross", "deduct", "net")
        self.tree_sal = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")

        self.tree_sal.heading("emp_id", text="Emp ID")
        self.tree_sal.heading("name", text="Name")
        self.tree_sal.heading("dept", text="Department")
        self.tree_sal.heading("period", text="Period")
        self.tree_sal.heading("basic", text="Basic (₹)")
        self.tree_sal.heading("att_sal", text="Att. Salary (₹)")
        self.tree_sal.heading("ot_pay", text="OT Pay (₹)")
        self.tree_sal.heading("allow", text="Allowances (₹)")
        self.tree_sal.heading("gross", text="Gross (₹)")
        self.tree_sal.heading("deduct", text="Deductions (₹)")
        self.tree_sal.heading("net", text="Net Payable (₹)")

        self.tree_sal.column("emp_id", width=95, anchor=tk.W)
        self.tree_sal.column("name", width=130, anchor=tk.W)
        self.tree_sal.column("dept", width=140, anchor=tk.W)
        self.tree_sal.column("period", width=100, anchor=tk.CENTER)
        self.tree_sal.column("basic", width=85, anchor=tk.E)
        self.tree_sal.column("att_sal", width=90, anchor=tk.E)
        self.tree_sal.column("ot_pay", width=75, anchor=tk.E)
        self.tree_sal.column("allow", width=85, anchor=tk.E)
        self.tree_sal.column("gross", width=90, anchor=tk.E)
        self.tree_sal.column("deduct", width=85, anchor=tk.E)
        self.tree_sal.column("net", width=95, anchor=tk.E)

        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree_sal.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree_sal.xview)
        self.tree_sal.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree_sal.grid(row=0, column=0, sticky=tk.NSEW)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.load_salary_report()

    def load_salary_report(self):
        for item in self.tree_sal.get_children():
            self.tree_sal.delete(item)

        m_str = self.var_sal_m.get()
        y_str = self.var_sal_y.get().strip()

        m_val = int(m_str.split(" - ")[0]) if m_str != "All" else None
        y_val = int(y_str) if y_str.isdigit() else None

        records = models.get_all_salary_records(m_val, y_val)
        tot_net = 0.0

        for r in records:
            tot_net += float(r["net_salary"])
            self.tree_sal.insert("", tk.END, values=(
                r["employee_id"], r["name"], r["department"],
                f"{get_month_name(r['month'])} {r['year']}",
                f"{r['basic_salary']:,.2f}",
                f"{r['attendance_salary']:,.2f}",
                f"{r['overtime_pay']:,.2f}",
                f"{r['allowances']:,.2f}",
                f"{r['gross_salary']:,.2f}",
                f"{r['deductions']:,.2f}",
                f"{r['net_salary']:,.2f}"
            ))

        self.lbl_sal_summary.config(text=f"Total Payroll: {format_currency(tot_net)} ({len(records)} Processed)")

    def export_salary_excel(self):
        m_str = self.var_sal_m.get()
        y_str = self.var_sal_y.get().strip()
        m_val = int(m_str.split(" - ")[0]) if m_str != "All" else None
        y_val = int(y_str) if y_str.isdigit() else None

        success, path = export_salary_report_to_excel(m_val, y_val)
        if success:
            messagebox.showinfo("Export Successful", f"Salary report exported to:\n{path}")
        else:
            messagebox.showerror("Export Failed", f"Could not export salary report:\n{path}")

    # --------------------------------------------------------------------------
    # 4. Overtime Report & Embedded Matplotlib Visual Chart
    # --------------------------------------------------------------------------
    def build_overtime_chart_tab(self):
        paned = ttk.PanedWindow(self.tab_ot, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left sub-frame: Overtime records table
        left_frame = ttk.Frame(paned, padding=5)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Overtime Summary Table", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        ot_cols = ("emp_id", "name", "dept", "ot_hours", "ot_rate", "ot_pay")
        self.tree_ot = ttk.Treeview(left_frame, columns=ot_cols, show="headings", selectmode="browse")

        self.tree_ot.heading("emp_id", text="Emp ID")
        self.tree_ot.heading("name", text="Name")
        self.tree_ot.heading("dept", text="Department")
        self.tree_ot.heading("ot_hours", text="OT Hours")
        self.tree_ot.heading("ot_rate", text="Rate (₹/hr)")
        self.tree_ot.heading("ot_pay", text="OT Pay (₹)")

        self.tree_ot.column("emp_id", width=80, anchor=tk.W)
        self.tree_ot.column("name", width=120, anchor=tk.W)
        self.tree_ot.column("dept", width=130, anchor=tk.W)
        self.tree_ot.column("ot_hours", width=65, anchor=tk.CENTER)
        self.tree_ot.column("ot_rate", width=75, anchor=tk.E)
        self.tree_ot.column("ot_pay", width=80, anchor=tk.E)

        self.tree_ot.pack(fill=tk.BOTH, expand=True)

        # Right sub-frame: Matplotlib Chart
        self.right_chart_frame = ttk.Frame(paned, padding=5)
        paned.add(self.right_chart_frame, weight=1)

        ttk.Label(self.right_chart_frame, text="Staff Distribution by Department", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.chart_container = ttk.Frame(self.right_chart_frame)
        self.chart_container.pack(fill=tk.BOTH, expand=True)

        self.load_overtime_data()
        self.render_chart()

    def load_overtime_data(self):
        for item in self.tree_ot.get_children():
            self.tree_ot.delete(item)

        salary_recs = models.get_all_salary_records()
        for s in salary_recs:
            if float(s["overtime_hours"]) > 0:
                self.tree_ot.insert("", tk.END, values=(
                    s["employee_id"], s["name"], s["department"],
                    s["overtime_hours"],
                    format_currency(s["overtime_rate"]),
                    format_currency(s["overtime_pay"])
                ))

    def render_chart(self):
        """Render department distribution pie chart with Matplotlib."""
        for child in self.chart_container.winfo_children():
            child.destroy()

        try:
            import matplotlib
            matplotlib.use("TkAgg")
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            lbl = ttk.Label(self.chart_container, text="Matplotlib is not installed.\nRun: pip install matplotlib", font=("Segoe UI", 9, "italic"))
            lbl.pack(expand=True)
            return

        dept_data = models.get_dashboard_metrics()["department_breakdown"]
        if not dept_data:
            lbl = ttk.Label(self.chart_container, text="No department data available to plot.", font=("Segoe UI", 9, "italic"))
            lbl.pack(expand=True)
            return

        labels = [d["department"].replace(" & ", "\n& ") for d in dept_data]
        counts = [d["count"] for d in dept_data]
        colors = ['#1e3a8a', '#0284c7', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#64748b']

        fig = Figure(figsize=(5, 4), dpi=90)
        fig.patch.set_facecolor('#f8fafc')
        ax = fig.add_subplot(111)

        ax.pie(
            counts,
            labels=labels,
            autopct='%1.0f%%',
            startangle=140,
            colors=colors[:len(labels)],
            textprops={'fontsize': 8}
        )
        ax.set_title("AIET Staff Headcount by Department", fontsize=10, fontweight='bold', color="#1e293b", pad=10)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh_all(self):
        self.load_emp_report()
        self.load_att_report()
        self.load_salary_report()
        self.load_overtime_data()
        self.render_chart()
