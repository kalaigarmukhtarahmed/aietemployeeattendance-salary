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

export const DEPARTMENTS = [
  'Computer Science & Eng',
  'Information Science & Eng',
  'Electronics & Communication',
  'Mechanical Engineering',
  'Civil Engineering',
  'Artificial Intelligence & ML',
  'Data Science & Analytics',
  'Basic Science & Humanities',
  'Management Studies (MBA)',
  'Administration & Accounts',
  'Examination & Academic Cell',
  'Library & Information Center',
  'Training & Placement Cell',
  'Laboratory & Technical Support'
] as const;

export const DESIGNATIONS = [
  'Professor & HOD',
  'Professor',
  'Associate Professor',
  'Assistant Professor',
  'Senior Lecturer',
  'Lecturer',
  'Lab Instructor',
  'Administrative Officer',
  'System Administrator',
  'Accountant',
  'Office Assistant'
] as const;

const MALE_FIRST_NAMES = [
  'Rajesh', 'Manoj', 'Suresh', 'Karthik', 'Prabhakar', 'Ramesh', 'Sandeep', 'Arvind',
  'Vinay', 'Gautham', 'Harish', 'Naveen', 'Chethan', 'Rakshith', 'Ashish', 'Praveen',
  'Santosh', 'Bharath', 'Vikram', 'Sudhir', 'Sharath', 'Raghav', 'Vijay', 'Kiran',
  'Prasad', 'Mohan', 'Satish', 'Ganesh', 'Umesh', 'Jagadish', 'Mahesh', 'Anand',
  'Prashanth', 'Girish', 'Shailesh', 'Raghavendra', 'Deepak', 'Sachin', 'Sunil', 'Rohit',
  'Pradeep', 'Yogesh', 'Lokesh', 'Gururaj', 'Srikanth', 'Ravindra', 'Dayanand', 'Vidyadhar',
  'Chandra', 'Sudarshan'
];

const FEMALE_FIRST_NAMES = [
  'Ananya', 'Sneha', 'Divya', 'Priya', 'Pooja', 'Deepa', 'Shweta', 'Rohini',
  'Meghana', 'Shilpa', 'Bhavya', 'Sushmitha', 'Kavya', 'Swathi', 'Manjula', 'Rashmi',
  'Keerthi', 'Archana', 'Jyothi', 'Usha', 'Sunitha', 'Pallavi', 'Radhika', 'Geetha',
  'Shruthi', 'Sowmya', 'Rekha', 'Mamatha', 'Roopa', 'Vidyashree', 'Smitha', 'Preethi',
  'Lavanya', 'Ashwini', 'Vani', 'Savitha', 'Chaithra', 'Pavithra', 'Shobha', 'Pushpa',
  'Nalini', 'Suma', 'Chetana', 'Varsha', 'Akshatha', 'Sahana', 'Sushma', 'Sindhu',
  'Thejaswini', 'Yamuna'
];

const SURNAMES = [
  'Shetty', 'Bhat', 'Hegde', 'Rao', 'Poojary', 'Alva', 'Mendon', 'Naik',
  'Shenoy', 'Acharya', 'Kulal', 'Prabhu', 'Kamath', 'Pai', 'Nayak', 'Kotian',
  'Bangera', 'Salian', 'Karkera', 'Devadiga', 'Rai', 'Ballal', 'Kumble', 'Kadri',
  'Suvarna', 'Karanth', 'Soans', 'Kunder', 'Anchan', 'Amin', 'Somayaji', 'Kudva',
  'Baliga', 'Udupa', 'Tantri', 'Holla', 'Adiga', 'Aithal', 'Maroli', 'Ullal',
  'Mulky', 'Padubidri', 'Kinnigoli', 'Belthangady', 'Karkala', 'Surathkal', 'Haleyangadi', 'Bajpe',
  'Gurupura', 'Puttur'
];

// Department configuration: prefix and count (Sum = 500)
const DEPT_CONFIGS: Array<{ dept: string; prefix: string; baseCode: number; count: number; isTech: boolean }> = [
  { dept: 'Computer Science & Eng', prefix: 'AIET-CSE', baseCode: 101, count: 65, isTech: true },
  { dept: 'Information Science & Eng', prefix: 'AIET-ISE', baseCode: 201, count: 45, isTech: true },
  { dept: 'Electronics & Communication', prefix: 'AIET-ECE', baseCode: 301, count: 55, isTech: true },
  { dept: 'Mechanical Engineering', prefix: 'AIET-ME', baseCode: 401, count: 45, isTech: true },
  { dept: 'Civil Engineering', prefix: 'AIET-CV', baseCode: 501, count: 40, isTech: true },
  { dept: 'Artificial Intelligence & ML', prefix: 'AIET-AIML', baseCode: 601, count: 45, isTech: true },
  { dept: 'Data Science & Analytics', prefix: 'AIET-AIDS', baseCode: 701, count: 35, isTech: true },
  { dept: 'Basic Science & Humanities', prefix: 'AIET-BSH', baseCode: 801, count: 50, isTech: true },
  { dept: 'Management Studies (MBA)', prefix: 'AIET-MBA', baseCode: 901, count: 25, isTech: false },
  { dept: 'Administration & Accounts', prefix: 'AIET-ADM', baseCode: 1, count: 25, isTech: false },
  { dept: 'Examination & Academic Cell', prefix: 'AIET-EXAM', baseCode: 1, count: 15, isTech: false },
  { dept: 'Library & Information Center', prefix: 'AIET-LIB', baseCode: 1, count: 12, isTech: false },
  { dept: 'Training & Placement Cell', prefix: 'AIET-TPO', baseCode: 1, count: 13, isTech: false },
  { dept: 'Laboratory & Technical Support', prefix: 'AIET-LAB', baseCode: 1, count: 30, isTech: true },
];

/**
 * Deterministically generates exactly 500 AIET employees
 */
export function generate500Employees(): Employee[] {
  const employees: Employee[] = [];
  let globalIndex = 0;

  DEPT_CONFIGS.forEach((cfg) => {
    for (let i = 0; i < cfg.count; i++) {
      globalIndex++;
      const isFemale = (globalIndex * 7 + i * 3) % 2 === 0;
      const firstName = isFemale
        ? FEMALE_FIRST_NAMES[(globalIndex + i) % FEMALE_FIRST_NAMES.length]
        : MALE_FIRST_NAMES[(globalIndex + i) % MALE_FIRST_NAMES.length];
      const surname = SURNAMES[(globalIndex * 3 + i * 2) % SURNAMES.length];

      // Formatting ID: e.g. AIET-CSE-101, AIET-ADM-001
      const numPart = cfg.baseCode >= 100
        ? String(cfg.baseCode + i)
        : String(cfg.baseCode + i).padStart(3, '0');
      const empId = `${cfg.prefix}-${numPart}`;

      // Designations and Salary tiers based on seniority
      let title = '';
      let designation = '';
      let basicSalary = 45000;
      let otRate = 350;
      let allowances = 6000;
      let deductions = 4000;

      if (i === 0 && cfg.isTech) {
        // HOD
        title = 'Dr. ';
        designation = 'Professor & HOD';
        basicSalary = 85000 + (globalIndex % 5) * 2000;
        otRate = 500;
        allowances = 12000;
        deductions = 8500;
      } else if (i < 4 && cfg.isTech) {
        // Professors
        title = 'Dr. ';
        designation = 'Professor';
        basicSalary = 75000 + (globalIndex % 4) * 2000;
        otRate = 450;
        allowances = 10000;
        deductions = 7200;
      } else if (i < 10 && cfg.isTech) {
        // Associate Professors
        title = (i % 2 === 0 ? 'Dr. ' : 'Prof. ');
        designation = 'Associate Professor';
        basicSalary = 60000 + (globalIndex % 5) * 1500;
        otRate = 400;
        allowances = 8000;
        deductions = 5500;
      } else if (cfg.isTech && i < cfg.count - 4) {
        // Assistant Professors
        title = 'Prof. ';
        designation = 'Assistant Professor';
        basicSalary = 45000 + (globalIndex % 7) * 1500;
        otRate = 350;
        allowances = 6000;
        deductions = 4200;
      } else if (cfg.isTech) {
        // Lab Instructors
        title = isFemale ? 'Ms. ' : 'Mr. ';
        designation = 'Lab Instructor';
        basicSalary = 30000 + (globalIndex % 4) * 1200;
        otRate = 250;
        allowances = 3500;
        deductions = 2600;
      } else if (cfg.dept.includes('Administration')) {
        title = isFemale ? 'Ms. ' : 'Mr. ';
        designation = i === 0 ? 'Administrative Officer' : i < 4 ? 'Superintendent' : 'Office Executive';
        basicSalary = i === 0 ? 55000 : 35000 + (globalIndex % 4) * 1500;
        otRate = 300;
        allowances = 5000;
        deductions = 3800;
      } else if (cfg.dept.includes('Library')) {
        title = isFemale ? 'Ms. ' : 'Mr. ';
        designation = i === 0 ? 'Chief Librarian' : 'Assistant Librarian';
        basicSalary = i === 0 ? 52000 : 32000 + (globalIndex % 3) * 1200;
        otRate = 280;
        allowances = 4500;
        deductions = 3200;
      } else if (cfg.dept.includes('Placement')) {
        title = isFemale ? 'Ms. ' : 'Mr. ';
        designation = i === 0 ? 'Head - Training & Placement' : 'Placement Coordinator';
        basicSalary = i === 0 ? 65000 : 42000 + (globalIndex % 4) * 1500;
        otRate = 350;
        allowances = 7000;
        deductions = 4500;
      } else if (cfg.dept.includes('Examination')) {
        title = isFemale ? 'Ms. ' : 'Mr. ';
        designation = i === 0 ? 'Controller of Examination' : 'Academic Officer';
        basicSalary = i === 0 ? 62000 : 38000 + (globalIndex % 4) * 1200;
        otRate = 320;
        allowances = 5500;
        deductions = 4000;
      } else {
        title = 'Prof. ';
        designation = i < 3 ? 'Associate Professor' : 'Assistant Professor';
        basicSalary = 48000 + (globalIndex % 5) * 1500;
        otRate = 350;
        allowances = 6500;
        deductions = 4300;
      }

      const fullName = `${title}${firstName} ${surname}`;
      const emailDomain = 'aiet.org.in';
      const cleanFirst = firstName.toLowerCase();
      const cleanLast = surname.toLowerCase();
      const email = `${cleanFirst}.${cleanLast}${i > 0 && (i % 5 === 0) ? i : ''}@${emailDomain}`;

      // Phone number: starting with 98, 97, 96, 99
      const phonePrefix = ['9845', '9741', '9611', '9900', '9880'][globalIndex % 5];
      const phoneRest = String(100000 + ((globalIndex * 1337 + i * 29) % 900000));
      const phone = `${phonePrefix}${phoneRest.slice(0, 6)}`;

      // Joining date between 2015 and 2024
      const joinYear = 2015 + (globalIndex % 10);
      const joinMonth = String(1 + (globalIndex % 12)).padStart(2, '0');
      const joinDay = String(1 + ((globalIndex * 3) % 28)).padStart(2, '0');
      const joiningDate = `${joinYear}-${joinMonth}-${joinDay}`;

      // 97% Active, 3% on Study/Sabbatical Leave (Inactive)
      const status: 'Active' | 'Inactive' = (globalIndex % 33 === 0) ? 'Inactive' : 'Active';

      employees.push({
        id: empId,
        name: fullName,
        department: cfg.dept,
        designation,
        phone,
        email,
        joiningDate,
        basicSalary,
        overtimeRate: otRate,
        allowances,
        deductions,
        status
      });
    }
  });

  return employees;
}

/**
 * Deterministically generates initial monthly attendance records for the 500 employees.
 */
export function generate500Attendance(employees: Employee[], month = 9, year = 2026): Attendance[] {
  return employees.map((emp, idx) => {
    const totalWorkingDays = 25;
    // High attendance institution: 21 to 25 present days
    const leaveDays = emp.status === 'Inactive' ? 25 : (idx % 11 === 0 ? 3 : idx % 7 === 0 ? 2 : idx % 5 === 0 ? 1 : 0);
    const daysPresent = totalWorkingDays - leaveDays;

    // Overtime hours (0 to 14 hrs)
    const overtimeHours = emp.status === 'Inactive'
      ? 0
      : (idx % 6 === 0 ? 12 : idx % 4 === 0 ? 8 : idx % 3 === 0 ? 6 : idx % 2 === 0 ? 4 : 0);

    return {
      id: `att-${emp.id}-${month}-${year}`,
      employeeId: emp.id,
      month,
      year,
      totalWorkingDays,
      daysPresent,
      leaveDays,
      overtimeHours
    };
  });
}

/**
 * Computes official salary records using strict prompt formulas:
 * - Attendance Salary = (Basic Salary / Total Working Days) * Days Present
 * - Overtime Pay = Overtime Hours * Overtime Rate
 * - Gross Salary = Attendance Salary + Overtime Pay + Allowances
 * - Net Salary = Gross Salary - Deductions
 */
export function generate500Salaries(employees: Employee[], attendance: Attendance[]): SalaryRecord[] {
  const empMap = new Map(employees.map(e => [e.id, e]));
  const todayStr = '2026-09-21';

  return attendance.map((att) => {
    const emp = empMap.get(att.employeeId) || {
      basicSalary: 45000,
      overtimeRate: 350,
      allowances: 5000,
      deductions: 3500
    };

    const attendanceSalary = Math.round((emp.basicSalary / att.totalWorkingDays) * att.daysPresent);
    const overtimePay = Math.round(att.overtimeHours * emp.overtimeRate);
    const grossSalary = attendanceSalary + overtimePay + emp.allowances;
    const netSalary = grossSalary - emp.deductions;

    return {
      id: `sal-${att.employeeId}-${att.month}-${att.year}`,
      employeeId: att.employeeId,
      month: att.month,
      year: att.year,
      basicSalary: emp.basicSalary,
      totalWorkingDays: att.totalWorkingDays,
      daysPresent: att.daysPresent,
      leaveDays: att.leaveDays,
      overtimeHours: att.overtimeHours,
      overtimeRate: emp.overtimeRate,
      attendanceSalary,
      overtimePay,
      allowances: emp.allowances,
      grossSalary,
      deductions: emp.deductions,
      netSalary,
      calculatedDate: todayStr
    };
  });
}

// Pre-generated static collections of exactly 500 items
export const INITIAL_500_EMPLOYEES = generate500Employees();
export const INITIAL_500_ATTENDANCE = generate500Attendance(INITIAL_500_EMPLOYEES);
export const INITIAL_500_SALARIES = generate500Salaries(INITIAL_500_EMPLOYEES, INITIAL_500_ATTENDANCE);
