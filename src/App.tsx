import React, { useState, useMemo } from 'react';
import ExcelUploadView from './components/ExcelUploadView';
import {
  Users,
  Calendar,
  DollarSign,
  FileText,
  BarChart3,
  Settings,
  Plus,
  Trash2,
  Edit,
  Download,
  Search,
  CheckCircle,
  AlertCircle,
  Clock,
  Printer,
  FileSpreadsheet,
  Code,
  Building2,
  RefreshCw,
  FolderDown
} from 'lucide-react';
import JSZip from 'jszip';
import {
  Employee,
  Attendance,
  SalaryRecord,
  INITIAL_500_EMPLOYEES,
  INITIAL_500_ATTENDANCE,
  INITIAL_500_SALARIES,
  DEPARTMENTS,
  DESIGNATIONS
} from './data/mockEmployees500';

// Load Python project files into bundle
const pythonSourceFiles = import.meta.glob<string>('../employee_attendance_system/*.{py,txt,md}', {
  query: '?raw',
  import: 'default',
  eager: true,
});

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'employees' | 'attendance' | 'salary' | 'excel_upload' | 'slips' | 'reports' | 'code' | 'settings'>('dashboard');

  const [employees, setEmployees] = useState<Employee[]>(INITIAL_500_EMPLOYEES);
  const [attendance, setAttendance] = useState<Attendance[]>(INITIAL_500_ATTENDANCE);
  const [salaries, setSalaries] = useState<SalaryRecord[]>(INITIAL_500_SALARIES);

  // Employee Form & Pagination states
  const [empForm, setEmpForm] = useState<Partial<Employee>>({
    id: '',
    name: '',
    department: DEPARTMENTS[0],
    designation: DESIGNATIONS[3],
    phone: '',
    email: '',
    joiningDate: '2024-06-01',
    basicSalary: 50000,
    overtimeRate: 350,
    allowances: 6000,
    deductions: 4000,
    status: 'Active'
  });
  const [empSearch, setEmpSearch] = useState('');
  const [empDeptFilter, setEmpDeptFilter] = useState('All');
  const [empPage, setEmpPage] = useState(1);
  const [empPageSize, setEmpPageSize] = useState(25);
  const [editingEmpId, setEditingEmpId] = useState<string | null>(null);

  // Attendance Form & Pagination states
  const [attSearch, setAttSearch] = useState('');
  const [attDeptFilter, setAttDeptFilter] = useState('All');
  const [attPage, setAttPage] = useState(1);
  const [attPageSize, setAttPageSize] = useState(25);
  const [attEmpId, setAttEmpId] = useState(INITIAL_500_EMPLOYEES[0]?.id || 'AIET-CSE-101');
  const [attMonth, setAttMonth] = useState(9);
  const [attYear, setAttYear] = useState(2026);
  const [attTotalDays, setAttTotalDays] = useState(25);
  const [attPresentDays, setAttPresentDays] = useState(25);
  const [attLeaveDays, setAttLeaveDays] = useState(0);
  const [attOtHours, setAttOtHours] = useState(0);

  // Salary processing state
  const [salEmpId, setSalEmpId] = useState(INITIAL_500_EMPLOYEES[0]?.id || 'AIET-CSE-101');
  const [salMonth, setSalMonth] = useState(9);
  const [salYear, setSalYear] = useState(2026);
  const [calculatedSalary, setCalculatedSalary] = useState<SalaryRecord | null>(null);

  // Salary slip viewer modal & Pagination states
  const [slipModalRecord, setSlipModalRecord] = useState<SalaryRecord | null>(null);
  const [slipsSearch, setSlipsSearch] = useState('');
  const [slipsDeptFilter, setSlipsDeptFilter] = useState('All');
  const [slipsPage, setSlipsPage] = useState(1);
  const [slipsPageSize, setSlipsPageSize] = useState(25);

  // Notification / Alert
  const [alert, setAlert] = useState<{ msg: string; type: 'success' | 'error' | 'info' } | null>(null);

  const showAlert = (msg: string, type: 'success' | 'error' | 'info' = 'info') => {
    setAlert({ msg, type });
    setTimeout(() => setAlert(null), 4000);
  };

  // Helper formatting
  const formatINR = (val: number) => `₹ ${val.toLocaleString('en-IN')}`;
  const getMonthName = (m: number) => [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ][m - 1] || `${m}`;

  // Employee CRUD
  const handleSaveEmployee = (e: React.FormEvent) => {
    e.preventDefault();
    if (!empForm.id?.trim() || !empForm.name?.trim()) {
      showAlert('Employee ID and Name are required.', 'error');
      return;
    }

    if (editingEmpId) {
      setEmployees(prev => prev.map(item => item.id === editingEmpId ? { ...item, ...(empForm as Employee), id: editingEmpId } : item));
      showAlert(`Employee ${editingEmpId} updated successfully.`, 'success');
      setEditingEmpId(null);
    } else {
      if (employees.some(item => item.id.toLowerCase() === empForm.id?.trim().toLowerCase())) {
        showAlert(`Employee ID ${empForm.id} already exists. Must be unique.`, 'error');
        return;
      }
      setEmployees(prev => [...prev, empForm as Employee]);
      showAlert(`Employee ${empForm.id} added successfully.`, 'success');
    }

    setEmpForm({
      id: '',
      name: '',
      department: DEPARTMENTS[0],
      designation: DESIGNATIONS[3],
      phone: '',
      email: '',
      joiningDate: '2024-06-01',
      basicSalary: 50000,
      overtimeRate: 350,
      allowances: 6000,
      deductions: 4000,
      status: 'Active'
    });
  };

  const handleEditEmployee = (emp: Employee) => {
    setEditingEmpId(emp.id);
    setEmpForm(emp);
  };

  const handleDeleteEmployee = (id: string) => {
    if (confirm(`Are you sure you want to delete employee ${id}?`)) {
      setEmployees(prev => prev.filter(e => e.id !== id));
      setAttendance(prev => prev.filter(a => a.employeeId !== id));
      setSalaries(prev => prev.filter(s => s.employeeId !== id));
      showAlert(`Employee ${id} deleted.`, 'info');
    }
  };

  // Attendance Save / Update
  const handleSaveAttendance = (e: React.FormEvent) => {
    e.preventDefault();
    if (attPresentDays + attLeaveDays > attTotalDays) {
      showAlert(`Validation Error: Days Present (${attPresentDays}) + Leave Days (${attLeaveDays}) exceeds Total Working Days (${attTotalDays}).`, 'error');
      return;
    }

    const existingIndex = attendance.findIndex(a => a.employeeId === attEmpId && a.month === attMonth && a.year === attYear);
    const newRecord: Attendance = {
      id: existingIndex >= 0 ? attendance[existingIndex].id : `att-${Date.now()}`,
      employeeId: attEmpId,
      month: attMonth,
      year: attYear,
      totalWorkingDays: attTotalDays,
      daysPresent: attPresentDays,
      leaveDays: attLeaveDays,
      overtimeHours: attOtHours
    };

    if (existingIndex >= 0) {
      const updated = [...attendance];
      updated[existingIndex] = newRecord;
      setAttendance(updated);
      showAlert(`Attendance updated for ${attEmpId} (${getMonthName(attMonth)} ${attYear}).`, 'success');
    } else {
      setAttendance(prev => [...prev, newRecord]);
      showAlert(`Attendance recorded for ${attEmpId} (${getMonthName(attMonth)} ${attYear}).`, 'success');
    }
  };

  // Salary Calculation
  const handleCalculateSalary = () => {
    const emp = employees.find(e => e.id === salEmpId);
    if (!emp) {
      showAlert('Selected employee does not exist.', 'error');
      return;
    }

    const att = attendance.find(a => a.employeeId === salEmpId && a.month === salMonth && a.year === salYear);
    if (!att) {
      showAlert(`No attendance recorded for ${emp.name} for ${getMonthName(salMonth)} ${salYear}. Record attendance first!`, 'error');
      return;
    }

    // Formulas:
    // Attendance Salary: Basic Salary / Total Working Days * Days Present
    // Overtime Pay: Overtime Hours * Overtime Rate
    // Gross Salary: Attendance Salary + Overtime Pay + Allowances
    // Net Salary: Gross Salary - Deductions
    const attSalary = Math.round((emp.basicSalary / att.totalWorkingDays) * att.daysPresent);
    const otPay = Math.round(att.overtimeHours * emp.overtimeRate);
    const gross = attSalary + otPay + emp.allowances;
    const net = gross - emp.deductions;

    const calc: SalaryRecord = {
      id: `sal-${salEmpId}-${salMonth}-${salYear}`,
      employeeId: salEmpId,
      month: salMonth,
      year: salYear,
      basicSalary: emp.basicSalary,
      totalWorkingDays: att.totalWorkingDays,
      daysPresent: att.daysPresent,
      leaveDays: att.leaveDays,
      overtimeHours: att.overtimeHours,
      overtimeRate: emp.overtimeRate,
      attendanceSalary: attSalary,
      overtimePay: otPay,
      allowances: emp.allowances,
      grossSalary: gross,
      deductions: emp.deductions,
      netSalary: net,
      calculatedDate: new Date().toISOString().split('T')[0]
    };

    setCalculatedSalary(calc);
    showAlert('Salary calculated successfully! Click Save Salary Record to finalize.', 'info');
  };

  const handleSaveSalary = () => {
    if (!calculatedSalary) return;
    setSalaries(prev => {
      const idx = prev.findIndex(s => s.employeeId === calculatedSalary.employeeId && s.month === calculatedSalary.month && s.year === calculatedSalary.year);
      if (idx >= 0) {
        const copy = [...prev];
        copy[idx] = calculatedSalary;
        return copy;
      }
      return [...prev, calculatedSalary];
    });
    showAlert(`Salary record saved for ${calculatedSalary.employeeId} (${getMonthName(calculatedSalary.month)} ${calculatedSalary.year}).`, 'success');
  };

  // Export to CSV
  const exportToCSV = (data: any[], filename: string) => {
    if (data.length === 0) {
      showAlert('No data to export.', 'error');
      return;
    }
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map(obj => Object.values(obj).map(val => `"${val}"`).join(','));
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers, ...rows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showAlert(`Exported ${filename} successfully.`, 'success');
  };

  // Download Python Project ZIP
  const handleDownloadPythonProject = async () => {
    showAlert('Preparing AIET Python Desktop Project ZIP (500-Employee Engine)...', 'info');
    try {
      const zip = new JSZip();
      const folder = zip.folder('employee_attendance_system');

      // Package all Python files from project
      for (const [path, content] of Object.entries(pythonSourceFiles)) {
        const fname = path.split('/').pop();
        if (fname && folder) {
          folder.file(fname, content);
        }
      }

      // Add Windows launcher & quick start guide
      folder?.file('requirements.txt', `openpyxl>=3.1.2\nreportlab>=4.0.0\nmatplotlib>=3.7.0\n`);
      folder?.file('README.txt', `AIET Employee Attendance & Salary Processing System\nAlvas Institute of Engineering and Technology, Moodbidri\n\nHOW TO RUN ON WINDOWS:\n1. Ensure Python 3 is installed (check python --version)\n2. Open Command Prompt in this folder\n3. Install dependencies:\n   pip install -r requirements.txt\n4. Run the application:\n   python main.py\n\nFeatures:\n- 500-employee SQLite institutional roster\n- Monthly attendance & overtime tracker\n- Automatic salary calculation (institutional formula)\n- Excel import/export (.xlsx / .csv)\n- ReportLab PDF salary slips\n`);

      const content = await zip.generateAsync({ type: 'blob' });
      const url = window.URL.createObjectURL(content);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'AIET_Employee_Attendance_Salary_System.zip';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showAlert('Python project ZIP downloaded successfully!', 'success');
    } catch (err) {
      showAlert('Failed to build ZIP.', 'error');
    }
  };

  // Filtered and paginated employees
  const filteredEmployees = employees.filter(e => {
    const matchesSearch = e.name.toLowerCase().includes(empSearch.toLowerCase()) ||
      e.id.toLowerCase().includes(empSearch.toLowerCase()) ||
      e.department.toLowerCase().includes(empSearch.toLowerCase());
    const matchesDept = empDeptFilter === 'All' || e.department === empDeptFilter;
    return matchesSearch && matchesDept;
  });

  const totalEmpPages = Math.max(1, Math.ceil(filteredEmployees.length / (empPageSize === -1 ? (filteredEmployees.length || 1) : empPageSize)));
  const currentSafeEmpPage = Math.min(empPage, totalEmpPages);
  const paginatedEmployees = empPageSize === -1
    ? filteredEmployees
    : filteredEmployees.slice((currentSafeEmpPage - 1) * empPageSize, currentSafeEmpPage * empPageSize);

  // Filtered and paginated attendance
  const filteredAttendance = attendance.filter(a => {
    const emp = employees.find(e => e.id === a.employeeId);
    const matchesSearch = a.employeeId.toLowerCase().includes(attSearch.toLowerCase()) ||
      (emp && emp.name.toLowerCase().includes(attSearch.toLowerCase())) ||
      (emp && emp.department.toLowerCase().includes(attSearch.toLowerCase()));
    const matchesDept = attDeptFilter === 'All' || (emp && emp.department === attDeptFilter);
    return matchesSearch && matchesDept;
  });

  const totalAttPages = Math.max(1, Math.ceil(filteredAttendance.length / (attPageSize === -1 ? (filteredAttendance.length || 1) : attPageSize)));
  const currentSafeAttPage = Math.min(attPage, totalAttPages);
  const paginatedAttendance = attPageSize === -1
    ? filteredAttendance
    : filteredAttendance.slice((currentSafeAttPage - 1) * attPageSize, currentSafeAttPage * attPageSize);

  // Filtered and paginated salary slips
  const filteredSalaries = salaries.filter(s => {
    const emp = employees.find(e => e.id === s.employeeId);
    const matchesSearch = s.employeeId.toLowerCase().includes(slipsSearch.toLowerCase()) ||
      (emp && emp.name.toLowerCase().includes(slipsSearch.toLowerCase())) ||
      (emp && emp.department.toLowerCase().includes(slipsSearch.toLowerCase()));
    const matchesDept = slipsDeptFilter === 'All' || (emp && emp.department === slipsDeptFilter);
    return matchesSearch && matchesDept;
  });

  const totalSlipsPages = Math.max(1, Math.ceil(filteredSalaries.length / (slipsPageSize === -1 ? (filteredSalaries.length || 1) : slipsPageSize)));
  const currentSafeSlipsPage = Math.min(slipsPage, totalSlipsPages);
  const paginatedSalaries = slipsPageSize === -1
    ? filteredSalaries
    : filteredSalaries.slice((currentSafeSlipsPage - 1) * slipsPageSize, currentSafeSlipsPage * slipsPageSize);

  // Selected employee data for salary processing view
  const currentSalEmployee = employees.find(e => e.id === salEmpId);
  const currentSalAttendance = attendance.find(a => a.employeeId === salEmpId && a.month === salMonth && a.year === salYear);

  return (
    <div id="aiet-system-root" className="flex flex-col h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Top Institutional Header */}
      <header className="bg-blue-900 text-white px-6 py-3 shadow-md flex items-center justify-between border-b border-blue-950">
        <div className="flex items-center space-x-4">
          <div className="bg-white/10 p-2.5 rounded-lg border border-white/20">
            <Building2 className="w-7 h-7 text-blue-200" />
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-bold tracking-tight">ALVAS INSTITUTE OF ENGINEERING AND TECHNOLOGY</h1>
            <p className="text-xs sm:text-sm text-blue-200">Employee Attendance &amp; Salary Processing System • Desktop &amp; Admin Suite</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-xs bg-blue-800 text-blue-100 font-medium px-2.5 py-1 rounded border border-blue-700">
            Local Desktop Engine: Python 3 + SQLite
          </span>
          <button
            onClick={handleDownloadPythonProject}
            className="flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-1.5 rounded transition shadow"
          >
            <FolderDown className="w-4 h-4" />
            <span>Download Python (.zip)</span>
          </button>
        </div>
      </header>

      {/* Main Content Area with Sidebar */}
      <div className="flex flex-1 overflow-hidden">
        {/* Navigation Sidebar */}
        <aside className="w-60 bg-slate-900 text-slate-200 flex flex-col justify-between shrink-0 shadow-inner">
          <nav className="p-3 space-y-1">
            <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">Navigation</div>
            {[
              { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
              { id: 'employees', label: 'Employees', icon: Users },
              { id: 'attendance', label: 'Attendance', icon: Calendar },
              { id: 'salary', label: 'Salary Processing', icon: DollarSign },
              { id: 'excel_upload', label: 'Upload Excel & Calc', icon: FileSpreadsheet },
              { id: 'slips', label: 'Salary Slips', icon: FileText },
              { id: 'reports', label: 'Reports', icon: FileSpreadsheet },
              { id: 'code', label: 'Python Source Code', icon: Code },
              { id: 'settings', label: 'Settings & Demo', icon: Settings },
            ].map(item => {
              const Icon = item.icon;
              const active = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id as any)}
                  className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-md text-sm font-medium transition ${
                    active ? 'bg-blue-800 text-white font-semibold shadow-sm' : 'hover:bg-slate-800 text-slate-300'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-blue-200' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
          <div className="p-4 bg-slate-950/60 border-t border-slate-800 text-xs text-slate-400 space-y-1">
            <div className="font-semibold text-slate-200">AIET Administration</div>
            <div>Moodbidri, Karnataka</div>
            <div className="text-[10px] text-slate-500 pt-1">v1.0.0 • SQLite3 Connected</div>
          </div>
        </aside>

        {/* Dynamic Center Work Area */}
        <main className="flex-1 overflow-y-auto p-6 bg-slate-100">
          {/* Global Alert Notification */}
          {alert && (
            <div
              className={`mb-4 px-4 py-3 rounded-lg border text-sm flex items-center justify-between shadow-sm ${
                alert.type === 'success'
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                  : alert.type === 'error'
                  ? 'bg-rose-50 border-rose-200 text-rose-800'
                  : 'bg-blue-50 border-blue-200 text-blue-800'
              }`}
            >
              <div className="flex items-center space-x-2">
                {alert.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4 text-rose-600" />}
                <span className="font-medium">{alert.msg}</span>
              </div>
              <button onClick={() => setAlert(null)} className="text-xs font-bold underline ml-4">Dismiss</button>
            </div>
          )}

          {/* 1. DASHBOARD VIEW */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-slate-800">Administrative Overview &amp; Payroll Summary</h2>
                  <p className="text-xs text-slate-500">Alvas Institute of Engineering and Technology • Pay Period: September 2026</p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setActiveTab('excel_upload')}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-2 rounded-md transition flex items-center space-x-1 shadow-xs"
                  >
                    <FileSpreadsheet className="w-3.5 h-3.5" />
                    <span>Upload Excel &amp; Calculate</span>
                  </button>
                  <button
                    onClick={() => setActiveTab('employees')}
                    className="bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold px-3 py-2 rounded-md transition flex items-center space-x-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Employee</span>
                  </button>
                  <button
                    onClick={() => setActiveTab('salary')}
                    className="bg-slate-700 hover:bg-slate-800 text-white text-xs font-semibold px-3 py-2 rounded-md transition flex items-center space-x-1"
                  >
                    <DollarSign className="w-3.5 h-3.5" />
                    <span>Run Payroll</span>
                  </button>
                </div>
              </div>

              {/* Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { title: 'TOTAL EMPLOYEES', value: employees.length, sub: 'Registered academic & admin staff', color: 'border-l-4 border-blue-600' },
                  { title: 'ACTIVE EMPLOYEES', value: employees.filter(e => e.status === 'Active').length, sub: 'Eligible for monthly payroll', color: 'border-l-4 border-emerald-600' },
                  { title: 'TOTAL DAYS PRESENT', value: attendance.reduce((acc, curr) => acc + curr.daysPresent, 0), sub: 'Staff days logged (Sept 2026)', color: 'border-l-4 border-teal-600' },
                  { title: 'TOTAL LEAVE DAYS', value: attendance.reduce((acc, curr) => acc + curr.leaveDays, 0), sub: 'Approved leaves (Sept 2026)', color: 'border-l-4 border-amber-600' },
                  { title: 'TOTAL SALARY (MONTH)', value: formatINR(salaries.reduce((acc, curr) => acc + curr.netSalary, 0)), sub: 'Net payable for September 2026', color: 'border-l-4 border-indigo-600' },
                  { title: 'TOTAL OVERTIME HOURS', value: `${attendance.reduce((acc, curr) => acc + curr.overtimeHours, 0)} hrs`, sub: 'Logged extra duty hours', color: 'border-l-4 border-purple-600' },
                ].map((card, i) => (
                  <div key={i} className={`bg-white p-4 rounded-xl border border-slate-200 shadow-sm ${card.color}`}>
                    <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">{card.title}</div>
                    <div className="text-2xl font-black text-slate-800 my-1">{card.value}</div>
                    <div className="text-xs text-slate-400">{card.sub}</div>
                  </div>
                ))}
              </div>

              {/* Departmental Table & Recent Salaries */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center space-x-2">
                    <Building2 className="w-4 h-4 text-blue-700" />
                    <span>Departmental Headcount Breakdown</span>
                  </h3>
                  <div className="divide-y divide-slate-100 text-xs">
                    {DEPARTMENTS.map(dept => {
                      const count = employees.filter(e => e.department === dept).length;
                      return (
                        <div key={dept} className="py-2.5 flex items-center justify-between">
                          <span className="font-medium text-slate-700">{dept}</span>
                          <span className="bg-slate-100 text-slate-800 font-bold px-2 py-0.5 rounded-full">{count} Staff</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center space-x-2">
                    <DollarSign className="w-4 h-4 text-emerald-600" />
                    <span>Recent Processed Salaries (Sept 2026)</span>
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="bg-slate-50 border-b border-slate-200 text-slate-600">
                          <th className="py-2 px-3">Emp ID</th>
                          <th className="py-2 px-3">Employee Name</th>
                          <th className="py-2 px-3 text-right">Net Salary</th>
                          <th className="py-2 px-3 text-center">Slip</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {salaries.slice(0, 5).map(sal => {
                          const emp = employees.find(e => e.id === sal.employeeId);
                          return (
                            <tr key={sal.id} className="hover:bg-slate-50">
                              <td className="py-2 px-3 font-semibold text-blue-800">{sal.employeeId}</td>
                              <td className="py-2 px-3">{emp?.name || sal.employeeId}</td>
                              <td className="py-2 px-3 text-right font-bold text-emerald-700">{formatINR(sal.netSalary)}</td>
                              <td className="py-2 px-3 text-center">
                                <button
                                  onClick={() => setSlipModalRecord(sal)}
                                  className="text-blue-700 hover:text-blue-900 font-semibold underline text-[11px]"
                                >
                                  View Slip
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 2. EMPLOYEE MANAGEMENT VIEW */}
          {activeTab === 'employees' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Form */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <h2 className="text-sm font-bold text-slate-800 mb-4 pb-2 border-b border-slate-100 flex items-center justify-between">
                    <span>{editingEmpId ? 'Update Employee' : 'Add New Employee'}</span>
                    {editingEmpId && (
                      <button
                        onClick={() => {
                          setEditingEmpId(null);
                          setEmpForm({
                            id: '',
                            name: '',
                            department: DEPARTMENTS[0],
                            designation: DESIGNATIONS[3],
                            phone: '',
                            email: '',
                            joiningDate: '2024-06-01',
                            basicSalary: 50000,
                            overtimeRate: 350,
                            allowances: 6000,
                            deductions: 4000,
                            status: 'Active'
                          });
                        }}
                        className="text-xs text-slate-500 hover:text-slate-800 font-medium"
                      >
                        Cancel Edit
                      </button>
                    )}
                  </h2>
                  <form onSubmit={handleSaveEmployee} className="space-y-3 text-xs">
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Employee ID *</label>
                      <input
                        type="text"
                        disabled={!!editingEmpId}
                        value={empForm.id || ''}
                        onChange={e => setEmpForm({ ...empForm, id: e.target.value })}
                        placeholder="e.g. AIET-CSE-103"
                        className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600 disabled:bg-slate-100"
                        required
                      />
                    </div>
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Full Name *</label>
                      <input
                        type="text"
                        value={empForm.name || ''}
                        onChange={e => setEmpForm({ ...empForm, name: e.target.value })}
                        placeholder="Faculty / Staff Full Name"
                        className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                        required
                      />
                    </div>
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Department *</label>
                      <select
                        value={empForm.department}
                        onChange={e => setEmpForm({ ...empForm, department: e.target.value })}
                        className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                      >
                        {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Designation *</label>
                      <select
                        value={empForm.designation}
                        onChange={e => setEmpForm({ ...empForm, designation: e.target.value })}
                        className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                      >
                        {DESIGNATIONS.map(d => <option key={d} value={d}>{d}</option>)}
                      </select>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Phone *</label>
                        <input
                          type="tel"
                          value={empForm.phone || ''}
                          onChange={e => setEmpForm({ ...empForm, phone: e.target.value })}
                          placeholder="9845xxxxxx"
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                          required
                        />
                      </div>
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Joining Date *</label>
                        <input
                          type="date"
                          value={empForm.joiningDate || ''}
                          onChange={e => setEmpForm({ ...empForm, joiningDate: e.target.value })}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Email *</label>
                      <input
                        type="email"
                        value={empForm.email || ''}
                        onChange={e => setEmpForm({ ...empForm, email: e.target.value })}
                        placeholder="staff@aiet.org.in"
                        className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                        required
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Basic Salary (₹) *</label>
                        <input
                          type="number"
                          min="0"
                          value={empForm.basicSalary ?? 0}
                          onChange={e => setEmpForm({ ...empForm, basicSalary: parseFloat(e.target.value) || 0 })}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                          required
                        />
                      </div>
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">OT Rate (₹/hr)</label>
                        <input
                          type="number"
                          min="0"
                          value={empForm.overtimeRate ?? 0}
                          onChange={e => setEmpForm({ ...empForm, overtimeRate: parseFloat(e.target.value) || 0 })}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Allowances (₹)</label>
                        <input
                          type="number"
                          min="0"
                          value={empForm.allowances ?? 0}
                          onChange={e => setEmpForm({ ...empForm, allowances: parseFloat(e.target.value) || 0 })}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                        />
                      </div>
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Deductions (₹)</label>
                        <input
                          type="number"
                          min="0"
                          value={empForm.deductions ?? 0}
                          onChange={e => setEmpForm({ ...empForm, deductions: parseFloat(e.target.value) || 0 })}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Status</label>
                      <select
                        value={empForm.status}
                        onChange={e => setEmpForm({ ...empForm, status: e.target.value as any })}
                        className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                      >
                        <option value="Active">Active</option>
                        <option value="Inactive">Inactive</option>
                      </select>
                    </div>
                    <div className="pt-2 flex items-center space-x-2">
                      <button
                        type="submit"
                        className="flex-1 bg-blue-700 hover:bg-blue-800 text-white font-semibold py-2 rounded-md transition shadow text-xs"
                      >
                        {editingEmpId ? 'Save Changes' : 'Add Employee'}
                      </button>
                    </div>
                  </form>
                </div>

                {/* Table */}
                <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                    <div className="flex items-center space-x-2 flex-1">
                      <div className="relative flex-1 max-w-xs">
                        <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
                        <input
                          type="text"
                          value={empSearch}
                          onChange={e => {
                            setEmpSearch(e.target.value);
                            setEmpPage(1);
                          }}
                          placeholder="Search ID, name, dept..."
                          className="w-full pl-9 pr-3 py-1.5 border border-slate-300 rounded-md text-xs focus:ring-2 focus:ring-blue-600"
                        />
                      </div>
                      <select
                        value={empDeptFilter}
                        onChange={e => {
                          setEmpDeptFilter(e.target.value);
                          setEmpPage(1);
                        }}
                        className="border border-slate-300 rounded-md px-2 py-1.5 text-xs bg-white text-slate-700 focus:ring-2 focus:ring-blue-600"
                      >
                        <option value="All">All Departments</option>
                        {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
                      </select>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => exportToCSV(employees, 'AIET_Employees_Directory.csv')}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-1.5 rounded transition flex items-center space-x-1"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Export CSV</span>
                      </button>
                      <span className="text-xs text-slate-500 font-medium">
                        Total: {filteredEmployees.length}
                      </span>
                    </div>
                  </div>

                  <div className="overflow-x-auto flex-1">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="bg-slate-100 border-b border-slate-200 text-slate-700">
                          <th className="py-2.5 px-3">Emp ID</th>
                          <th className="py-2.5 px-3">Name</th>
                          <th className="py-2.5 px-3">Department</th>
                          <th className="py-2.5 px-3">Designation</th>
                          <th className="py-2.5 px-3 text-right">Basic (₹)</th>
                          <th className="py-2.5 px-3 text-center">Status</th>
                          <th className="py-2.5 px-3 text-center">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {paginatedEmployees.length === 0 ? (
                          <tr>
                            <td colSpan={7} className="py-8 text-center text-slate-400 text-xs">
                              No employees found matching the filter criteria.
                            </td>
                          </tr>
                        ) : (
                          paginatedEmployees.map(emp => (
                            <tr key={emp.id} className="hover:bg-slate-50">
                              <td className="py-2.5 px-3 font-semibold text-blue-900">{emp.id}</td>
                              <td className="py-2.5 px-3 font-medium text-slate-800">{emp.name}</td>
                              <td className="py-2.5 px-3 text-slate-600">{emp.department}</td>
                              <td className="py-2.5 px-3 text-slate-600">{emp.designation}</td>
                              <td className="py-2.5 px-3 text-right font-medium">{formatINR(emp.basicSalary)}</td>
                              <td className="py-2.5 px-3 text-center">
                                <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
                                  emp.status === 'Active' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                                }`}>
                                  {emp.status}
                                </span>
                              </td>
                              <td className="py-2.5 px-3 text-center space-x-2">
                                <button
                                  onClick={() => handleEditEmployee(emp)}
                                  className="text-blue-600 hover:text-blue-800 p-1"
                                  title="Edit"
                                >
                                  <Edit className="w-3.5 h-3.5 inline" />
                                </button>
                                <button
                                  onClick={() => handleDeleteEmployee(emp.id)}
                                  className="text-rose-600 hover:text-rose-800 p-1"
                                  title="Delete"
                                >
                                  <Trash2 className="w-3.5 h-3.5 inline" />
                                </button>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination Bar */}
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600 pt-3 border-t border-slate-100 mt-2">
                    <div className="flex items-center space-x-3">
                      <span>
                        Showing {filteredEmployees.length === 0 ? 0 : (currentSafeEmpPage - 1) * (empPageSize === -1 ? filteredEmployees.length : empPageSize) + 1} to{' '}
                        {empPageSize === -1 ? filteredEmployees.length : Math.min(currentSafeEmpPage * empPageSize, filteredEmployees.length)} of {filteredEmployees.length}
                      </span>
                      <div className="flex items-center space-x-1 pl-2 border-l border-slate-200">
                        <span className="text-[11px] text-slate-500">Rows:</span>
                        <select
                          value={empPageSize}
                          onChange={e => {
                            setEmpPageSize(Number(e.target.value));
                            setEmpPage(1);
                          }}
                          className="border border-slate-200 rounded px-1.5 py-0.5 text-xs bg-white"
                        >
                          <option value={15}>15</option>
                          <option value={25}>25</option>
                          <option value={50}>50</option>
                          <option value={100}>100</option>
                          <option value={-1}>All ({employees.length})</option>
                        </select>
                      </div>
                    </div>

                    {totalEmpPages > 1 && (
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => setEmpPage(1)}
                          disabled={currentSafeEmpPage === 1}
                          className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                        >
                          «
                        </button>
                        <button
                          onClick={() => setEmpPage(p => Math.max(1, p - 1))}
                          disabled={currentSafeEmpPage === 1}
                          className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                        >
                          ‹
                        </button>
                        <span className="px-2 py-1 bg-slate-100 font-semibold rounded text-xs">
                          {currentSafeEmpPage} / {totalEmpPages}
                        </span>
                        <button
                          onClick={() => setEmpPage(p => Math.min(totalEmpPages, p + 1))}
                          disabled={currentSafeEmpPage === totalEmpPages}
                          className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                        >
                          ›
                        </button>
                        <button
                          onClick={() => setEmpPage(totalEmpPages)}
                          disabled={currentSafeEmpPage === totalEmpPages}
                          className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                        >
                          »
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 3. ATTENDANCE VIEW */}
          {activeTab === 'attendance' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Form */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <h2 className="text-sm font-bold text-slate-800 mb-4 pb-2 border-b border-slate-100">
                    Record Monthly Attendance &amp; Overtime
                  </h2>
                  <form onSubmit={handleSaveAttendance} className="space-y-3.5 text-xs">
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Select Employee *</label>
                      <select
                        value={attEmpId}
                        onChange={e => {
                          setAttEmpId(e.target.value);
                          const existing = attendance.find(a => a.employeeId === e.target.value && a.month === attMonth && a.year === attYear);
                          if (existing) {
                            setAttTotalDays(existing.totalWorkingDays);
                            setAttPresentDays(existing.daysPresent);
                            setAttLeaveDays(existing.leaveDays);
                            setAttOtHours(existing.overtimeHours);
                          }
                        }}
                        className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                      >
                        {employees.map(e => (
                          <option key={e.id} value={e.id}>{e.id} - {e.name}</option>
                        ))}
                      </select>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Month *</label>
                        <select
                          value={attMonth}
                          onChange={e => setAttMonth(parseInt(e.target.value))}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                        >
                          {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
                            <option key={m} value={m}>{m} - {getMonthName(m)}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Year *</label>
                        <input
                          type="number"
                          value={attYear}
                          onChange={e => setAttYear(parseInt(e.target.value) || 2026)}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Total Working Days in Month *</label>
                      <input
                        type="number"
                        min="1"
                        max="31"
                        value={attTotalDays}
                        onChange={e => setAttTotalDays(parseInt(e.target.value) || 0)}
                        className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                        required
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Days Present *</label>
                        <input
                          type="number"
                          min="0"
                          max={attTotalDays}
                          value={attPresentDays}
                          onChange={e => setAttPresentDays(parseInt(e.target.value) || 0)}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                          required
                        />
                      </div>
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Leave Days *</label>
                        <input
                          type="number"
                          min="0"
                          max={attTotalDays}
                          value={attLeaveDays}
                          onChange={e => setAttLeaveDays(parseInt(e.target.value) || 0)}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Overtime Hours (hrs)</label>
                      <input
                        type="number"
                        min="0"
                        step="0.5"
                        value={attOtHours}
                        onChange={e => setAttOtHours(parseFloat(e.target.value) || 0)}
                        className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                      />
                    </div>
                    <div className="p-2.5 bg-blue-50 border border-blue-200 rounded text-[11px] text-blue-800">
                      Rule check: {attPresentDays} present + {attLeaveDays} leave = {attPresentDays + attLeaveDays} days (Total: {attTotalDays})
                    </div>
                    <button
                      type="submit"
                      className="w-full bg-blue-700 hover:bg-blue-800 text-white font-semibold py-2 rounded-md transition shadow text-xs"
                    >
                      Save Attendance
                    </button>
                  </form>
                </div>

                {/* Attendance Table */}
                <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                    <div className="flex items-center space-x-2 flex-1">
                      <div className="relative flex-1 max-w-xs">
                        <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
                        <input
                          type="text"
                          value={attSearch}
                          onChange={e => {
                            setAttSearch(e.target.value);
                            setAttPage(1);
                          }}
                          placeholder="Search ID, name, dept..."
                          className="w-full pl-9 pr-3 py-1.5 border border-slate-300 rounded-md text-xs focus:ring-2 focus:ring-blue-600"
                        />
                      </div>
                      <select
                        value={attDeptFilter}
                        onChange={e => {
                          setAttDeptFilter(e.target.value);
                          setAttPage(1);
                        }}
                        className="border border-slate-300 rounded-md px-2 py-1.5 text-xs bg-white text-slate-700 focus:ring-2 focus:ring-blue-600"
                      >
                        <option value="All">All Departments</option>
                        {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
                      </select>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => exportToCSV(attendance, 'AIET_Attendance_Register.csv')}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-1.5 rounded transition flex items-center space-x-1"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Export CSV</span>
                      </button>
                      <span className="text-xs text-slate-500 font-medium">
                        Total: {filteredAttendance.length}
                      </span>
                    </div>
                  </div>
                  <div className="overflow-x-auto flex-1">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="bg-slate-100 border-b border-slate-200 text-slate-700">
                          <th className="py-2.5 px-3">Emp ID</th>
                          <th className="py-2.5 px-3">Employee Name</th>
                          <th className="py-2.5 px-3">Department</th>
                          <th className="py-2.5 px-3 text-center">Period</th>
                          <th className="py-2.5 px-3 text-center">Working Days</th>
                          <th className="py-2.5 px-3 text-center">Present</th>
                          <th className="py-2.5 px-3 text-center">Leave</th>
                          <th className="py-2.5 px-3 text-center">OT Hours</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {paginatedAttendance.length === 0 ? (
                          <tr>
                            <td colSpan={8} className="py-8 text-center text-slate-400 text-xs">
                              No attendance records found matching criteria.
                            </td>
                          </tr>
                        ) : (
                          paginatedAttendance.map(att => {
                            const emp = employees.find(e => e.id === att.employeeId);
                            return (
                              <tr key={att.id} className="hover:bg-slate-50">
                                <td className="py-2.5 px-3 font-semibold text-blue-900">{att.employeeId}</td>
                                <td className="py-2.5 px-3 font-medium text-slate-800">{emp?.name || att.employeeId}</td>
                                <td className="py-2.5 px-3 text-slate-600">{emp?.department || '-'}</td>
                                <td className="py-2.5 px-3 text-center text-slate-600">{getMonthName(att.month)} {att.year}</td>
                                <td className="py-2.5 px-3 text-center">{att.totalWorkingDays}</td>
                                <td className="py-2.5 px-3 text-center font-semibold text-emerald-700">{att.daysPresent}</td>
                                <td className="py-2.5 px-3 text-center font-semibold text-rose-600">{att.leaveDays}</td>
                                <td className="py-2.5 px-3 text-center text-purple-700 font-semibold">{att.overtimeHours} hrs</td>
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Attendance Pagination Bar */}
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600 pt-3 border-t border-slate-100 mt-2">
                    <div className="flex items-center space-x-3">
                      <span>
                        Showing {filteredAttendance.length === 0 ? 0 : (currentSafeAttPage - 1) * (attPageSize === -1 ? filteredAttendance.length : attPageSize) + 1} to{' '}
                        {attPageSize === -1 ? filteredAttendance.length : Math.min(currentSafeAttPage * attPageSize, filteredAttendance.length)} of {filteredAttendance.length}
                      </span>
                      <div className="flex items-center space-x-1 pl-2 border-l border-slate-200">
                        <span className="text-[11px] text-slate-500">Rows:</span>
                        <select
                          value={attPageSize}
                          onChange={e => {
                            setAttPageSize(Number(e.target.value));
                            setAttPage(1);
                          }}
                          className="border border-slate-200 rounded px-1.5 py-0.5 text-xs bg-white"
                        >
                          <option value={15}>15</option>
                          <option value={25}>25</option>
                          <option value={50}>50</option>
                          <option value={100}>100</option>
                          <option value={-1}>All ({attendance.length})</option>
                        </select>
                      </div>
                    </div>

                    {totalAttPages > 1 && (
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => setAttPage(1)}
                          disabled={currentSafeAttPage === 1}
                          className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                        >
                          «
                        </button>
                        <button
                          onClick={() => setAttPage(p => Math.max(1, p - 1))}
                          disabled={currentSafeAttPage === 1}
                          className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                        >
                          ‹
                        </button>
                        <span className="px-2 py-1 bg-slate-100 font-semibold rounded text-xs">
                          {currentSafeAttPage} / {totalAttPages}
                        </span>
                        <button
                          onClick={() => setAttPage(p => Math.min(totalAttPages, p + 1))}
                          disabled={currentSafeAttPage === totalAttPages}
                          className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                        >
                          ›
                        </button>
                        <button
                          onClick={() => setAttPage(totalAttPages)}
                          disabled={currentSafeAttPage === totalAttPages}
                          className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                        >
                          »
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 4. SALARY PROCESSING VIEW */}
          {activeTab === 'salary' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Selection & Calculation Panel */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
                  <h2 className="text-sm font-bold text-slate-800 pb-2 border-b border-slate-100">
                    Salary Processing &amp; Calculation Engine
                  </h2>
                  <div className="space-y-3 text-xs">
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Select Employee *</label>
                      <select
                        value={salEmpId}
                        onChange={e => {
                          setSalEmpId(e.target.value);
                          setCalculatedSalary(null);
                        }}
                        className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                      >
                        {employees.map(e => (
                          <option key={e.id} value={e.id}>{e.id} - {e.name}</option>
                        ))}
                      </select>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Month *</label>
                        <select
                          value={salMonth}
                          onChange={e => {
                            setSalMonth(parseInt(e.target.value));
                            setCalculatedSalary(null);
                          }}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                        >
                          {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
                            <option key={m} value={m}>{m} - {getMonthName(m)}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block font-medium text-slate-700 mb-1">Year *</label>
                        <input
                          type="number"
                          value={salYear}
                          onChange={e => {
                            setSalYear(parseInt(e.target.value) || 2026);
                            setCalculatedSalary(null);
                          }}
                          className="w-full border border-slate-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-600"
                        />
                      </div>
                    </div>

                    {/* Quick Employee Summary Badge */}
                    {currentSalEmployee && (
                      <div className="p-3 bg-slate-50 border border-slate-200 rounded-md space-y-1">
                        <div className="font-bold text-slate-800">{currentSalEmployee.name}</div>
                        <div className="text-slate-500">{currentSalEmployee.designation} • {currentSalEmployee.department}</div>
                        <div className="text-slate-600">Basic: <span className="font-semibold">{formatINR(currentSalEmployee.basicSalary)}</span></div>
                        <div className="text-slate-600">OT Rate: <span className="font-semibold">{formatINR(currentSalEmployee.overtimeRate)}/hr</span></div>
                      </div>
                    )}

                    {/* Attendance Info Badge */}
                    <div className={`p-3 rounded-md border ${
                      currentSalAttendance ? 'bg-emerald-50 border-emerald-200 text-emerald-900' : 'bg-rose-50 border-rose-200 text-rose-900'
                    }`}>
                      {currentSalAttendance ? (
                        <div>
                          <div className="font-bold">✓ Attendance Verified</div>
                          <div>Working Days: {currentSalAttendance.totalWorkingDays} | Present: {currentSalAttendance.daysPresent} | Leave: {currentSalAttendance.leaveDays}</div>
                          <div>Overtime: {currentSalAttendance.overtimeHours} hrs</div>
                        </div>
                      ) : (
                        <div>
                          <div className="font-bold">⚠ No Attendance Record</div>
                          <div className="text-[11px]">Please log attendance for this employee and period before calculating.</div>
                        </div>
                      )}
                    </div>

                    <button
                      onClick={handleCalculateSalary}
                      disabled={!currentSalAttendance}
                      className="w-full bg-blue-700 hover:bg-blue-800 disabled:bg-slate-300 text-white font-bold py-2.5 rounded-md transition shadow text-xs flex items-center justify-center space-x-2"
                    >
                      <DollarSign className="w-4 h-4" />
                      <span>Calculate Salary</span>
                    </button>

                    {calculatedSalary && (
                      <button
                        onClick={handleSaveSalary}
                        className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 rounded-md transition shadow text-xs flex items-center justify-center space-x-2"
                      >
                        <CheckCircle className="w-4 h-4" />
                        <span>Save Salary Record</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Breakdown Display */}
                <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-slate-800 pb-2 border-b border-slate-100 mb-4">
                      Salary Components &amp; Verified Breakdown
                    </h3>

                    {calculatedSalary || salaries.find(s => s.employeeId === salEmpId && s.month === salMonth && s.year === salYear) ? (
                      (() => {
                        const rec = calculatedSalary || salaries.find(s => s.employeeId === salEmpId && s.month === salMonth && s.year === salYear)!;
                        return (
                          <div className="space-y-4 text-xs">
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <span className="text-slate-500 block">Attendance Salary</span>
                                <span className="text-sm font-bold text-slate-800">{formatINR(rec.attendanceSalary)}</span>
                              </div>
                              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <span className="text-slate-500 block">Overtime Pay</span>
                                <span className="text-sm font-bold text-purple-700">{formatINR(rec.overtimePay)}</span>
                              </div>
                              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <span className="text-slate-500 block">Allowances</span>
                                <span className="text-sm font-bold text-teal-700">{formatINR(rec.allowances)}</span>
                              </div>
                              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <span className="text-slate-500 block">Deductions</span>
                                <span className="text-sm font-bold text-rose-700">-{formatINR(rec.deductions)}</span>
                              </div>
                            </div>

                            <div className="p-4 bg-blue-900 text-white rounded-xl shadow flex items-center justify-between">
                              <div>
                                <span className="text-xs text-blue-200 uppercase tracking-wider font-semibold">Gross Salary</span>
                                <div className="text-xl font-bold">{formatINR(rec.grossSalary)}</div>
                              </div>
                              <div className="text-right">
                                <span className="text-xs text-emerald-300 uppercase tracking-wider font-semibold">Net Payable Salary</span>
                                <div className="text-2xl font-black text-emerald-400">{formatINR(rec.netSalary)}</div>
                              </div>
                            </div>

                            <div className="border border-slate-200 rounded-lg p-3 bg-slate-50 space-y-1">
                              <div className="font-semibold text-slate-700">Formal AIET Payroll Formula Verification:</div>
                              <div className="text-slate-600 font-mono text-[11px]">
                                • Attendance Salary = (₹{rec.basicSalary} / {rec.totalWorkingDays}) × {rec.daysPresent} = ₹{rec.attendanceSalary}
                              </div>
                              <div className="text-slate-600 font-mono text-[11px]">
                                • Overtime Pay = {rec.overtimeHours} hrs × ₹{rec.overtimeRate} = ₹{rec.overtimePay}
                              </div>
                              <div className="text-slate-600 font-mono text-[11px]">
                                • Gross Salary = ₹{rec.attendanceSalary} + ₹{rec.overtimePay} + ₹{rec.allowances} = ₹{rec.grossSalary}
                              </div>
                              <div className="text-slate-600 font-mono text-[11px]">
                                • Net Salary = ₹{rec.grossSalary} - ₹{rec.deductions} = ₹{rec.netSalary}
                              </div>
                            </div>

                            <div className="pt-2 flex items-center space-x-3">
                              <button
                                onClick={() => setSlipModalRecord(rec)}
                                className="bg-purple-700 hover:bg-purple-800 text-white font-semibold px-4 py-2 rounded-md transition text-xs flex items-center space-x-1.5"
                              >
                                <FileText className="w-4 h-4" />
                                <span>Preview / Print Salary Slip</span>
                              </button>
                            </div>
                          </div>
                        );
                      })()
                    ) : (
                      <div className="py-16 text-center text-slate-400 text-xs">
                        Select an employee and click &quot;Calculate Salary&quot; to compute exact payroll figures.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 4b. EXCEL UPLOAD & CALCULATION VIEW */}
          {activeTab === 'excel_upload' && (
            <ExcelUploadView
              employees={employees}
              setEmployees={setEmployees}
              attendance={attendance}
              setAttendance={setAttendance}
              salaries={salaries}
              setSalaries={setSalaries}
              showAlert={showAlert}
              onNavigateToTab={(tab: string) => setActiveTab(tab as any)}
            />
          )}

          {/* 5. SALARY SLIPS VIEW */}
          {activeTab === 'slips' && (
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                <div>
                  <h2 className="text-sm font-bold text-slate-800">Generated Monthly Salary Slips</h2>
                  <p className="text-xs text-slate-500">Official AIET Salary Slips with Earnings, Deductions &amp; Authorizations</p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => exportToCSV(salaries, 'AIET_Salary_Slips_Register.csv')}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-1.5 rounded transition flex items-center space-x-1"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export All Slips (CSV)</span>
                  </button>
                  <span className="text-xs text-slate-500 font-medium">
                    Total: {filteredSalaries.length}
                  </span>
                </div>
              </div>

              {/* Slips Filter Bar */}
              <div className="flex flex-col sm:flex-row items-center gap-3">
                <div className="relative flex-1 max-w-xs">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    value={slipsSearch}
                    onChange={e => {
                      setSlipsSearch(e.target.value);
                      setSlipsPage(1);
                    }}
                    placeholder="Search ID, name, dept..."
                    className="w-full pl-9 pr-3 py-1.5 border border-slate-300 rounded-md text-xs focus:ring-2 focus:ring-blue-600"
                  />
                </div>
                <select
                  value={slipsDeptFilter}
                  onChange={e => {
                    setSlipsDeptFilter(e.target.value);
                    setSlipsPage(1);
                  }}
                  className="border border-slate-300 rounded-md px-2 py-1.5 text-xs bg-white text-slate-700 focus:ring-2 focus:ring-blue-600"
                >
                  <option value="All">All Departments</option>
                  {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-100 border-b border-slate-200 text-slate-700">
                      <th className="py-2.5 px-3">Emp ID</th>
                      <th className="py-2.5 px-3">Name</th>
                      <th className="py-2.5 px-3">Department</th>
                      <th className="py-2.5 px-3 text-center">Period</th>
                      <th className="py-2.5 px-3 text-right">Gross (₹)</th>
                      <th className="py-2.5 px-3 text-right">Deductions (₹)</th>
                      <th className="py-2.5 px-3 text-right font-bold text-emerald-800">Net Salary (₹)</th>
                      <th className="py-2.5 px-3 text-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {paginatedSalaries.length === 0 ? (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-400 text-xs">
                          No salary records found matching criteria.
                        </td>
                      </tr>
                    ) : (
                      paginatedSalaries.map(sal => {
                        const emp = employees.find(e => e.id === sal.employeeId);
                        return (
                          <tr key={sal.id} className="hover:bg-slate-50">
                            <td className="py-2.5 px-3 font-semibold text-blue-900">{sal.employeeId}</td>
                            <td className="py-2.5 px-3 font-medium text-slate-800">{emp?.name || sal.employeeId}</td>
                            <td className="py-2.5 px-3 text-slate-600">{emp?.department}</td>
                            <td className="py-2.5 px-3 text-center text-slate-600">{getMonthName(sal.month)} {sal.year}</td>
                            <td className="py-2.5 px-3 text-right">{formatINR(sal.grossSalary)}</td>
                            <td className="py-2.5 px-3 text-right text-rose-700">-{formatINR(sal.deductions)}</td>
                            <td className="py-2.5 px-3 text-right font-bold text-emerald-700">{formatINR(sal.netSalary)}</td>
                            <td className="py-2.5 px-3 text-center">
                              <button
                                onClick={() => setSlipModalRecord(sal)}
                                className="bg-blue-800 hover:bg-blue-900 text-white font-semibold px-2.5 py-1 rounded text-[11px] transition inline-flex items-center space-x-1"
                              >
                                <FileText className="w-3 h-3" />
                                <span>View Slip</span>
                              </button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>

              {/* Slips Pagination Bar */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600 pt-3 border-t border-slate-100 mt-2">
                <div className="flex items-center space-x-3">
                  <span>
                    Showing {filteredSalaries.length === 0 ? 0 : (currentSafeSlipsPage - 1) * (slipsPageSize === -1 ? filteredSalaries.length : slipsPageSize) + 1} to{' '}
                    {slipsPageSize === -1 ? filteredSalaries.length : Math.min(currentSafeSlipsPage * slipsPageSize, filteredSalaries.length)} of {filteredSalaries.length}
                  </span>
                  <div className="flex items-center space-x-1 pl-2 border-l border-slate-200">
                    <span className="text-[11px] text-slate-500">Rows:</span>
                    <select
                      value={slipsPageSize}
                      onChange={e => {
                        setSlipsPageSize(Number(e.target.value));
                        setSlipsPage(1);
                      }}
                      className="border border-slate-200 rounded px-1.5 py-0.5 text-xs bg-white"
                    >
                      <option value={15}>15</option>
                      <option value={25}>25</option>
                      <option value={50}>50</option>
                      <option value={100}>100</option>
                      <option value={-1}>All ({salaries.length})</option>
                    </select>
                  </div>
                </div>

                {totalSlipsPages > 1 && (
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => setSlipsPage(1)}
                      disabled={currentSafeSlipsPage === 1}
                      className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                    >
                      «
                    </button>
                    <button
                      onClick={() => setSlipsPage(p => Math.max(1, p - 1))}
                      disabled={currentSafeSlipsPage === 1}
                      className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                    >
                      ‹
                    </button>
                    <span className="px-2 py-1 bg-slate-100 font-semibold rounded text-xs">
                      {currentSafeSlipsPage} / {totalSlipsPages}
                    </span>
                    <button
                      onClick={() => setSlipsPage(p => Math.min(totalSlipsPages, p + 1))}
                      disabled={currentSafeSlipsPage === totalSlipsPages}
                      className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                    >
                      ›
                    </button>
                    <button
                      onClick={() => setSlipsPage(totalSlipsPages)}
                      disabled={currentSafeSlipsPage === totalSlipsPages}
                      className="px-2 py-1 border border-slate-200 rounded bg-white hover:bg-slate-50 disabled:opacity-40 text-[11px]"
                    >
                      »
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 6. REPORTS VIEW */}
          {activeTab === 'reports' && (
            <div className="space-y-6">
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-bold text-slate-800">Administrative Reports &amp; Analytics</h2>
                  <p className="text-xs text-slate-500">Alvas Institute of Engineering and Technology</p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => exportToCSV(employees, 'AIET_Employee_Directory.csv')}
                    className="bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold px-3 py-1.5 rounded transition"
                  >
                    Export Employees (CSV)
                  </button>
                  <button
                    onClick={() => exportToCSV(salaries, 'AIET_Monthly_Payroll_Report.csv')}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-1.5 rounded transition"
                  >
                    Export Salary Report (CSV)
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-800 mb-3">1. Employee Department Distribution</h3>
                  <div className="space-y-2 text-xs">
                    {DEPARTMENTS.map(dept => {
                      const count = employees.filter(e => e.department === dept).length;
                      const pct = Math.round((count / (employees.length || 1)) * 100);
                      return (
                        <div key={dept} className="space-y-1">
                          <div className="flex justify-between font-medium text-slate-700">
                            <span>{dept}</span>
                            <span>{count} staff ({pct}%)</span>
                          </div>
                          <div className="w-full bg-slate-100 rounded-full h-2">
                            <div className="bg-blue-700 h-2 rounded-full" style={{ width: `${pct}%` }}></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-800 mb-3">2. Overtime Hours Contribution</h3>
                  <div className="space-y-3 text-xs">
                    {salaries.filter(s => s.overtimeHours > 0).map(s => {
                      const emp = employees.find(e => e.id === s.employeeId);
                      return (
                        <div key={s.id} className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                          <div>
                            <div className="font-bold text-slate-800">{emp?.name}</div>
                            <div className="text-slate-500">{emp?.department} • {s.overtimeHours} hrs @ {formatINR(s.overtimeRate)}/hr</div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-purple-800">{formatINR(s.overtimePay)}</div>
                            <div className="text-[10px] text-slate-400">OT Pay</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 7. PYTHON SOURCE CODE BROWSER & DOWNLOAD */}
          {activeTab === 'code' && (
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div>
                  <h2 className="text-sm font-bold text-slate-800">Python Desktop Software Source Code</h2>
                  <p className="text-xs text-slate-500">Standalone Tkinter + SQLite application for Alvas Institute of Engineering and Technology</p>
                </div>
                <button
                  onClick={handleDownloadPythonProject}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-4 py-2 rounded-md transition flex items-center space-x-1.5 shadow"
                >
                  <FolderDown className="w-4 h-4" />
                  <span>Download Project as ZIP</span>
                </button>
              </div>

              <div className="p-4 bg-slate-900 text-slate-100 rounded-lg text-xs font-mono overflow-x-auto space-y-2">
                <div className="text-emerald-400 font-bold"># Windows Execution Guide for College Demonstration:</div>
                <div>1. Unzip the project folder: <span className="text-amber-300">employee_attendance_system/</span></div>
                <div>2. Open Command Prompt inside that directory:</div>
                <div className="text-blue-300 bg-slate-800/80 p-2 rounded">
                  pip install -r requirements.txt<br />
                  python main.py
                </div>
                <div className="text-slate-400 pt-2"># Modules Included:</div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-slate-300 pt-1">
                  <div>• main.py (Tkinter GUI shell)</div>
                  <div>• database.py (SQLite3 connection &amp; schema)</div>
                  <div>• models.py (Data access &amp; formulas)</div>
                  <div>• employee.py (CRUD Frame &amp; Treeview)</div>
                  <div>• attendance.py (Attendance &amp; Overtime)</div>
                  <div>• salary.py (Payroll calculation)</div>
                  <div>• excel_import.py (Excel/CSV Parser &amp; Batch Calc)</div>
                  <div>• excel_upload_screen.py (Tkinter Upload GUI)</div>
                  <div>• pdf_generator.py (ReportLab Salary Slips)</div>
                  <div>• excel_export.py (openpyxl Excel exports)</div>
                  <div>• reports.py (Analytics &amp; Matplotlib chart)</div>
                  <div>• utils.py (Input validators)</div>
                </div>
              </div>
            </div>
          )}

          {/* 8. SETTINGS & DEMO VIEW */}
          {activeTab === 'settings' && (
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-5">
              <h2 className="text-sm font-bold text-slate-800 pb-2 border-b border-slate-100">
                System Settings &amp; Demonstration Helpers
              </h2>
              <div className="space-y-4 text-xs">
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-2">
                  <h3 className="font-bold text-slate-800">Demonstration Reset</h3>
                  <p className="text-slate-600">Restore factory sample employees and attendance records for AIET departments.</p>
                  <button
                    onClick={() => {
                      setEmployees(INITIAL_500_EMPLOYEES);
                      setAttendance(INITIAL_500_ATTENDANCE);
                      setSalaries(INITIAL_500_SALARIES);
                      showAlert('AIET 500 employee demonstration records re-loaded successfully.', 'success');
                    }}
                    className="bg-blue-700 hover:bg-blue-800 text-white font-semibold px-3 py-1.5 rounded transition inline-flex items-center space-x-1.5"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Reload AIET 500-Employee Sample Data</span>
                  </button>
                </div>

                <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-1 text-slate-600">
                  <div className="font-bold text-slate-800">Institution Information:</div>
                  <div>Alvas Institute of Engineering and Technology (AIET)</div>
                  <div>Shobhavana Campus, Mijar, Moodbidri, Dakshina Kannada, Karnataka - 574227</div>
                  <div>Affiliated to Visvesvaraya Technological University (VTU), Belagavi</div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Salary Slip Modal Preview */}
      {slipModalRecord && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6 text-slate-800 max-h-[90vh] overflow-y-auto">
            {/* Slip Header */}
            <div className="text-center border-b-2 border-blue-900 pb-3 mb-4">
              <h2 className="text-lg font-black text-blue-950 uppercase tracking-tight">ALVAS INSTITUTE OF ENGINEERING AND TECHNOLOGY</h2>
              <p className="text-xs text-slate-600">Shobhavana Campus, Mijar, Moodbidri, D.K., Karnataka - 574227</p>
              <p className="text-xs text-slate-500">Affiliated to VTU Belagavi &amp; Approved by AICTE New Delhi</p>
              <div className="mt-2 inline-block bg-blue-100 text-blue-900 font-bold text-xs px-3 py-1 rounded">
                EMPLOYEE SALARY SLIP — {getMonthName(slipModalRecord.month).toUpperCase()} {slipModalRecord.year}
              </div>
            </div>

            {/* Employee Details Grid */}
            {(() => {
              const emp = employees.find(e => e.id === slipModalRecord.employeeId);
              return (
                <div className="grid grid-cols-2 gap-3 text-xs bg-slate-50 p-3 rounded-lg border border-slate-200 mb-4">
                  <div><span className="font-bold text-slate-700">Employee ID:</span> {slipModalRecord.employeeId}</div>
                  <div><span className="font-bold text-slate-700">Department:</span> {emp?.department || '-'}</div>
                  <div><span className="font-bold text-slate-700">Employee Name:</span> {emp?.name || '-'}</div>
                  <div><span className="font-bold text-slate-700">Designation:</span> {emp?.designation || '-'}</div>
                  <div><span className="font-bold text-slate-700">Working Days:</span> {slipModalRecord.totalWorkingDays}</div>
                  <div><span className="font-bold text-slate-700">Days Present / Leave:</span> {slipModalRecord.daysPresent} / {slipModalRecord.leaveDays}</div>
                </div>
              );
            })()}

            {/* Earnings & Deductions Table */}
            <div className="border border-slate-300 rounded-lg overflow-hidden text-xs mb-4">
              <div className="grid grid-cols-2 bg-slate-100 border-b border-slate-300 font-bold text-slate-800 p-2">
                <div>EARNINGS &amp; ALLOWANCES</div>
                <div>DEDUCTIONS</div>
              </div>
              <div className="grid grid-cols-2 p-3 gap-3 divide-x divide-slate-200">
                <div className="space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Basic Salary:</span>
                    <span className="font-medium">{formatINR(slipModalRecord.basicSalary)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Attendance Salary:</span>
                    <span className="font-medium">{formatINR(slipModalRecord.attendanceSalary)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Overtime Pay ({slipModalRecord.overtimeHours} hrs):</span>
                    <span className="font-medium">{formatINR(slipModalRecord.overtimePay)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Special Allowances:</span>
                    <span className="font-medium">{formatINR(slipModalRecord.allowances)}</span>
                  </div>
                  <div className="flex justify-between font-bold pt-2 border-t border-slate-200 text-blue-900">
                    <span>Gross Earnings:</span>
                    <span>{formatINR(slipModalRecord.grossSalary)}</span>
                  </div>
                </div>

                <div className="pl-3 space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Provident Fund &amp; Tax:</span>
                    <span className="font-medium text-rose-700">{formatINR(slipModalRecord.deductions)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Other Deductions:</span>
                    <span className="font-medium text-slate-400">₹ 0.00</span>
                  </div>
                  <div className="flex justify-between font-bold pt-10 border-t border-slate-200 text-rose-900">
                    <span>Total Deductions:</span>
                    <span>{formatINR(slipModalRecord.deductions)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Net Salary Highlight */}
            <div className="bg-emerald-50 border-2 border-emerald-500 p-3 rounded-lg flex items-center justify-between mb-8">
              <span className="font-black text-emerald-900 text-sm">NET PAYABLE SALARY:</span>
              <span className="text-xl font-black text-emerald-700">{formatINR(slipModalRecord.netSalary)}</span>
            </div>

            {/* Signatures */}
            <div className="grid grid-cols-3 text-center text-xs text-slate-500 pt-6 border-t border-dashed border-slate-300 mb-6">
              <div>
                <div className="h-8"></div>
                <div className="border-t border-slate-400 pt-1 font-semibold text-slate-700">Accounts Staff</div>
              </div>
              <div>
                <div className="h-8"></div>
                <div className="border-t border-slate-400 pt-1 font-semibold text-slate-700">Principal / Director</div>
              </div>
              <div>
                <div className="h-8"></div>
                <div className="border-t border-slate-400 pt-1 font-semibold text-slate-700">Employee Signature</div>
              </div>
            </div>

            {/* Modal Controls */}
            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => window.print()}
                className="bg-blue-700 hover:bg-blue-800 text-white font-semibold text-xs px-4 py-2 rounded-md transition flex items-center space-x-1.5"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print Salary Slip</span>
              </button>
              <button
                onClick={() => setSlipModalRecord(null)}
                className="bg-slate-200 hover:bg-slate-300 text-slate-800 font-semibold text-xs px-4 py-2 rounded-md transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
