"""
Attendance Management Screen for AIET Employee Attendance & Salary Processing System.
Tkinter Frame handling Attendance logging, Overtime recording, and validations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import models
from utils import (
    validate_attendance_days,
    validate_positive_number,
    get_month_name
)

class AttendanceScreen(ttk.Frame):
    def __init__(self, parent, on_data_changed_callback=None):
        super().__init__(parent)
        self.on_data_changed_callback = on_data_changed_callback
        self.employees_map = {}  # "ID - Name" -> ID
        self.init_ui()
        self.refresh_employees_list()
        self.load_attendance()

    def init_ui(self):
        # Header banner
        header_frame = tk.Frame(self, bg="#1e3a8a", height=50)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(
            header_frame,
            text="Monthly Attendance & Overtime Tracker — AIET",
            font=("Segoe UI", 13, "bold"),
            bg="#1e3a8a",
            fg="white"
        )
        title_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        # Main Layout
        main_content = ttk.Frame(self, padding=15)
        main_content.pack(fill=tk.BOTH, expand=True)

        # Left Column: Attendance Form
        form_frame = ttk.LabelFrame(main_content, text=" Record Monthly Attendance ", padding=15)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        # Variables
        self.var_emp_selection = tk.StringVar()
        now = datetime.now()
        self.var_month = tk.IntVar(value=now.month)
        self.var_year = tk.IntVar(value=now.year)
        self.var_working_days = tk.StringVar(value="25")
        self.var_days_present = tk.StringVar(value="25")
        self.var_leave_days = tk.StringVar(value="0")
        self.var_ot_hours = tk.StringVar(value="0")

        # Form Controls
        row = 0

        # Employee Combobox
        ttk.Label(form_frame, text="Select Employee *:", font=("Segoe UI", 9)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.combo_employee = ttk.Combobox(form_frame, textvariable=self.var_emp_selection, width=28, font=("Segoe UI", 9))
        self.combo_employee.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.combo_employee.bind("<<ComboboxSelected>>", self.on_employee_combo_changed)
        row += 1

        # Month Combobox
        ttk.Label(form_frame, text="Month *:", font=("Segoe UI", 9)).grid(row=row, column=0, sticky=tk.W, pady=5)
        month_names = [f"{i} - {get_month_name(i)}" for i in range(1, 13)]
        self.combo_month = ttk.Combobox(form_frame, values=month_names, state="readonly", width=28, font=("Segoe UI", 9))
        self.combo_month.current(now.month - 1)
        self.combo_month.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.combo_month.bind("<<ComboboxSelected>>", self.on_month_year_changed)
        row += 1

        # Year Spinbox
        ttk.Label(form_frame, text="Year *:", font=("Segoe UI", 9)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.spin_year = ttk.Spinbox(form_frame, from_=2020, to=2035, textvariable=self.var_year, width=28, font=("Segoe UI", 9))
        self.spin_year.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.spin_year.bind("<KeyRelease>", lambda e: self.on_month_year_changed())
        row += 1

        # Total Working Days
        ttk.Label(form_frame, text="Total Working Days *:", font=("Segoe UI", 9)).grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_working_days, width=30, font=("Segoe UI", 9)).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Days Present
        ttk.Label(form_frame, text="Days Present *:", font=("Segoe UI", 9)).grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_days_present, width=30, font=("Segoe UI", 9)).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Leave Days
        ttk.Label(form_frame, text="Leave Days *:", font=("Segoe UI", 9)).grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_leave_days, width=30, font=("Segoe UI", 9)).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Overtime Hours
        ttk.Label(form_frame, text="Overtime Hours:", font=("Segoe UI", 9)).grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.var_ot_hours, width=30, font=("Segoe UI", 9)).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Information notice
        notice_lbl = tk.Label(
            form_frame,
            text="Rule: Days Present + Leave Days\nmust not exceed Total Working Days.",
            font=("Segoe UI", 8, "italic"),
            fg="#64748b",
            justify=tk.LEFT
        )
        notice_lbl.grid(row=row, column=0, columnspan=2, pady=(10, 5), sticky=tk.W)
        row += 1

        # Action Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=(15, 0), sticky=tk.EW)

        self.btn_save = tk.Button(btn_frame, text="Save / Update", bg="#16a34a", fg="white", font=("Segoe UI", 9, "bold"),
                                  relief=tk.FLAT, padx=10, pady=5, cursor="hand2", command=self.save_attendance)
        self.btn_save.pack(side=tk.LEFT, padx=3)

        self.btn_clear = tk.Button(btn_frame, text="Clear", bg="#64748b", fg="white", font=("Segoe UI", 9, "bold"),
                                   relief=tk.FLAT, padx=10, pady=5, cursor="hand2", command=self.clear_form)
        self.btn_clear.pack(side=tk.LEFT, padx=3)

        self.btn_delete = tk.Button(btn_frame, text="Delete", bg="#dc2626", fg="white", font=("Segoe UI", 9, "bold"),
                                    relief=tk.FLAT, padx=10, pady=5, cursor="hand2", command=self.delete_attendance)
        self.btn_delete.pack(side=tk.LEFT, padx=3)

        # Right Column: Filter + Treeview Table
        table_frame = ttk.Frame(main_content)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Filter bar
        filter_box = ttk.LabelFrame(table_frame, text=" Filter & Search Attendance ", padding=10)
        filter_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_box, text="Search:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.var_search = tk.StringVar()
        entry_search = ttk.Entry(filter_box, textvariable=self.var_search, width=18, font=("Segoe UI", 9))
        entry_search.pack(side=tk.LEFT, padx=(0, 8))
        entry_search.bind("<Return>", lambda e: self.search_attendance())

        ttk.Label(filter_box, text="Month:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.var_filter_month = tk.StringVar(value="All")
        month_filter_opts = ["All"] + [f"{i} - {get_month_name(i)}" for i in range(1, 13)]
        combo_filter_month = ttk.Combobox(filter_box, textvariable=self.var_filter_month, values=month_filter_opts, state="readonly", width=12, font=("Segoe UI", 9))
        combo_filter_month.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(filter_box, text="Year:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.var_filter_year = tk.StringVar(value=str(now.year))
        spin_filter_year = ttk.Spinbox(filter_box, from_=2020, to=2035, textvariable=self.var_filter_year, width=6, font=("Segoe UI", 9))
        spin_filter_year.pack(side=tk.LEFT, padx=(0, 8))

        btn_search = tk.Button(filter_box, text="Filter", bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"),
                               relief=tk.FLAT, padx=10, pady=2, cursor="hand2", command=self.search_attendance)
        btn_search.pack(side=tk.LEFT, padx=3)

        btn_reset = tk.Button(filter_box, text="Reset", bg="#475569", fg="white", font=("Segoe UI", 9),
                              relief=tk.FLAT, padx=8, pady=2, cursor="hand2", command=self.reset_filter)
        btn_reset.pack(side=tk.LEFT, padx=3)

        self.lbl_count = ttk.Label(filter_box, text="", font=("Segoe UI", 9, "italic"))
        self.lbl_count.pack(side=tk.RIGHT, padx=5)

        # Table Treeview
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("att_id", "emp_id", "name", "dept", "period", "working_days", "present", "leave", "ot_hours")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("att_id", text="ID")
        self.tree.heading("emp_id", text="Emp ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("dept", text="Department")
        self.tree.heading("period", text="Month / Year")
        self.tree.heading("working_days", text="Working Days")
        self.tree.heading("present", text="Present")
        self.tree.heading("leave", text="Leave")
        self.tree.heading("ot_hours", text="OT Hours")

        self.tree.column("att_id", width=40, anchor=tk.CENTER)
        self.tree.column("emp_id", width=95, anchor=tk.W)
        self.tree.column("name", width=140, anchor=tk.W)
        self.tree.column("dept", width=140, anchor=tk.W)
        self.tree.column("period", width=110, anchor=tk.CENTER)
        self.tree.column("working_days", width=90, anchor=tk.CENTER)
        self.tree.column("present", width=70, anchor=tk.CENTER)
        self.tree.column("leave", width=65, anchor=tk.CENTER)
        self.tree.column("ot_hours", width=80, anchor=tk.CENTER)

        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_attendance_selected)

    def refresh_employees_list(self):
        """Populate active employees into combobox."""
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

    def get_selected_emp_id(self):
        selected_text = self.var_emp_selection.get().strip()
        if selected_text in self.employees_map:
            return self.employees_map[selected_text]
        # In case the user typed just the ID
        return selected_text.split(" - ")[0].strip()

    def get_selected_month_number(self):
        idx = self.combo_month.current()
        return idx + 1 if idx >= 0 else datetime.now().month

    def on_employee_combo_changed(self, event=None):
        self.check_and_load_existing_record()

    def on_month_year_changed(self, event=None):
        self.check_and_load_existing_record()

    def check_and_load_existing_record(self):
        emp_id = self.get_selected_emp_id()
        if not emp_id:
            return
        m = self.get_selected_month_number()
        try:
            y = int(self.var_year.get())
        except (ValueError, TypeError):
            return

        rec = models.get_attendance(emp_id, m, y)
        if rec:
            self.var_working_days.set(str(rec["total_working_days"]))
            self.var_days_present.set(str(rec["days_present"]))
            self.var_leave_days.set(str(rec["leave_days"]))
            self.var_ot_hours.set(str(rec["overtime_hours"]))

    def load_attendance(self, month=None, year=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        records = models.get_all_attendance(month, year)
        for r in records:
            m_name = get_month_name(r["month"])
            self.tree.insert("", tk.END, values=(
                r["attendance_id"],
                r["employee_id"],
                r["name"],
                r["department"],
                f"{m_name} {r['year']}",
                r["total_working_days"],
                r["days_present"],
                r["leave_days"],
                r["overtime_hours"]
            ))

        self.lbl_count.config(text=f"Total: {len(records)} Records")

    def search_attendance(self):
        q = self.var_search.get().strip()
        m_filter = self.var_filter_month.get()
        y_filter = self.var_filter_year.get().strip()

        m_val = None
        if m_filter != "All":
            m_val = int(m_filter.split(" - ")[0])

        y_val = int(y_filter) if y_filter.isdigit() else None

        for item in self.tree.get_children():
            self.tree.delete(item)

        results = models.search_attendance(q, m_val, y_val)
        for r in results:
            m_name = get_month_name(r["month"])
            self.tree.insert("", tk.END, values=(
                r["attendance_id"],
                r["employee_id"],
                r["name"],
                r["department"],
                f"{m_name} {r['year']}",
                r["total_working_days"],
                r["days_present"],
                r["leave_days"],
                r["overtime_hours"]
            ))
        self.lbl_count.config(text=f"Found: {len(results)} Records")

    def reset_filter(self):
        self.var_search.set("")
        self.var_filter_month.set("All")
        self.var_filter_year.set(str(datetime.now().year))
        self.load_attendance()

    def on_attendance_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0])["values"]
        att_id, emp_id = vals[0], vals[1]

        # Find employee in dropdown
        for display_str, eid in self.employees_map.items():
            if eid == emp_id:
                self.var_emp_selection.set(display_str)
                break

        # Parse month & year from period string (e.g. "September 2024")
        period_parts = str(vals[4]).split()
        if len(period_parts) == 2:
            m_str, y_str = period_parts[0], period_parts[1]
            import calendar
            for i, name in enumerate(calendar.month_name):
                if name.lower() == m_str.lower():
                    self.combo_month.current(i - 1)
                    break
            if y_str.isdigit():
                self.var_year.set(int(y_str))

        self.var_working_days.set(str(vals[5]))
        self.var_days_present.set(str(vals[6]))
        self.var_leave_days.set(str(vals[7]))
        self.var_ot_hours.set(str(vals[8]))

    def save_attendance(self):
        emp_id = self.get_selected_emp_id()
        if not emp_id:
            messagebox.showerror("Validation Error", "Please select an employee.")
            return

        month = self.get_selected_month_number()
        try:
            year = int(self.var_year.get())
            if year < 2000 or year > 2099:
                messagebox.showerror("Validation Error", "Please enter a valid 4-digit year.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Year must be a valid integer.")
            return

        # Validate attendance days
        ok, msg = validate_attendance_days(
            self.var_working_days.get(),
            self.var_days_present.get(),
            self.var_leave_days.get()
        )
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return

        # Validate overtime hours
        ok, msg = validate_positive_number(self.var_ot_hours.get(), "Overtime Hours", allow_zero=True)
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return

        att_data = (
            emp_id,
            month,
            year,
            int(self.var_working_days.get().strip()),
            int(self.var_days_present.get().strip()),
            int(self.var_leave_days.get().strip()),
            float(self.var_ot_hours.get().strip() or 0.0)
        )

        success, msg = models.save_or_update_attendance(att_data)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_attendance()
            if self.on_data_changed_callback:
                self.on_data_changed_callback()
        else:
            messagebox.showerror("Error", msg)

    def delete_attendance(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Please select an attendance record from the table to delete.")
            return

        att_id = self.tree.item(selected[0])["values"][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this attendance record?")
        if confirm:
            success, msg = models.delete_attendance(att_id)
            if success:
                messagebox.showinfo("Deleted", "Attendance record deleted successfully.")
                self.clear_form()
                self.load_attendance()
                if self.on_data_changed_callback:
                    self.on_data_changed_callback()
            else:
                messagebox.showerror("Error", msg)

    def clear_form(self):
        now = datetime.now()
        self.combo_month.current(now.month - 1)
        self.var_year.set(now.year)
        self.var_working_days.set("25")
        self.var_days_present.set("25")
        self.var_leave_days.set("0")
        self.var_ot_hours.set("0")
        self.tree.selection_remove(self.tree.selection())
