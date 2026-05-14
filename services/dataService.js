// MongoDB Data Service
// This service connects to MongoDB and fetches real data for the Analytics page

const MONGODB_URI = 'mongodb+srv://priyadharshini:Ezhilithanya@cluster0.crvutrr.mongodb.net/College_db';

// Fetch data from MongoDB
async function fetchAnalyticsData(startDate, endDate, department = null, semester = null) {
  try {
    // This would be your actual MongoDB API endpoint
    // For now, we'll simulate the API call with fetch
    const response = await fetch('/api/analytics', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({
        startDate,
        endDate,
        department,
        semester,
        database: 'College_db',
        uri: MONGODB_URI
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch data from MongoDB');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('MongoDB connection error:', error);
    // Always return semester-specific static data as fallback
    return getSemesterSpecificStaticData(semester);
  }
}

// Fetch attendance data from MongoDB
export async function fetchAttendanceData(startDate, endDate, department = null, semester = null) {
  try {
    const response = await fetch(`${MONGODB_URI}/attendance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        startDate,
        endDate,
        department,
        semester
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching attendance data:', error);
    return [];
  }
}

// Fetch performance data from MongoDB
export async function fetchPerformanceData(startDate, endDate, department = null, semester = null) {
  try {
    const response = await fetch(`${MONGODB_URI}/performance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        startDate,
        endDate,
        department,
        semester
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching performance data:', error);
    return [];
  }
}

// Fetch department data from MongoDB
export async function fetchDepartmentData(semester = null) {
  try {
    const response = await fetch(`${MONGODB_URI}/departments?semester=${semester || ''}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching department data:', error);
    return [];
  }
}

// Fetch grade distribution from MongoDB
export async function fetchGradeDistribution(department = null, semester = null) {
  try {
    const response = await fetch(`${MONGODB_URI}/grades?department=${department || ''}&semester=${semester || ''}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching grade distribution:', error);
    return [];
  }
}

// Fetch income/expense data from MongoDB
export async function fetchIncomeExpenseData(startDate, endDate, semester = null) {
  try {
    const response = await fetch(`${MONGODB_URI}/income-expense`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        startDate,
        endDate,
        semester
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching income/expense data:', error);
    return [];
  }
}

// Fetch student enrollment data from MongoDB
export async function fetchStudentEnrollmentData(department = null, semester = null) {
  try {
    const response = await fetch(`${MONGODB_URI}/students?department=${department || ''}&semester=${semester || ''}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching student enrollment data:', error);
    return [];
  }
}

// Fetch faculty data from MongoDB
export async function fetchFacultyData(department = null, semester = null) {
  try {
    const response = await fetch(`${MONGODB_URI}/faculty?department=${department || ''}&semester=${semester || ''}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching faculty data:', error);
    return [];
  }
}

// Get semester-specific static data for fallback
function getSemesterSpecificStaticData(semester) {
  const semesterData = {
    'Semester 4 (Current)': {
      attendanceData: [
        {month: 'Jan', attendance: 85, target: 90},
        {month: 'Feb', attendance: 87, target: 90},
        {month: 'Mar', attendance: 86, target: 90},
        {month: 'Apr', attendance: 84, target: 90},
        {month: 'May', attendance: 80, target: 90},
        {month: 'Jun', attendance: 82, target: 90},
        {month: 'Jul', attendance: 85, target: 90},
        {month: 'Aug', attendance: 89, target: 90},
        {month: 'Sep', attendance: 86, target: 90},
        {month: 'Oct', attendance: 91, target: 90},
        {month: 'Nov', attendance: 83, target: 90},
        {month: 'Dec', attendance: 79, target: 90},
      ],
      performanceData: [
        {month: 'Jan', passRate: 88, avgMarks: 78},
        {month: 'Feb', passRate: 90, avgMarks: 82},
        {month: 'Mar', passRate: 85, avgMarks: 80},
        {month: 'Apr', passRate: 83, avgMarks: 77},
        {month: 'May', passRate: 80, avgMarks: 75},
        {month: 'Jun', passRate: 82, avgMarks: 78},
        {month: 'Jul', passRate: 84, avgMarks: 79},
        {month: 'Aug', passRate: 87, avgMarks: 83},
        {month: 'Sep', passRate: 86, avgMarks: 81},
        {month: 'Oct', passRate: 88, avgMarks: 84},
        {month: 'Nov', passRate: 83, avgMarks: 79},
        {month: 'Dec', passRate: 80, avgMarks: 76},
      ],
      departmentData: [
        {name: 'Computer Science', students: 680, faculty: 82, avgAttendance: 86, cgpa: 8.4},
        {name: 'Physics', students: 420, faculty: 68, avgAttendance: 82, cgpa: 7.9},
        {name: 'Mathematics', students: 390, faculty: 58, avgAttendance: 80, cgpa: 8.1},
        {name: 'Electronics', students: 580, faculty: 94, avgAttendance: 85, cgpa: 8.2},
        {name: 'Mechanical', students: 510, faculty: 86, avgAttendance: 81, cgpa: 7.8},
      ],
      gradeDistribution: [
        {grade: 'A+', count: 120, color: '#22c55e'},
        {grade: 'A', count: 280, color: '#3b82f6'},
        {grade: 'B+', count: 200, color: '#06b6d4'},
        {grade: 'B', count: 150, color: '#8b5cf6'},
        {grade: 'C', count: 80, color: '#f59e0b'},
        {grade: 'F', count: 30, color: '#ef4444'},
      ],
      summaryData: {
        students: '2,690',
        faculty: '400',
        departments: '5',
        courses: '48',
        income: 4100000,
        expense: 2300000,
        scholarships: 140
      }
    },
    'Semester 3': {
      attendanceData: [
        {month: 'Jan', attendance: 83, target: 90},
        {month: 'Feb', attendance: 85, target: 90},
        {month: 'Mar', attendance: 84, target: 90},
        {month: 'Apr', attendance: 82, target: 90},
        {month: 'May', attendance: 78, target: 90},
        {month: 'Jun', attendance: 80, target: 90},
        {month: 'Jul', attendance: 83, target: 90},
        {month: 'Aug', attendance: 87, target: 90},
        {month: 'Sep', attendance: 84, target: 90},
        {month: 'Oct', attendance: 89, target: 90},
        {month: 'Nov', attendance: 81, target: 90},
        {month: 'Dec', attendance: 77, target: 90},
      ],
      performanceData: [
        {month: 'Jan', passRate: 86, avgMarks: 76},
        {month: 'Feb', passRate: 88, avgMarks: 80},
        {month: 'Mar', passRate: 83, avgMarks: 78},
        {month: 'Apr', passRate: 81, avgMarks: 75},
        {month: 'May', passRate: 78, avgMarks: 73},
        {month: 'Jun', passRate: 80, avgMarks: 76},
        {month: 'Jul', passRate: 82, avgMarks: 77},
        {month: 'Aug', passRate: 85, avgMarks: 81},
        {month: 'Sep', passRate: 84, avgMarks: 79},
        {month: 'Oct', passRate: 86, avgMarks: 82},
        {month: 'Nov', passRate: 81, avgMarks: 77},
        {month: 'Dec', passRate: 78, avgMarks: 74},
      ],
      departmentData: [
        {name: 'Computer Science', students: 650, faculty: 80, avgAttendance: 84, cgpa: 8.3},
        {name: 'Physics', students: 410, faculty: 66, avgAttendance: 80, cgpa: 7.8},
        {name: 'Mathematics', students: 380, faculty: 56, avgAttendance: 78, cgpa: 8.0},
        {name: 'Electronics', students: 560, faculty: 92, avgAttendance: 83, cgpa: 8.1},
        {name: 'Mechanical', students: 500, faculty: 84, avgAttendance: 79, cgpa: 7.7},
      ],
      gradeDistribution: [
        {grade: 'A+', count: 100, color: '#22c55e'},
        {grade: 'A', count: 260, color: '#3b82f6'},
        {grade: 'B+', count: 180, color: '#06b6d4'},
        {grade: 'B', count: 140, color: '#8b5cf6'},
        {grade: 'C', count: 70, color: '#f59e0b'},
        {grade: 'F', count: 40, color: '#ef4444'},
      ],
      summaryData: {
        students: '2,550',
        faculty: '390',
        departments: '5',
        courses: '46',
        income: 3900000,
        expense: 2100000,
        scholarships: 130
      }
    },
    'Semester 2': {
      attendanceData: [
        {month: 'Jan', attendance: 81, target: 90},
        {month: 'Feb', attendance: 83, target: 90},
        {month: 'Mar', attendance: 82, target: 90},
        {month: 'Apr', attendance: 80, target: 90},
        {month: 'May', attendance: 76, target: 90},
        {month: 'Jun', attendance: 78, target: 90},
        {month: 'Jul', attendance: 81, target: 90},
        {month: 'Aug', attendance: 85, target: 90},
        {month: 'Sep', attendance: 82, target: 90},
        {month: 'Oct', attendance: 87, target: 90},
        {month: 'Nov', attendance: 79, target: 90},
        {month: 'Dec', attendance: 75, target: 90},
      ],
      performanceData: [
        {month: 'Jan', passRate: 84, avgMarks: 74},
        {month: 'Feb', passRate: 86, avgMarks: 78},
        {month: 'Mar', passRate: 83, avgMarks: 76},
        {month: 'Apr', passRate: 81, avgMarks: 73},
        {month: 'May', passRate: 78, avgMarks: 71},
        {month: 'Jun', passRate: 80, avgMarks: 74},
        {month: 'Jul', passRate: 82, avgMarks: 75},
        {month: 'Aug', passRate: 85, avgMarks: 79},
        {month: 'Sep', passRate: 84, avgMarks: 77},
        {month: 'Oct', passRate: 86, avgMarks: 80},
        {month: 'Nov', passRate: 79, avgMarks: 75},
        {month: 'Dec', passRate: 76, avgMarks: 72},
      ],
      departmentData: [
        {name: 'Computer Science', students: 620, faculty: 78, avgAttendance: 82, cgpa: 8.2},
        {name: 'Physics', students: 400, faculty: 64, avgAttendance: 78, cgpa: 7.7},
        {name: 'Mathematics', students: 370, faculty: 54, avgAttendance: 76, cgpa: 7.9},
        {name: 'Electronics', students: 540, faculty: 90, avgAttendance: 81, cgpa: 8.0},
        {name: 'Mechanical', students: 490, faculty: 82, avgAttendance: 77, cgpa: 7.6},
      ],
      gradeDistribution: [
        {grade: 'A+', count: 80, color: '#22c55e'},
        {grade: 'A', count: 240, color: '#3b82f6'},
        {grade: 'B+', count: 160, color: '#06b6d4'},
        {grade: 'B', count: 130, color: '#8b5cf6'},
        {grade: 'C', count: 60, color: '#f59e0b'},
        {grade: 'F', count: 50, color: '#ef4444'},
      ],
      summaryData: {
        students: '2,410',
        faculty: '380',
        departments: '5',
        courses: '44',
        income: 3700000,
        expense: 1900000,
        scholarships: '120'
      }
    },
    'Semester 1': {
      attendanceData: [
        {month: 'Jan', attendance: 79, target: 90},
        {month: 'Feb', attendance: 81, target: 90},
        {month: 'Mar', attendance: 80, target: 90},
        {month: 'Apr', attendance: 78, target: 90},
        {month: 'May', attendance: 74, target: 90},
        {month: 'Jun', attendance: 76, target: 90},
        {month: 'Jul', attendance: 79, target: 90},
        {month: 'Aug', attendance: 83, target: 90},
        {month: 'Sep', attendance: 80, target: 90},
        {month: 'Oct', attendance: 85, target: 90},
        {month: 'Nov', attendance: 77, target: 90},
        {month: 'Dec', attendance: 73, target: 90},
      ],
      performanceData: [
        {month: 'Jan', passRate: 82, avgMarks: 72},
        {month: 'Feb', passRate: 84, avgMarks: 74},
        {month: 'Mar', passRate: 81, avgMarks: 74},
        {month: 'Apr', passRate: 79, avgMarks: 71},
        {month: 'May', passRate: 76, avgMarks: 69},
        {month: 'Jun', passRate: 78, avgMarks: 72},
        {month: 'Jul', passRate: 80, avgMarks: 73},
        {month: 'Aug', passRate: 83, avgMarks: 77},
        {month: 'Sep', passRate: 82, avgMarks: 75},
        {month: 'Oct', passRate: 84, avgMarks: 78},
        {month: 'Nov', passRate: 79, avgMarks: 71},
        {month: 'Dec', passRate: 76, avgMarks: 70},
      ],
      departmentData: [
        {name: 'Computer Science', students: 590, faculty: 76, avgAttendance: 80, cgpa: 8.1},
        {name: 'Physics', students: 380, faculty: 62, avgAttendance: 76, cgpa: 7.5},
        {name: 'Mathematics', students: 350, faculty: 52, avgAttendance: 74, cgpa: 7.7},
        {name: 'Electronics', students: 520, faculty: 88, avgAttendance: 79, cgpa: 7.9},
        {name: 'Mechanical', students: 470, faculty: 80, avgAttendance: 75, cgpa: 7.5},
      ],
      gradeDistribution: [
        {grade: 'A+', count: 60, color: '#22c55e'},
        {grade: 'A', count: 220, color: '#3b82f6'},
        {grade: 'B+', count: 120, color: '#06b6d4'},
        {grade: 'B', count: 110, color: '#8b5cf6'},
        {grade: 'C', count: 40, color: '#f59e0b'},
        {grade: 'F', count: 70, color: '#ef4444'},
      ],
      summaryData: {
        students: '2,270',
        faculty: '370',
        departments: '5',
        courses: '42',
        income: 3300000,
        expense: 1700000,
        scholarships: '110'
      }
    }
  };
  
  return semesterData[semester] || semesterData['Semester 4 (Current)'];
}

// Export consolidated data function for the Analytics page
export async function fetchAnalyticsData(startDate, endDate, department = null, semester = null) {
  const [
    attendanceData,
    performanceData,
    departmentData,
    gradeDistribution,
    incomeExpenseData,
    studentEnrollmentData,
    facultyData
  ] = await Promise.all([
    fetchAttendanceData(startDate, endDate, department, semester),
    fetchPerformanceData(startDate, endDate, department, semester),
    fetchDepartmentData(semester),
    fetchGradeDistribution(department, semester),
    fetchIncomeExpenseData(startDate, endDate, semester),
    fetchStudentEnrollmentData(department, semester),
    fetchFacultyData(department, semester)
  ]);

  return {
    attendanceData,
    performanceData,
    departmentData,
    gradeDistribution,
    incomeExpenseData,
    studentEnrollmentData,
    facultyData,
    summaryData: {
      students: studentEnrollmentData.reduce((sum, item) => sum + (item.students || 0), 0).toString(),
      faculty: facultyData.reduce((sum, item) => sum + (item.faculty || 0), 0).toString(),
      departments: departmentData.length.toString(),
      courses: '48', // You can calculate this from actual data
      income: incomeExpenseData.reduce((sum, item) => sum + (item.income || 0), 0),
      expense: incomeExpenseData.reduce((sum, item) => sum + (item.expense || 0), 0),
      scholarships: '140' // You can calculate this from actual data
    }
  };
}
