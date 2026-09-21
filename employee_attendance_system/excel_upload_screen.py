"""
Excel Upload and Batch Calculation GUI Screen for AIET Desktop System.
Allows staff to upload Excel sheets (.xlsx, .xls, .csv), parse attendance data,
auto-calculate salary components using exact institutional formulas,
and commit the batch into the SQLite database.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import excel_import
from utils import get_month_name

class ExcelUploadScreen(tk.Frame):
    def __init__(self, parent, on_data_changed_callback=None):
        super().__init__(parent, bg="#f8fafc")
        self.on_data_changed_callback = on_data_changed_callback
        self.parsed_records = []
        self.filtered_records = []
        self.current_file_path = None

        self.create_ui()

    def create_ui(self):
        # 1. Top Header Banner
        header_frame = tk.Frame(self, bg="#ffffff", padx=25, pady=16)
        header_frame.pack(fill=tk.X)

        title_box = tk.Frame(header_frame, bg="#ffffff")
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text="📥 Excel Sheet Upload & Batch Salary Calculator",
            font=("Segoe UI", 15, "bold"),
            fg="#1e3a8a",
            bg="#ffffff"
        ).pack(anchor=tk.W)

        tk.Label(
            title_box,
            text="Upload monthly attendance spreadsheets to auto-compute Attendance Salary, Overtime Pay, Gross & Net Salary instantly.",
            font=("Segoe UI", 9),
            fg="#64748b",
            bg="#ffffff"
        ).pack(anchor=tk.W, pady=(2, 0))

        # 2. Action Controls Toolbar
        toolbar = tk.Frame(self, bg="#ffffff", padx=25, pady=12)
        toolbar.pack(fill=tk.X, pady=(1, 10))

        btn_upload = tk.Button(
            toolbar,
            text="📂 Choose Excel / CSV File",
            font=("Segoe UI", 9, "bold"),
            bg="#1e3a8a",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.browse_and_process_file
        )
        btn_upload.pack(side=tk.LEFT, padx=(0, 10))

        btn_demo = tk.Button(
            toolbar,
            text="⚡ Load Sample AIET Sheet",
            font=("Segoe UI", 9),
            bg="#0284c7",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.load_demo_sheet
        )
        btn_demo.pack(side=tk.LEFT, padx=(0, 10))

        btn_template = tk.Button(
            toolbar,
            text="📋 Download Excel Template",
            font=("Segoe UI", 9),
            bg="#f1f5f9",
            fg="#1e293b",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.download_template
        )
        btn_template.pack(side=tk.LEFT, padx=(0, 10))

        # Search box on right
        search_frame = tk.Frame(toolbar, bg="#ffffff")
        search_frame.pack(side=tk.RIGHT)

        tk.Label(search_frame, text="🔍 Filter:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#ffffff").pack(side=tk.LEFT, padx=(0, 5))
        self.var_filter = tk.StringVar()
        self.var_filter.trace_add("write", lambda *args: self.filter_table())
        ent_filter = tk.Entry(search_frame, textvariable=self.var_filter, font=("Segoe UI", 9), width=22)
        ent_filter.pack(side=tk.LEFT)

        # 3. Summary Stats Cards
        self.stats_frame = tk.Frame(self, bg="#f8fafc", padx=25)
        self.stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.card_total = self.create_metric_card(self.stats_frame, "Total Rows", "0", "#1e3a8a")
        self.card_valid = self.create_metric_card(self.stats_frame, "Valid & Ready", "0", "#16a34a")
        self.card_errors = self.create_metric_card(self.stats_frame, "Errors / Attention", "0", "#dc2626")
        self.card_gross = self.create_metric_card(self.stats_frame, "Total Calculated Gross", "₹ 0.00", "#0891b2")
        self.card_net = self.create_metric_card(self.stats_frame, "Total Net Payable", "₹ 0.00", "#7c3aed")

        # 4. Data Treeview Table
        table_container = tk.Frame(self, bg="#ffffff", padx=25, pady=10)
        table_container.pack(fill=tk.BOTH, expand=True)

        columns = (
            "row", "emp_id", "name", "dept", "period", "working_days", "present",
            "leaves", "ot_hours", "basic", "att_salary", "ot_pay", "allow",
            "gross", "deduct", "net", "status"
        )

        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")

        headers_config = [
            ("row", "#", 40, tk.CENTER),
            ("emp_id", "Emp ID", 90, tk.W),
            ("name", "Employee Name", 140, tk.W),
            ("dept", "Department", 120, tk.W),
            ("period", "Period", 90, tk.CENTER),
            ("working_days", "Work Days", 70, tk.CENTER),
            ("present", "Present", 60, tk.CENTER),
            ("leaves", "Leaves", 60, tk.CENTER),
            ("ot_hours", "OT Hrs", 60, tk.CENTER),
            ("basic", "Basic Sal", 85, tk.E),
            ("att_salary", "Att. Salary", 85, tk.E),
            ("ot_pay", "OT Pay", 75, tk.E),
            ("allow", "Allowances", 80, tk.E),
            ("gross", "Gross Salary", 95, tk.E),
            ("deduct", "Deductions", 80, tk.E),
            ("net", "Net Salary", 95, tk.E),
            ("status", "Calculation Status", 150, tk.W),
        ]

        for col_id, text, width, align in headers_config:
            self.tree.heading(col_id, text=text, command=lambda c=col_id: self.sort_column(c))
            self.tree.column(col_id, width=width, anchor=align)

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        table_container.rowconfigure(0, weight=1)
        table_container.columnconfigure(0, weight=1)

        # 5. Bottom Action Bar
        bottom_bar = tk.Frame(self, bg="#ffffff", padx=25, pady=12)
        bottom_bar.pack(fill=tk.X)

        self.lbl_file_status = tk.Label(
            bottom_bar,
            text="No spreadsheet file uploaded yet. Choose an Excel (.xlsx, .xls) or CSV file above.",
            font=("Segoe UI", 9, "italic"),
            fg="#64748b",
            bg="#ffffff"
        )
        self.lbl_file_status.pack(side=tk.LEFT)

        btn_save_all = tk.Button(
            bottom_bar,
            text="💾 Save & Apply All to Database",
            font=("Segoe UI", 9, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=16,
            pady=7,
            cursor="hand2",
            command=self.save_batch_records
        )
        btn_save_all.pack(side=tk.RIGHT, padx=(10, 0))

        btn_export = tk.Button(
            bottom_bar,
            text="📊 Export Calculated Results",
            font=("Segoe UI", 9),
            bg="#475569",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self.export_calculated
        )
        btn_export.pack(side=tk.RIGHT)

    def create_metric_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="#ffffff", padx=16, pady=12, highlightbackground="#e2e8f0", highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#ffffff").pack(anchor=tk.W)
        lbl_val = tk.Label(card, text=value, font=("Segoe UI", 13, "bold"), fg=color, bg="#ffffff")
        lbl_val.pack(anchor=tk.W, pady=(2, 0))
        return lbl_val

    def browse_and_process_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Attendance / Salary Excel File",
            filetypes=[
                ("Excel & CSV Files", "*.xlsx *.xls *.csv"),
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.process_file(file_path)

    def download_template(self):
        save_path = filedialog.asksaveasfilename(
            title="Save AIET Attendance Import Template",
            defaultextension=".xlsx",
            initialfile="AIET_Attendance_Salary_Import_Template.xlsx",
            filetypes=[("Excel Workbook", "*.xlsx"), ("CSV Document", "*.csv")]
        )
        if save_path:
            try:
                ok, path = excel_import.generate_excel_import_template(save_path)
                if ok:
                    messagebox.showinfo("Template Ready", f"Excel import template saved successfully:\n{path}")
                else:
                    messagebox.showerror("Error", "Could not generate Excel template.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_demo_sheet(self):
        """Generate a temporary template and load it directly for immediate preview."""
        temp_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(temp_dir, exist_ok=True)
        demo_file = os.path.join(temp_dir, "AIET_Demo_Attendance_Batch.xlsx")
        ok, path = excel_import.generate_excel_import_template(demo_file)
        if ok:
            self.process_file(path)

    def process_file(self, file_path):
        self.current_file_path = file_path
        filename = os.path.basename(file_path)
        self.lbl_file_status.config(text=f"Loaded File: {filename} ({os.path.getsize(file_path) // 1024} KB)")

        result = excel_import.parse_and_calculate_excel(file_path)
        if not result["success"]:
            messagebox.showerror("File Parsing Failed", result.get("error", "Unknown error while reading file."))
            return

        self.parsed_records = result["records"]
        self.card_total.config(text=str(result["total_rows"]))
        self.card_valid.config(text=str(result["valid_rows"]))
        self.card_errors.config(text=str(result["error_rows"]))
        self.card_gross.config(text=f"₹ {result['total_gross']:,.2f}")
        self.card_net.config(text=f"₹ {result['total_net']:,.2f}")

        self.filter_table()

    def filter_table(self):
        q = self.var_filter.get().strip().lower()
        self.tree.delete(*self.tree.get_children())

        filtered = []
        for r in self.parsed_records:
            if not q or (
                q in r["employee_id"].lower() or
                q in r["name"].lower() or
                q in r["department"].lower() or
                q in r["status"].lower() or
                q in str(r["month"]).lower() or
                q in str(r["year"]).lower()
            ):
                filtered.append(r)

        self.filtered_records = filtered

        for r in filtered:
            period_str = f"{r['month_name'][:3]} '{str(r['year'])[-2:]}"
            status_display = "✓ " + r["status"] if r["is_valid"] else "⚠ " + r["status"]

            row_id = self.tree.insert("", tk.END, values=(
                r["row_num"],
                r["employee_id"],
                r["name"],
                r["department"],
                period_str,
                r["total_working_days"],
                r["days_present"],
                r["leave_days"],
                r["overtime_hours"],
                f"{r['basic_salary']:,.0f}",
                f"{r['attendance_salary']:,.0f}",
                f"{r['overtime_pay']:,.0f}",
                f"{r['allowances']:,.0f}",
                f"{r['gross_salary']:,.0f}",
                f"{r['deductions']:,.0f}",
                f"{r['net_salary']:,.0f}",
                status_display
            ))

            if not r["is_valid"]:
                self.tree.item(row_id, tags=("error_row",))
            else:
                self.tree.item(row_id, tags=("valid_row",))

        self.tree.tag_configure("error_row", background="#fef2f2", foreground="#991b1b")
        self.tree.tag_configure("valid_row", background="#ffffff", foreground="#0f172a")

    def sort_column(self, col_id):
        # Allow basic sorting
        pass

    def save_batch_records(self):
        if not self.parsed_records:
            messagebox.showwarning("No Data", "Please upload an Excel or CSV file first.")
            return

        valid_count = sum(1 for r in self.parsed_records if r["is_valid"])
        if valid_count == 0:
            messagebox.showerror("No Valid Records", "No records passed validation. Please resolve the errors before saving.")
            return

        confirm = messagebox.askyesno(
            "Confirm Batch Save",
            f"Are you sure you want to save and commit {valid_count} calculated attendance & salary records into the AIET database?"
        )
        if not confirm:
            return

        saved, err_count, errors = excel_import.save_batch_to_database(self.parsed_records)

        msg = f"Successfully saved {saved} employee attendance and salary records into the database!"
        if err_count > 0:
            msg += f"\n\n{err_count} records were skipped due to errors."

        messagebox.showinfo("Batch Save Completed", msg)

        if self.on_data_changed_callback:
            self.on_data_changed_callback()

    def export_calculated(self):
        if not self.parsed_records:
            messagebox.showwarning("No Data", "No calculated records available to export.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Export Calculated Batch Sheet",
            defaultextension=".xlsx",
            initialfile="AIET_Batch_Calculated_Payroll.xlsx",
            filetypes=[("Excel Workbook", "*.xlsx"), ("CSV Document", "*.csv")]
        )
        if save_path:
            try:
                ok, path = excel_import.export_calculated_to_excel(self.parsed_records, save_path)
                if ok:
                    messagebox.showinfo("Export Successful", f"Calculated spreadsheet exported successfully:\n{path}")
                else:
                    messagebox.showerror("Export Failed", "Could not export spreadsheet.")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
