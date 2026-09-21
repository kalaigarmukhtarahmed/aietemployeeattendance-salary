import React, { useState, useRef } from 'react';
import * as XLSX from 'xlsx';
import {
  Upload,
  FileSpreadsheet,
  Download,
  CheckCircle,
  AlertCircle,
  Search,
  Save,
  Trash2,
  HelpCircle,
  Calculator,
  RefreshCw,
  Sparkles,
  Layers
} from 'lucide-react';

export interface Employee {
  id: string;
  name: string;
  department: string;
  designation: string;
  phone: string;
  email: string;
  joiningDate: string;
  basicSalary: number;
  overtimeRate: number;
  allowances: number;
  deductions: number;
  status: 'Active' | 'Inactive';
}

export interface Attendance {
  id: string;
  employeeId: string;
  month: number;
  year: number;
  totalWorkingDays: number;
  daysPresent: number;
  leaveDays: number;
  overtimeHours: number;
}

export interface SalaryRecord {
  id: string;
  employeeId: string;
  month: number;
  year: number;
  basicSalary: number;
  totalWorkingDays: number;
  daysPresent: number;
  leaveDays: number;
  overtimeHours: number;
  overtimeRate: number;
  attendanceSalary: number;
  overtimePay: number;
  allowances: number;
  grossSalary: number;
  deductions: number;
  netSalary: number;
  calculatedDate: string;
}

export interface CalculatedBatchItem {
  rowNum: number;
  employeeId: string;
  name: string;
  department: string;
  designation: string;
  month: number;
  year: number;
  totalWorkingDays: number;
  daysPresent: number;
  leaveDays: number;
  overtimeHours: number;
  overtimeRate: number;
  basicSalary: number;
  attendanceSalary: number;
  overtimePay: number;
  allowances: number;
  grossSalary: number;
  deductions: number;
  netSalary: number;
  isValid: boolean;
  statusMessage: string;
}

interface ExcelUploadViewProps {
  employees: Employee[];
  setEmployees: React.Dispatch<React.SetStateAction<Employee[]>>;
  attendance: Attendance[];
  setAttendance: React.Dispatch<React.SetStateAction<Attendance[]>>;
  salaries: SalaryRecord[];
  setSalaries: React.Dispatch<React.SetStateAction<SalaryRecord[]>>;
  showAlert: (msg: string, type: 'success' | 'error' | 'info') => void;
  onNavigateToTab?: (tab: string) => void;
}

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

function formatINR(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
}

function normalizeHeader(str: any): string {
  if (!str) return '';
  return String(str)
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '');
}

export default function ExcelUploadView({
  employees,
  setEmployees,
  attendance,
  setAttendance,
  salaries,
  setSalaries,
  showAlert,
  onNavigateToTab
}: ExcelUploadViewProps) {
  const [calculatedItems, setCalculatedItems] = useState<CalculatedBatchItem[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'valid' | 'error'>('all');
  const [isDragging, setIsDragging] = useState(false);
  const [showFormulasModal, setShowFormulasModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Parse Excel raw data into calculated items
  const processRawData = (rows: any[][], sourceName: string) => {
    if (!rows || rows.length === 0) {
      showAlert('Uploaded file is completely empty.', 'error');
      return;
    }

    // 1. Locate the header row
    let headerIdx = -1;
    for (let i = 0; i < Math.min(rows.length, 10); i++) {
      const rowNorm = rows[i].map(c => normalizeHeader(c));
      const hasEmp = rowNorm.some(h => ['employeeid', 'empid', 'id', 'staffid', 'facultyid'].includes(h));
      const hasAtt = rowNorm.some(h => ['dayspresent', 'present', 'totalworkingdays', 'workingdays'].includes(h));
      if (hasEmp || hasAtt) {
        headerIdx = i;
        break;
      }
    }

    if (headerIdx === -1) {
      headerIdx = 0;
    }

    const headerRow = rows[headerIdx];
    const colMap: Record<string, number> = {};

    const fieldAliases: Record<string, string[]> = {
      employeeId: ['employeeid', 'empid', 'id', 'employee', 'staffid', 'facultyid'],
      month: ['month', 'm', 'paymonth', 'monthnumber'],
      year: ['year', 'y', 'payyear'],
      totalWorkingDays: ['totalworkingdays', 'workingdays', 'totaldays', 'daysinmonth', 'workdays'],
      daysPresent: ['dayspresent', 'present', 'presentdays', 'attendeddays', 'attended'],
      leaveDays: ['leavedays', 'leaves', 'leave', 'absent', 'absentdays'],
      overtimeHours: ['overtimehours', 'overtime', 'othours', 'ot', 'extrahours'],
      basicSalary: ['basicsalary', 'basic', 'salary'],
      overtimeRate: ['overtimerate', 'otrate', 'rateperhour', 'hourlyrate'],
      allowances: ['allowances', 'allowance', 'da', 'hra'],
      deductions: ['deductions', 'deduction', 'pf', 'tax']
    };

    headerRow.forEach((h, colIdx) => {
      const norm = normalizeHeader(h);
      for (const [field, aliases] of Object.entries(fieldAliases)) {
        if (colMap[field] === undefined && aliases.includes(norm)) {
          colMap[field] = colIdx;
        }
      }
    });

    // Fallbacks if not recognized
    if (colMap.employeeId === undefined && headerRow.length > 0) colMap.employeeId = 0;
    if (colMap.month === undefined && headerRow.length > 1) colMap.month = 1;
    if (colMap.year === undefined && headerRow.length > 2) colMap.year = 2;
    if (colMap.totalWorkingDays === undefined && headerRow.length > 3) colMap.totalWorkingDays = 3;
    if (colMap.daysPresent === undefined && headerRow.length > 4) colMap.daysPresent = 4;
    if (colMap.leaveDays === undefined && headerRow.length > 5) colMap.leaveDays = 5;
    if (colMap.overtimeHours === undefined && headerRow.length > 6) colMap.overtimeHours = 6;

    const dataRows = rows.slice(headerIdx + 1);
    const empMap = new Map(employees.map(e => [e.id.trim().toUpperCase(), e]));

    const defaultMonth = 9;
    const defaultYear = 2026;

    const parsedResults: CalculatedBatchItem[] = [];

    dataRows.forEach((row, idx) => {
      if (!row || row.every(cell => cell === null || cell === undefined || String(cell).trim() === '')) {
        return;
      }

      const getColVal = (f: string, fallback = '') => {
        const colIdx = colMap[f];
        if (colIdx !== undefined && row[colIdx] !== undefined && row[colIdx] !== null) {
          return String(row[colIdx]).trim();
        }
        return fallback;
      };

      const rawEmpId = getColVal('employeeId').toUpperCase();
      if (!rawEmpId) return;

      const rawMonth = getColVal('month', String(defaultMonth));
      const rawYear = getColVal('year', String(defaultYear));
      const rawTotDays = getColVal('totalWorkingDays', '25');
      const rawPresDays = getColVal('daysPresent', '25');
      const rawLeaveDays = getColVal('leaveDays', '0');
      const rawOtHrs = getColVal('overtimeHours', '0');

      // Month parsing
      let monthNum = defaultMonth;
      if (/^\d+$/.test(rawMonth)) {
        monthNum = parseInt(rawMonth, 10);
      } else {
        const foundM = MONTH_NAMES.findIndex(m => m.toLowerCase().startsWith(rawMonth.toLowerCase()));
        if (foundM >= 0) monthNum = foundM + 1;
      }
      if (monthNum < 1 || monthNum > 12) monthNum = defaultMonth;

      const yearNum = /^\d+$/.test(rawYear) ? parseInt(rawYear, 10) : defaultYear;
      const totalDays = Math.max(1, parseFloat(rawTotDays) || 25);
      const daysPresent = Math.max(0, parseFloat(rawPresDays) || 0);
      const leaveDays = Math.max(0, parseFloat(rawLeaveDays) || 0);
      const overtimeHours = Math.max(0, parseFloat(rawOtHrs) || 0);

      // Match employee
      const matchedEmp = empMap.get(rawEmpId);
      let isValid = true;
      let statusMessage = 'Calculated & Verified';
      let empName = 'Unknown Staff';
      let dept = 'Unknown Department';
      let desig = 'Unknown Designation';
      let basic = 0;
      let otRate = 0;
      let allow = 0;
      let deduct = 0;

      if (!matchedEmp) {
        isValid = false;
        statusMessage = `Employee '${rawEmpId}' not found in registered staff`;
      } else {
        empName = matchedEmp.name;
        dept = matchedEmp.department;
        desig = matchedEmp.designation;
        basic = matchedEmp.basicSalary;
        otRate = matchedEmp.overtimeRate;
        allow = matchedEmp.allowances;
        deduct = matchedEmp.deductions;
      }

      // Check optional override values in sheet
      const overrideBasic = getColVal('basicSalary');
      if (overrideBasic && !isNaN(Number(overrideBasic))) basic = Number(overrideBasic);

      const overrideOtRate = getColVal('overtimeRate');
      if (overrideOtRate && !isNaN(Number(overrideOtRate))) otRate = Number(overrideOtRate);

      const overrideAllow = getColVal('allowances');
      if (overrideAllow && !isNaN(Number(overrideAllow))) allow = Number(overrideAllow);

      const overrideDeduct = getColVal('deductions');
      if (overrideDeduct && !isNaN(Number(overrideDeduct))) deduct = Number(overrideDeduct);

      // Validation
      if (daysPresent + leaveDays > totalDays) {
        isValid = false;
        statusMessage = `Days Present (${daysPresent}) + Leaves (${leaveDays}) exceeds Working Days (${totalDays})`;
      }

      // Formula Calculations
      // 1. Attendance Salary = (Basic Salary / Total Working Days) * Days Present
      const attendanceSalary = Math.round((basic / totalDays) * daysPresent);
      // 2. Overtime Pay = Overtime Hours * Overtime Rate
      const overtimePay = Math.round(overtimeHours * otRate);
      // 3. Gross Salary = Attendance Salary + Overtime Pay + Allowances
      const grossSalary = attendanceSalary + overtimePay + allow;
      // 4. Net Salary = Gross Salary - Deductions
      const netSalary = grossSalary - deduct;

      parsedResults.push({
        rowNum: idx + 1,
        employeeId: rawEmpId,
        name: empName,
        department: dept,
        designation: desig,
        month: monthNum,
        year: yearNum,
        totalWorkingDays: totalDays,
        daysPresent,
        leaveDays,
        overtimeHours,
        overtimeRate: otRate,
        basicSalary: basic,
        attendanceSalary,
        overtimePay,
        allowances: allow,
        grossSalary,
        deductions: deduct,
        netSalary,
        isValid,
        statusMessage
      });
    });

    setCalculatedItems(parsedResults);
    setFileName(sourceName);

    const validCnt = parsedResults.filter(r => r.isValid).length;
    const errCnt = parsedResults.length - validCnt;

    if (parsedResults.length === 0) {
      showAlert('No valid employee rows detected in spreadsheet.', 'error');
    } else {
      showAlert(
        `Parsed & calculated ${parsedResults.length} records (${validCnt} verified, ${errCnt} attention needed).`,
        errCnt > 0 ? 'info' : 'success'
      );
    }
  };

  // Handle file upload
  const handleFileUpload = (file: File) => {
    if (!file) return;

    setFileSize(`${(file.size / 1024).toFixed(1)} KB`);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][];
        processRawData(jsonData, file.name);
      } catch (err: any) {
        showAlert(`Failed to parse file: ${err.message || 'Corrupt spreadsheet'}`, 'error');
      }
    };
    reader.readAsArrayBuffer(file);
  };

  // One-click demo loader (scales to all 500 employees)
  const handleLoadDemoSheet = () => {
    const demoRows: any[][] = [
      ['Employee ID', 'Month', 'Year', 'Total Working Days', 'Days Present', 'Leave Days', 'Overtime Hours']
    ];

    employees.forEach((emp, idx) => {
      const totalWorkingDays = 25;
      const leaveDays = emp.status === 'Inactive' ? 25 : (idx % 11 === 0 ? 3 : idx % 7 === 0 ? 2 : idx % 5 === 0 ? 1 : 0);
      const daysPresent = totalWorkingDays - leaveDays;
      const overtimeHours = emp.status === 'Inactive' ? 0 : (idx % 6 === 0 ? 12 : idx % 4 === 0 ? 8 : idx % 3 === 0 ? 6 : idx % 2 === 0 ? 4 : 0);
      demoRows.push([emp.id, 9, 2026, totalWorkingDays, daysPresent, leaveDays, overtimeHours]);
    });

    setFileSize(`${(demoRows.length * 0.12).toFixed(1)} KB`);
    processRawData(demoRows, 'AIET_Faculty_Attendance_Sept2026.xlsx');
  };

  // Download Sample Excel Template pre-populated with all 500 faculty/staff records
  const handleDownloadTemplate = () => {
    const headers: any[][] = [
      ['ALVAS INSTITUTE OF ENGINEERING AND TECHNOLOGY (AIET) — ATTENDANCE & PAYROLL IMPORT TEMPLATE (500 EMPLOYEES)'],
      ['Instructions: Enter monthly attendance below. System auto-calculates Attendance Salary, OT Pay, Gross & Net Pay according to institutional rules.'],
      [],
      [
        'Employee ID',
        'Month',
        'Year',
        'Total Working Days',
        'Days Present',
        'Leave Days',
        'Overtime Hours',
        'Basic Salary (Optional)',
        'OT Rate (Optional)',
        'Allowances (Optional)',
        'Deductions (Optional)'
      ]
    ];

    employees.forEach((emp, idx) => {
      const totalWorkingDays = 25;
      const leaveDays = emp.status === 'Inactive' ? 25 : (idx % 11 === 0 ? 3 : idx % 7 === 0 ? 2 : idx % 5 === 0 ? 1 : 0);
      const daysPresent = totalWorkingDays - leaveDays;
      const overtimeHours = emp.status === 'Inactive' ? 0 : (idx % 6 === 0 ? 12 : idx % 4 === 0 ? 8 : idx % 3 === 0 ? 6 : idx % 2 === 0 ? 4 : 0);
      headers.push([
        emp.id, 9, 2026, totalWorkingDays, daysPresent, leaveDays, overtimeHours, '', '', '', ''
      ]);
    });

    const ws = XLSX.utils.aoa_to_sheet(headers);
    // Set column widths
    ws['!cols'] = [
      { wch: 16 }, { wch: 10 }, { wch: 10 }, { wch: 18 },
      { wch: 14 }, { wch: 12 }, { wch: 16 }, { wch: 22 },
      { wch: 18 }, { wch: 20 }, { wch: 20 }
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Attendance_Import');
    XLSX.writeFile(wb, 'AIET_Attendance_Salary_Import_Template.xlsx');
    showAlert(`Excel template for ${employees.length} employees downloaded successfully!`, 'success');
  };

  // Export Calculated Results to Excel
  const handleExportCalculated = () => {
    if (calculatedItems.length === 0) {
      showAlert('No calculated records to export.', 'error');
      return;
    }

    const exportRows = calculatedItems.map(item => ({
      'Row': item.rowNum,
      'Employee ID': item.employeeId,
      'Name': item.name,
      'Department': item.department,
      'Designation': item.designation,
      'Month': MONTH_NAMES[item.month - 1] || item.month,
      'Year': item.year,
      'Total Working Days': item.totalWorkingDays,
      'Days Present': item.daysPresent,
      'Leave Days': item.leaveDays,
      'Overtime Hours': item.overtimeHours,
      'Overtime Rate (₹/hr)': item.overtimeRate,
      'Basic Salary (₹)': item.basicSalary,
      'Attendance Salary (₹)': item.attendanceSalary,
      'Overtime Pay (₹)': item.overtimePay,
      'Allowances (₹)': item.allowances,
      'Gross Salary (₹)': item.grossSalary,
      'Deductions (₹)': item.deductions,
      'Net Salary (₹)': item.netSalary,
      'Status': item.statusMessage
    }));

    const ws = XLSX.utils.json_to_sheet(exportRows);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Calculated_Payroll');
    XLSX.writeFile(wb, `AIET_Batch_Calculated_Payroll_${new Date().toISOString().slice(0, 10)}.xlsx`);
    showAlert('Exported calculated payroll to Excel successfully!', 'success');
  };

  // Commit valid records into the Attendance and Salary states
  const handleSaveAllToSystem = () => {
    const validItems = calculatedItems.filter(r => r.isValid);
    if (validItems.length === 0) {
      showAlert('No valid records to save. Please review the errors.', 'error');
      return;
    }

    const todayStr = new Date().toISOString().split('T')[0];

    // 1. Update Attendance State
    setAttendance(prev => {
      const updated = [...prev];
      validItems.forEach(item => {
        const existingIdx = updated.findIndex(
          a => a.employeeId === item.employeeId && a.month === item.month && a.year === item.year
        );
        const record: Attendance = {
          id: existingIdx >= 0 ? updated[existingIdx].id : `att-${item.employeeId}-${item.month}-${item.year}`,
          employeeId: item.employeeId,
          month: item.month,
          year: item.year,
          totalWorkingDays: item.totalWorkingDays,
          daysPresent: item.daysPresent,
          leaveDays: item.leaveDays,
          overtimeHours: item.overtimeHours
        };
        if (existingIdx >= 0) {
          updated[existingIdx] = record;
        } else {
          updated.push(record);
        }
      });
      return updated;
    });

    // 2. Update Salary Records State
    setSalaries(prev => {
      const updated = [...prev];
      validItems.forEach(item => {
        const existingIdx = updated.findIndex(
          s => s.employeeId === item.employeeId && s.month === item.month && s.year === item.year
        );
        const record: SalaryRecord = {
          id: existingIdx >= 0 ? updated[existingIdx].id : `sal-${item.employeeId}-${item.month}-${item.year}`,
          employeeId: item.employeeId,
          month: item.month,
          year: item.year,
          basicSalary: item.basicSalary,
          totalWorkingDays: item.totalWorkingDays,
          daysPresent: item.daysPresent,
          leaveDays: item.leaveDays,
          overtimeHours: item.overtimeHours,
          overtimeRate: item.overtimeRate,
          attendanceSalary: item.attendanceSalary,
          overtimePay: item.overtimePay,
          allowances: item.allowances,
          grossSalary: item.grossSalary,
          deductions: item.deductions,
          netSalary: item.netSalary,
          calculatedDate: todayStr
        };
        if (existingIdx >= 0) {
          updated[existingIdx] = record;
        } else {
          updated.push(record);
        }
      });
      return updated;
    });

    showAlert(
      `Successfully saved ${validItems.length} calculated attendance & salary records into the AIET system! Check Dashboard, Salary Processing, or Slips.`,
      'success'
    );
  };

  // Filtered rows for the table
  const filteredItems = calculatedItems.filter(item => {
    const matchesSearch =
      item.employeeId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.statusMessage.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;
    if (statusFilter === 'valid') return item.isValid;
    if (statusFilter === 'error') return !item.isValid;
    return true;
  });

  const totalRows = calculatedItems.length;
  const validRows = calculatedItems.filter(r => r.isValid).length;
  const errorRows = totalRows - validRows;
  const totalGross = calculatedItems.filter(r => r.isValid).reduce((sum, r) => sum + r.grossSalary, 0);
  const totalNet = calculatedItems.filter(r => r.isValid).reduce((sum, r) => sum + r.netSalary, 0);

  const totalPages = Math.max(1, Math.ceil(filteredItems.length / (pageSize === -1 ? (filteredItems.length || 1) : pageSize)));
  const currentSafePage = Math.min(currentPage, totalPages);
  const paginatedItems = pageSize === -1
    ? filteredItems
    : filteredItems.slice((currentSafePage - 1) * pageSize, currentSafePage * pageSize);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="p-2 bg-blue-100 text-blue-900 rounded-lg">
              <FileSpreadsheet className="w-5 h-5" />
            </span>
            <h2 className="text-base font-bold text-slate-800">
              Excel Sheet Upload &amp; Batch Salary Calculation
            </h2>
            <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
              Automated Engine
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Upload attendance spreadsheets (.xlsx, .xls, .csv). The system reads working days, attendance, and overtime, then calculates Attendance Salary, Overtime Pay, Gross &amp; Net Salary automatically.
          </p>
        </div>

        <div className="flex items-center flex-wrap gap-2">
          <button
            onClick={() => setShowFormulasModal(true)}
            className="text-xs font-semibold text-blue-700 hover:text-blue-900 px-2.5 py-1.5 rounded border border-blue-200 hover:bg-blue-50 transition flex items-center space-x-1"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Calculation Rules</span>
          </button>
          <button
            onClick={handleDownloadTemplate}
            className="text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded transition flex items-center space-x-1.5 border border-slate-300"
          >
            <Download className="w-3.5 h-3.5 text-slate-600" />
            <span>Download Template</span>
          </button>
          <button
            onClick={handleLoadDemoSheet}
            className="text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 px-3 py-1.5 rounded transition flex items-center space-x-1.5 shadow-xs"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Load Sample AIET Sheet</span>
          </button>
        </div>
      </div>

      {/* File Drag-and-Drop & Selector */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileUpload(e.dataTransfer.files[0]);
          }
        }}
        className={`p-6 rounded-xl border-2 border-dashed transition text-center cursor-pointer ${
          isDragging
            ? 'border-blue-600 bg-blue-50/60'
            : fileName
            ? 'border-emerald-300 bg-emerald-50/30'
            : 'border-slate-300 bg-white hover:border-blue-400 hover:bg-slate-50'
        }`}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx, .xls, .csv"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileUpload(e.target.files[0]);
            }
          }}
        />

        <div className="max-w-md mx-auto flex flex-col items-center space-y-2">
          <div className="p-3 bg-blue-50 text-blue-800 rounded-full border border-blue-200">
            <Upload className="w-6 h-6 text-blue-700" />
          </div>

          {fileName ? (
            <div className="space-y-1">
              <div className="text-sm font-bold text-slate-800 flex items-center justify-center space-x-1.5">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span>Uploaded: {fileName}</span>
                <span className="text-xs text-slate-400 font-normal">({fileSize})</span>
              </div>
              <p className="text-xs text-slate-500">
                Data extracted and evaluated successfully. Click or drag another file to replace.
              </p>
            </div>
          ) : (
            <div className="space-y-1">
              <div className="text-sm font-bold text-slate-700">
                Click to browse or drag &amp; drop your Excel sheet here
              </div>
              <p className="text-xs text-slate-500">
                Supports Microsoft Excel (.xlsx, .xls) and CSV (.csv) spreadsheets
              </p>
            </div>
          )}
        </div>
      </div>

      {/* KPI Cards */}
      {calculatedItems.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs border-l-4 border-l-blue-600">
            <div className="text-[10px] font-bold text-slate-500 uppercase">Total Rows Parsed</div>
            <div className="text-xl font-black text-slate-800 mt-1">{totalRows}</div>
            <div className="text-[11px] text-slate-400">Sheet rows detected</div>
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs border-l-4 border-l-emerald-600">
            <div className="text-[10px] font-bold text-slate-500 uppercase">Valid &amp; Verified</div>
            <div className="text-xl font-black text-emerald-700 mt-1">{validRows}</div>
            <div className="text-[11px] text-emerald-600">Ready for payroll commit</div>
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs border-l-4 border-l-rose-500">
            <div className="text-[10px] font-bold text-slate-500 uppercase">Attention / Errors</div>
            <div className="text-xl font-black text-rose-700 mt-1">{errorRows}</div>
            <div className="text-[11px] text-rose-600">Requires correction</div>
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs border-l-4 border-l-indigo-600">
            <div className="text-[10px] font-bold text-slate-500 uppercase">Calculated Gross</div>
            <div className="text-lg font-black text-indigo-900 mt-1">{formatINR(totalGross)}</div>
            <div className="text-[11px] text-slate-400">Att. Salary + OT + Allow</div>
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs border-l-4 border-l-teal-600">
            <div className="text-[10px] font-bold text-slate-500 uppercase">Total Net Payable</div>
            <div className="text-lg font-black text-teal-800 mt-1">{formatINR(totalNet)}</div>
            <div className="text-[11px] text-teal-700 font-medium">After deductions</div>
          </div>
        </div>
      )}

      {/* Results Table Section */}
      {calculatedItems.length > 0 && (
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          {/* Action Bar Above Table */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-3">
              <div className="relative w-64">
                <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter by ID, name, dept..."
                  className="w-full pl-9 pr-3 py-1.5 border border-slate-300 rounded-md text-xs focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div className="flex items-center space-x-1 text-xs">
                {(['all', 'valid', 'error'] as const).map(mode => (
                  <button
                    key={mode}
                    onClick={() => setStatusFilter(mode)}
                    className={`px-2.5 py-1 rounded text-xs font-semibold capitalize transition ${
                      statusFilter === mode
                        ? 'bg-blue-900 text-white'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {mode === 'all' ? `All (${totalRows})` : mode === 'valid' ? `Valid (${validRows})` : `Errors (${errorRows})`}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={handleExportCalculated}
                className="bg-slate-700 hover:bg-slate-800 text-white text-xs font-semibold px-3 py-1.5 rounded transition flex items-center space-x-1"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export Calculated Excel</span>
              </button>
              <button
                onClick={handleSaveAllToSystem}
                disabled={validRows === 0}
                className={`text-xs font-bold px-4 py-1.5 rounded transition flex items-center space-x-1.5 shadow-sm ${
                  validRows > 0
                    ? 'bg-emerald-600 hover:bg-emerald-700 text-white cursor-pointer'
                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                }`}
              >
                <Save className="w-3.5 h-3.5" />
                <span>Save All ({validRows}) to System</span>
              </button>
            </div>
          </div>

          {/* Table Container */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-100 border-b border-slate-200 text-slate-700 font-semibold">
                  <th className="py-2.5 px-3">#</th>
                  <th className="py-2.5 px-3">Emp ID</th>
                  <th className="py-2.5 px-3">Employee Name</th>
                  <th className="py-2.5 px-3">Department</th>
                  <th className="py-2.5 px-3 text-center">Period</th>
                  <th className="py-2.5 px-3 text-center">Days (Tot/Pres/Lve)</th>
                  <th className="py-2.5 px-3 text-center">OT Hrs</th>
                  <th className="py-2.5 px-3 text-right">Basic (₹)</th>
                  <th className="py-2.5 px-3 text-right">Att. Sal (₹)</th>
                  <th className="py-2.5 px-3 text-right">OT Pay (₹)</th>
                  <th className="py-2.5 px-3 text-right">Allow (₹)</th>
                  <th className="py-2.5 px-3 text-right">Gross (₹)</th>
                  <th className="py-2.5 px-3 text-right">Deduct (₹)</th>
                  <th className="py-2.5 px-3 text-right font-bold text-emerald-800">Net Salary (₹)</th>
                  <th className="py-2.5 px-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {paginatedItems.length === 0 ? (
                  <tr>
                    <td colSpan={15} className="py-8 text-center text-slate-400 text-xs">
                      No matching records found for the active filter.
                    </td>
                  </tr>
                ) : (
                  paginatedItems.map((item) => (
                    <tr
                      key={`${item.employeeId}-${item.rowNum}`}
                      className={`hover:bg-slate-50 transition ${!item.isValid ? 'bg-rose-50/40' : ''}`}
                    >
                      <td className="py-2 px-3 text-slate-400 font-mono text-[11px]">{item.rowNum}</td>
                      <td className="py-2 px-3 font-semibold text-blue-900 whitespace-nowrap">{item.employeeId}</td>
                      <td className="py-2 px-3 font-medium text-slate-800 whitespace-nowrap">{item.name}</td>
                      <td className="py-2 px-3 text-slate-600 whitespace-nowrap">{item.department}</td>
                      <td className="py-2 px-3 text-center text-slate-600 whitespace-nowrap">
                        {MONTH_NAMES[item.month - 1]?.slice(0, 3)} '{String(item.year).slice(-2)}
                      </td>
                      <td className="py-2 px-3 text-center font-mono text-[11px]">
                        <span className="text-slate-500">{item.totalWorkingDays}</span> /{' '}
                        <span className="font-bold text-emerald-700">{item.daysPresent}</span> /{' '}
                        <span className="text-rose-600">{item.leaveDays}</span>
                      </td>
                      <td className="py-2 px-3 text-center text-slate-700">{item.overtimeHours}h</td>
                      <td className="py-2 px-3 text-right text-slate-600">{formatINR(item.basicSalary)}</td>
                      <td className="py-2 px-3 text-right text-blue-900 font-medium">{formatINR(item.attendanceSalary)}</td>
                      <td className="py-2 px-3 text-right text-slate-700">{formatINR(item.overtimePay)}</td>
                      <td className="py-2 px-3 text-right text-slate-700">+{formatINR(item.allowances)}</td>
                      <td className="py-2 px-3 text-right font-semibold text-indigo-900">{formatINR(item.grossSalary)}</td>
                      <td className="py-2 px-3 text-right text-rose-700">-{formatINR(item.deductions)}</td>
                      <td className="py-2 px-3 text-right font-black text-emerald-700">{formatINR(item.netSalary)}</td>
                      <td className="py-2 px-3 text-center whitespace-nowrap">
                        {item.isValid ? (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                            <CheckCircle className="w-3 h-3" />
                            <span>Verified</span>
                          </span>
                        ) : (
                          <span
                            title={item.statusMessage}
                            className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 cursor-help"
                          >
                            <AlertCircle className="w-3 h-3" />
                            <span className="truncate max-w-[120px]">{item.statusMessage}</span>
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination and Summary Bar */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-slate-600 pt-3 border-t border-slate-100">
            <div className="flex items-center flex-wrap gap-3">
              <div>
                Showing{' '}
                <span className="font-semibold text-slate-800">
                  {filteredItems.length === 0 ? 0 : (currentSafePage - 1) * (pageSize === -1 ? filteredItems.length : pageSize) + 1}
                </span>{' '}
                to{' '}
                <span className="font-semibold text-slate-800">
                  {pageSize === -1 ? filteredItems.length : Math.min(currentSafePage * pageSize, filteredItems.length)}
                </span>{' '}
                of <span className="font-semibold text-slate-800">{filteredItems.length}</span> records
                {filteredItems.length !== totalRows && (
                  <span className="text-slate-400 ml-1">(filtered from {totalRows})</span>
                )}
              </div>

              <div className="flex items-center space-x-1 pl-2 border-l border-slate-200">
                <span className="text-[11px] text-slate-500">Rows per page:</span>
                <select
                  value={pageSize}
                  onChange={(e) => {
                    setPageSize(Number(e.target.value));
                    setCurrentPage(1);
                  }}
                  className="border border-slate-200 rounded px-2 py-1 text-xs bg-white text-slate-700 focus:outline-hidden focus:ring-1 focus:ring-blue-600"
                >
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={250}>250</option>
                  <option value={-1}>All (500)</option>
                </select>
              </div>

              <div className="flex items-center space-x-3 pl-2 border-l border-slate-200">
                <span className="flex items-center space-x-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>
                  <span className="text-slate-700 font-medium">{validRows} Verified</span>
                </span>
                <span className="flex items-center space-x-1">
                  <span className="w-2 h-2 rounded-full bg-rose-500 inline-block"></span>
                  <span className="text-slate-700 font-medium">{errorRows} Errors</span>
                </span>
              </div>
            </div>

            {/* Page navigation buttons */}
            {totalPages > 1 && (
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => setCurrentPage(1)}
                  disabled={currentSafePage === 1}
                  className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed text-[11px] font-medium"
                  title="First Page"
                >
                  « First
                </button>
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentSafePage === 1}
                  className="px-2.5 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed text-[11px] font-medium"
                >
                  ‹ Prev
                </button>
                <span className="px-2.5 py-1 text-slate-700 font-semibold bg-slate-100 rounded text-xs">
                  {currentSafePage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentSafePage === totalPages}
                  className="px-2.5 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed text-[11px] font-medium"
                >
                  Next ›
                </button>
                <button
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={currentSafePage === totalPages}
                  className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed text-[11px] font-medium"
                  title="Last Page"
                >
                  Last »
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Formula & Rule Guidance Modal */}
      {showFormulasModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 text-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <div className="flex items-center space-x-2">
                <Calculator className="w-5 h-5 text-blue-700" />
                <h3 className="font-bold text-sm text-slate-900">AIET Institutional Calculation Rules</h3>
              </div>
              <button
                onClick={() => setShowFormulasModal(false)}
                className="text-xs font-bold text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-blue-50/70 border border-blue-200 rounded-lg">
                <div className="font-bold text-blue-900">1. Attendance Salary:</div>
                <div className="font-mono text-[11px] text-blue-800 mt-0.5">
                  (Basic Salary / Total Working Days) × Days Present
                </div>
                <div className="text-slate-500 text-[11px] mt-1">
                  Prorates basic pay according to attended teaching and administrative days.
                </div>
              </div>

              <div className="p-3 bg-indigo-50/70 border border-indigo-200 rounded-lg">
                <div className="font-bold text-indigo-900">2. Overtime Pay:</div>
                <div className="font-mono text-[11px] text-indigo-800 mt-0.5">
                  Overtime Hours × Overtime Rate (₹/hr)
                </div>
                <div className="text-slate-500 text-[11px] mt-1">
                  Rates are configured in employee master or overridden in sheet.
                </div>
              </div>

              <div className="p-3 bg-teal-50/70 border border-teal-200 rounded-lg">
                <div className="font-bold text-teal-900">3. Gross Salary:</div>
                <div className="font-mono text-[11px] text-teal-800 mt-0.5">
                  Attendance Salary + Overtime Pay + Allowances
                </div>
              </div>

              <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-lg">
                <div className="font-bold text-emerald-900">4. Net Salary:</div>
                <div className="font-mono text-[11px] text-emerald-800 mt-0.5">
                  Gross Salary − Deductions (PF / Tax)
                </div>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 space-y-1">
                <div className="font-bold text-slate-700">Validation Constraint:</div>
                <div>• Days Present + Leave Days must be &le; Total Working Days.</div>
                <div>• Employee ID must match a registered employee in the master database.</div>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowFormulasModal(false)}
                className="bg-blue-700 hover:bg-blue-800 text-white font-semibold text-xs px-4 py-2 rounded-md transition"
              >
                Close Guidance
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
