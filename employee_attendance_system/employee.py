"""
Employee Management Screen for AIET Employee Attendance & Salary Processing System.
Tkinter Frame handling Employee CRUD, search, and Treeview display.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import models
from utils import (
    validate_employee_id,
    validate_phone,
    validate_email,
    validate_date,
    validate_positive_number,
    format_currency
)

class EmployeeScreen(ttk.Frame):
    def __init__(self, parent, on_data_changed_callback=None):
        super().__init__(parent)
        self.on_data_changed_callback = on_data_changed_callback

        self.departments = [
            "Computer Science & Eng",
            "Information Science & Eng",
            "Electronics & Communication",
            "Mechanical Engineering",
            "Civil Engineering",
            "Artificial Intelligence & ML",
            "Basic Science & Humanities",
            "Administration"
        ]

        self.designations = [
            "Professor & HOD",
            "Professor",
            "Associate Professor",
            "Assistant Professor",
            "Lab Instructor",
            "Administrative Officer",
            "Office Assistant",
            "Accountant",
            "System Administrator"
        ]

        self.init_ui()
        self.load_employees()

    def init_ui(self):
        # Header banner
        header_frame = tk.Frame(self, bg="#1e3a8a", height=50)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(
            header_frame,
            text="Employee Management — Alvas Institute of Engineering and Technology",
            font=("Segoe UI", 13, "bold"),
            bg="#1e3a8a",
            fg="white"
        )
        title_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        # Main Paned / Grid area
        main_content = ttk.Frame(self, padding=15)
        main_content.pack(fill=tk.BOTH, expand=True)

        # Left Column: Form
        form_frame = ttk.LabelFrame(main_content, text=" Employee Details Form ", padding=15)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        # Variables
        self.var_emp_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_department = tk.StringVar(value=self.departments[0])
        self.var_designation = tk.StringVar(value=self.designations[3])
        self.var_phone = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_joining_date = tk.StringVar()
        self.var_basic_salary = tk.StringVar(value="0")
        self.var_overtime_rate = tk.StringVar(value="0")
        self.var_allowances = tk.StringVar(value="0")
        self.var_deductions = tk.StringVar(value="0")
        self.var_status = tk.StringVar(value="Active")

        # Form Layout
        fields = [
            ("Employee ID *:", self.var_emp_id, "entry", None),
            ("Full Name *:", self.var_name, "entry", None),
            ("Department *:", self.var_department, "combo", self.departments),
            ("Designation *:", self.var_designation, "combo", self.designations),
            ("Phone Number *:", self.var_phone, "entry", None),
            ("Email Address *:", self.var_email, "entry", None),
            ("Joining Date (YYYY-MM-DD) *:", self.var_joining_date, "entry", None),
            ("Basic Salary (₹) *:", self.var_basic_salary, "entry", None),
            ("Overtime Rate (₹/hr):", self.var_overtime_rate, "entry", None),
            ("Allowances (₹):", self.var_allowances, "entry", None),
            ("Deductions (₹):", self.var_deductions, "entry", None),
            ("Status *:", self.var_status, "combo", ["Active", "Inactive"]),
        ]

        row = 0
        for label_text, var, ftype, options in fields:
            lbl = ttk.Label(form_frame, text=label_text, font=("Segoe UI", 9))
            lbl.grid(row=row, column=0, sticky=tk.W, pady=3, padx=(0, 10))

            if ftype == "entry":
                entry = ttk.Entry(form_frame, textvariable=var, width=26, font=("Segoe UI", 9))
                entry.grid(row=row, column=1, sticky=tk.W, pady=3)
                if label_text.startswith("Employee ID"):
                    self.entry_emp_id = entry
            elif ftype == "combo":
                combo = ttk.Combobox(form_frame, textvariable=var, values=options, state="readonly", width=24, font=("Segoe UI", 9))
                combo.grid(row=row, column=1, sticky=tk.W, pady=3)

            row += 1

        # Button row inside Form
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=(15, 0), sticky=tk.EW)

        btn_style_config = {"width": 8}
        self.btn_add = tk.Button(btn_frame, text="Add", bg="#16a34a", fg="white", font=("Segoe UI", 9, "bold"),
                                 relief=tk.FLAT, padx=8, pady=4, cursor="hand2", command=self.add_employee)
        self.btn_add.pack(side=tk.LEFT, padx=3)

        self.btn_update = tk.Button(btn_frame, text="Update", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"),
                                    relief=tk.FLAT, padx=8, pady=4, cursor="hand2", command=self.update_employee)
        self.btn_update.pack(side=tk.LEFT, padx=3)

        self.btn_delete = tk.Button(btn_frame, text="Delete", bg="#dc2626", fg="white", font=("Segoe UI", 9, "bold"),
                                    relief=tk.FLAT, padx=8, pady=4, cursor="hand2", command=self.delete_employee)
        self.btn_delete.pack(side=tk.LEFT, padx=3)

        self.btn_clear = tk.Button(btn_frame, text="Clear", bg="#64748b", fg="white", font=("Segoe UI", 9, "bold"),
                                   relief=tk.FLAT, padx=8, pady=4, cursor="hand2", command=self.clear_form)
        self.btn_clear.pack(side=tk.LEFT, padx=3)

        # Right Column: Search + Table
        table_frame = ttk.Frame(main_content)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Search Bar
        search_box = ttk.LabelFrame(table_frame, text=" Search Employees ", padding=10)
        search_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_box, text="Search by ID / Name / Dept:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 8))
        self.var_search = tk.StringVar()
        self.entry_search = ttk.Entry(search_box, textvariable=self.var_search, width=28, font=("Segoe UI", 9))
        self.entry_search.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_search.bind("<Return>", lambda e: self.search_employees())

        btn_search = tk.Button(search_box, text="Search", bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"),
                               relief=tk.FLAT, padx=10, pady=2, cursor="hand2", command=self.search_employees)
        btn_search.pack(side=tk.LEFT, padx=3)

        btn_show_all = tk.Button(search_box, text="Show All", bg="#475569", fg="white", font=("Segoe UI", 9),
                                 relief=tk.FLAT, padx=10, pady=2, cursor="hand2", command=self.load_employees)
        btn_show_all.pack(side=tk.LEFT, padx=3)

        self.lbl_count = ttk.Label(search_box, text="", font=("Segoe UI", 9, "italic"))
        self.lbl_count.pack(side=tk.RIGHT, padx=5)

        # Table Treeview with Dual Scrollbars
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "dept", "designation", "phone", "email", "basic", "allow", "deduct", "status")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="Emp ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("dept", text="Department")
        self.tree.heading("designation", text="Designation")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("email", text="Email")
        self.tree.heading("basic", text="Basic (₹)")
        self.tree.heading("allow", text="Allowances (₹)")
        self.tree.heading("deduct", text="Deductions (₹)")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=95, anchor=tk.W)
        self.tree.column("name", width=140, anchor=tk.W)
        self.tree.column("dept", width=150, anchor=tk.W)
        self.tree.column("designation", width=130, anchor=tk.W)
        self.tree.column("phone", width=100, anchor=tk.CENTER)
        self.tree.column("email", width=150, anchor=tk.W)
        self.tree.column("basic", width=85, anchor=tk.E)
        self.tree.column("allow", width=90, anchor=tk.E)
        self.tree.column("deduct", width=90, anchor=tk.E)
        self.tree.column("status", width=70, anchor=tk.CENTER)

        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_employee_selected)

    def load_employees(self):
        """Fetch and display all employees from database."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        employees = models.get_all_employees()
        for emp in employees:
            self.tree.insert("", tk.END, values=(
                emp["employee_id"],
                emp["name"],
                emp["department"],
                emp["designation"],
                emp["phone"],
                emp["email"],
                f"{emp['basic_salary']:,.2f}",
                f"{emp['allowances']:,.2f}",
                f"{emp['deductions']:,.2f}",
                emp["status"]
            ))

        self.lbl_count.config(text=f"Total: {len(employees)} Employees")

    def search_employees(self):
        query = self.var_search.get().strip()
        if not query:
            self.load_employees()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        results = models.search_employees(query)
        for emp in results:
            self.tree.insert("", tk.END, values=(
                emp["employee_id"],
                emp["name"],
                emp["department"],
                emp["designation"],
                emp["phone"],
                emp["email"],
                f"{emp['basic_salary']:,.2f}",
                f"{emp['allowances']:,.2f}",
                f"{emp['deductions']:,.2f}",
                emp["status"]
            ))
        self.lbl_count.config(text=f"Found: {len(results)} matching")

    def on_employee_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        emp_id = item["values"][0]

        emp = models.get_employee(emp_id)
        if emp:
            self.var_emp_id.set(emp["employee_id"])
            self.entry_emp_id.config(state="disabled")  # Primary key protected during edit
            self.var_name.set(emp["name"])
            self.var_department.set(emp["department"])
            self.var_designation.set(emp["designation"])
            self.var_phone.set(emp["phone"])
            self.var_email.set(emp["email"])
            self.var_joining_date.set(emp["joining_date"])
            self.var_basic_salary.set(str(emp["basic_salary"]))
            self.var_overtime_rate.set(str(emp["overtime_rate"]))
            self.var_allowances.set(str(emp["allowances"]))
            self.var_deductions.set(str(emp["deductions"]))
            self.var_status.set(emp["status"])

    def validate_inputs(self, is_new=True):
        """Run complete validation suite on form inputs."""
        emp_id = self.var_emp_id.get().strip()
        if is_new:
            ok, msg = validate_employee_id(emp_id)
            if not ok:
                messagebox.showerror("Validation Error", msg)
                return False

        name = self.var_name.get().strip()
        if not name or len(name) < 2:
            messagebox.showerror("Validation Error", "Full Name is required and must be at least 2 characters.")
            return False

        ok, msg = validate_phone(self.var_phone.get())
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        ok, msg = validate_email(self.var_email.get())
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        ok, msg = validate_date(self.var_joining_date.get())
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        ok, msg = validate_positive_number(self.var_basic_salary.get(), "Basic Salary", allow_zero=False)
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        ok, msg = validate_positive_number(self.var_overtime_rate.get(), "Overtime Rate", allow_zero=True)
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        ok, msg = validate_positive_number(self.var_allowances.get(), "Allowances", allow_zero=True)
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        ok, msg = validate_positive_number(self.var_deductions.get(), "Deductions", allow_zero=True)
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        return True

    def add_employee(self):
        if not self.validate_inputs(is_new=True):
            return

        emp_tuple = (
            self.var_emp_id.get().strip(),
            self.var_name.get().strip(),
            self.var_department.get(),
            self.var_designation.get(),
            self.var_phone.get().strip(),
            self.var_email.get().strip(),
            self.var_joining_date.get().strip(),
            float(self.var_basic_salary.get().strip()),
            float(self.var_overtime_rate.get().strip() or 0.0),
            float(self.var_allowances.get().strip() or 0.0),
            float(self.var_deductions.get().strip() or 0.0),
            self.var_status.get()
        )

        success, msg = models.add_employee(emp_tuple)
        if success:
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.load_employees()
            if self.on_data_changed_callback:
                self.on_data_changed_callback()
        else:
            messagebox.showerror("Error", msg)

    def update_employee(self):
        emp_id = self.var_emp_id.get().strip()
        if not emp_id:
            messagebox.showwarning("Select Employee", "Please select an employee from the table to update.")
            return

        if not self.validate_inputs(is_new=False):
            return

        emp_tuple = (
            self.var_name.get().strip(),
            self.var_department.get(),
            self.var_designation.get(),
            self.var_phone.get().strip(),
            self.var_email.get().strip(),
            self.var_joining_date.get().strip(),
            float(self.var_basic_salary.get().strip()),
            float(self.var_overtime_rate.get().strip() or 0.0),
            float(self.var_allowances.get().strip() or 0.0),
            float(self.var_deductions.get().strip() or 0.0),
            self.var_status.get(),
            emp_id
        )

        success, msg = models.update_employee(emp_tuple)
        if success:
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.load_employees()
            if self.on_data_changed_callback:
                self.on_data_changed_callback()
        else:
            messagebox.showerror("Error", msg)

    def delete_employee(self):
        emp_id = self.var_emp_id.get().strip()
        if not emp_id:
            messagebox.showwarning("Select Employee", "Please select an employee to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete Employee '{emp_id}'?\n"
            "This will also delete their attendance and salary records."
        )
        if confirm:
            success, msg = models.delete_employee(emp_id)
            if success:
                messagebox.showinfo("Deleted", msg)
                self.clear_form()
                self.load_employees()
                if self.on_data_changed_callback:
                    self.on_data_changed_callback()
            else:
                messagebox.showerror("Error", msg)

    def clear_form(self):
        self.entry_emp_id.config(state="normal")
        self.var_emp_id.set("")
        self.var_name.set("")
        self.var_department.set(self.departments[0])
        self.var_designation.set(self.designations[3])
        self.var_phone.set("")
        self.var_email.set("")
        self.var_joining_date.set("")
        self.var_basic_salary.set("0")
        self.var_overtime_rate.set("0")
        self.var_allowances.set("0")
        self.var_deductions.set("0")
        self.var_status.set("Active")
        self.tree.selection_remove(self.tree.selection())
