// API endpoint for MongoDB analytics data
// This should be hosted on a server (Node.js/Express)

import express from 'express';
import { MongoClient } from 'mongodb';
import cors from 'cors';

const app = express();
const PORT = 3001;

// MongoDB connection
const MONGODB_URI = 'mongodb+srv://priyadharshini:Ezhilithanya@cluster0.crvutrr.mongodb.net/College_db?retryWrites=true&w=majority';
const DB_NAME = 'College_db';

// Fallback static data when MongoDB is not available
function getStaticFallbackData(year, semester) {
  const staticData = {
    2027: {
      4: {
        attendanceData: [
          { month: 'Jan', present: 85, absent: 15, total: 100 },
          { month: 'Feb', present: 88, absent: 12, total: 100 },
          { month: 'Mar', present: 82, absent: 18, total: 100 },
          { month: 'Apr', present: 90, absent: 10, total: 100 },
          { month: 'May', present: 87, absent: 13, total: 100 },
          { month: 'Jun', present: 91, absent: 9, total: 100 }
        ],
        performanceData: [
          { subject: 'Math', score: 85, grade: 'B' },
          { subject: 'Science', score: 92, grade: 'A' },
          { subject: 'English', score: 78, grade: 'C' },
          { subject: 'History', score: 88, grade: 'B+' },
          { subject: 'Computer', score: 95, grade: 'A+' }
        ],
        departmentData: [
          { department: 'Computer Science', students: 120 },
          { department: 'Electrical', students: 85 },
          { department: 'Mechanical', students: 95 },
          { department: 'Civil', students: 70 },
          { department: 'Electronics', students: 65 }
        ],
        gradeDistribution: [
          { grade: 'A+', count: 25 },
          { grade: 'A', count: 35 },
          { grade: 'B+', count: 45 },
          { grade: 'B', count: 55 },
          { grade: 'C', count: 30 },
          { grade: 'D', count: 10 }
        ],
        summaryData: {
          totalStudents: 435,
          averageAttendance: 87.5,
          averagePerformance: 85.2,
          topDepartment: 'Computer Science'
        }
      },
      3: {
        attendanceData: [
          { month: 'Jul', present: 83, absent: 17, total: 100 },
          { month: 'Aug', present: 86, absent: 14, total: 100 },
          { month: 'Sep', present: 89, absent: 11, total: 100 },
          { month: 'Oct', present: 84, absent: 16, total: 100 },
          { month: 'Nov', present: 88, absent: 12, total: 100 },
          { month: 'Dec', present: 90, absent: 10, total: 100 }
        ],
        performanceData: [
          { subject: 'Math', score: 82, grade: 'B-' },
          { subject: 'Science', score: 89, grade: 'B+' },
          { subject: 'English', score: 85, grade: 'B' },
          { subject: 'History', score: 86, grade: 'B' },
          { subject: 'Computer', score: 93, grade: 'A' }
        ],
        departmentData: [
          { department: 'Computer Science', students: 125 },
          { department: 'Electrical', students: 82 },
          { department: 'Mechanical', students: 98 },
          { department: 'Civil', students: 68 },
          { department: 'Electronics', students: 62 }
        ],
        gradeDistribution: [
          { grade: 'A+', count: 22 },
          { grade: 'A', count: 38 },
          { grade: 'B+', count: 42 },
          { grade: 'B', count: 52 },
          { grade: 'C', count: 32 },
          { grade: 'D', count: 11 }
        ],
        summaryData: {
          totalStudents: 435,
          averageAttendance: 86.7,
          averagePerformance: 84.8,
          topDepartment: 'Computer Science'
        }
      }
    },
    2026: {
      6: {
        attendanceData: [
          { month: 'Jan', present: 92, absent: 8, total: 100 },
          { month: 'Feb', present: 94, absent: 6, total: 100 },
          { month: 'Mar', present: 90, absent: 10, total: 100 },
          { month: 'Apr', present: 93, absent: 7, total: 100 },
          { month: 'May', present: 95, absent: 5, total: 100 },
          { month: 'Jun', present: 96, absent: 4, total: 100 }
        ],
        performanceData: [
          { subject: 'Math', score: 91, grade: 'A-' },
          { subject: 'Science', score: 94, grade: 'A' },
          { subject: 'English', score: 89, grade: 'B+' },
          { subject: 'History', score: 92, grade: 'A-' },
          { subject: 'Computer', score: 96, grade: 'A+' }
        ],
        departmentData: [
          { department: 'Computer Science', students: 130 },
          { department: 'Electrical', students: 88 },
          { department: 'Mechanical', students: 102 },
          { department: 'Civil', students: 72 },
          { department: 'Electronics', students: 68 }
        ],
        gradeDistribution: [
          { grade: 'A+', count: 35 },
          { grade: 'A', count: 42 },
          { grade: 'B+', count: 38 },
          { grade: 'B', count: 48 },
          { grade: 'C', count: 25 },
          { grade: 'D', count: 8 }
        ],
        summaryData: {
          totalStudents: 460,
          averageAttendance: 93.3,
          averagePerformance: 91.2,
          topDepartment: 'Computer Science'
        }
      }
    },
    2025: {
      4: {
        attendanceData: [
          { month: 'Jan', present: 87, absent: 13, total: 100 },
          { month: 'Feb', present: 89, absent: 11, total: 100 },
          { month: 'Mar', present: 85, absent: 15, total: 100 },
          { month: 'Apr', present: 88, absent: 12, total: 100 },
          { month: 'May', present: 86, absent: 14, total: 100 },
          { month: 'Jun', present: 90, absent: 10, total: 100 }
        ],
        performanceData: [
          { subject: 'Math', score: 86, grade: 'B' },
          { subject: 'Science', score: 90, grade: 'A-' },
          { subject: 'English', score: 84, grade: 'B' },
          { subject: 'History', score: 87, grade: 'B+' },
          { subject: 'Computer', score: 92, grade: 'A-' }
        ],
        departmentData: [
          { department: 'Computer Science', students: 118 },
          { department: 'Electrical', students: 80 },
          { department: 'Mechanical', students: 92 },
          { department: 'Civil', students: 66 },
          { department: 'Electronics', students: 60 }
        ],
        gradeDistribution: [
          { grade: 'A+', count: 28 },
          { grade: 'A', count: 36 },
          { grade: 'B+', count: 40 },
          { grade: 'B', count: 50 },
          { grade: 'C', count: 28 },
          { grade: 'D', count: 9 }
        ],
        summaryData: {
          totalStudents: 416,
          averageAttendance: 87.5,
          averagePerformance: 87.0,
          topDepartment: 'Computer Science'
        }
      },
      2: {
        attendanceData: [
          { month: 'Jul', present: 84, absent: 16, total: 100 },
          { month: 'Aug', present: 86, absent: 14, total: 100 },
          { month: 'Sep', present: 82, absent: 18, total: 100 },
          { month: 'Oct', present: 85, absent: 15, total: 100 },
          { month: 'Nov', present: 87, absent: 13, total: 100 },
          { month: 'Dec', present: 88, absent: 12, total: 100 }
        ],
        performanceData: [
          { subject: 'Math', score: 83, grade: 'B' },
          { subject: 'Science', score: 87, grade: 'B+' },
          { subject: 'English', score: 81, grade: 'B-' },
          { subject: 'History', score: 85, grade: 'B' },
          { subject: 'Computer', score: 89, grade: 'B+' }
        ],
        departmentData: [
          { department: 'Computer Science', students: 115 },
          { department: 'Electrical', students: 78 },
          { department: 'Mechanical', students: 89 },
          { department: 'Civil', students: 64 },
          { department: 'Electronics', students: 58 }
        ],
        gradeDistribution: [
          { grade: 'A+', count: 20 },
          { grade: 'A', count: 32 },
          { grade: 'B+', count: 38 },
          { grade: 'B', count: 48 },
          { grade: 'C', count: 30 },
          { grade: 'D', count: 12 }
        ],
        summaryData: {
          totalStudents: 404,
          averageAttendance: 85.3,
          averagePerformance: 84.2,
          topDepartment: 'Computer Science'
        }
      }
    },
    2024: {
      4: {
        attendanceData: [
          { month: 'Jan', present: 81, absent: 19, total: 100 },
          { month: 'Feb', present: 83, absent: 17, total: 100 },
          { month: 'Mar', present: 79, absent: 21, total: 100 },
          { month: 'Apr', present: 82, absent: 18, total: 100 },
          { month: 'May', present: 84, absent: 16, total: 100 },
          { month: 'Jun', present: 85, absent: 15, total: 100 }
        ],
        performanceData: [
          { subject: 'Math', score: 80, grade: 'B-' },
          { subject: 'Science', score: 84, grade: 'B' },
          { subject: 'English', score: 78, grade: 'C+' },
          { subject: 'History', score: 82, grade: 'B-' },
          { subject: 'Computer', score: 86, grade: 'B' }
        ],
        departmentData: [
          { department: 'Computer Science', students: 110 },
          { department: 'Electrical', students: 75 },
          { department: 'Mechanical', students: 85 },
          { department: 'Civil', students: 62 },
          { department: 'Electronics', students: 56 }
        ],
        gradeDistribution: [
          { grade: 'A+', count: 18 },
          { grade: 'A', count: 28 },
          { grade: 'B+', count: 35 },
          { grade: 'B', count: 45 },
          { grade: 'C', count: 32 },
          { grade: 'D', count: 15 }
        ],
        summaryData: {
          totalStudents: 388,
          averageAttendance: 82.3,
          averagePerformance: 81.2,
          topDepartment: 'Computer Science'
        }
      }
    }
  };

  return staticData[year]?.[semester] || null;
}

app.use(cors());
app.use(express.json());

// Cache MongoDB connection
let cachedClient = null;
let cachedDb = null;

async function connectToDatabase() {
  if (cachedClient && cachedDb) {
    return { client: cachedClient, db: cachedDb };
  }
  
  const client = new MongoClient(MONGODB_URI);
  await client.connect();
  const db = client.db(DB_NAME);
  
  cachedClient = client;
  cachedDb = db;
  
  return { client, db };
}

// GET analytics data
app.get('/api/analytics/:year/:semester', async (req, res) => {
  try {
    const { year, semester } = req.params;
    
    try {
      const { db } = await connectToDatabase();
      const analytics = await db.collection('analytics').findOne({
        year: parseInt(year),
        semester: parseInt(semester)
      });
      
      if (!analytics) {
        return res.status(404).json({ error: 'Analytics data not found' });
      }
      
      res.json(analytics.data);
    } catch (mongoError) {
      console.log('MongoDB connection failed, using fallback data:', mongoError.message);
      
      // Fallback to static data when MongoDB is not available
      const fallbackData = getStaticFallbackData(parseInt(year), parseInt(semester));
      if (fallbackData) {
        res.json(fallbackData);
      } else {
        res.status(404).json({ error: 'Analytics data not found' });
      }
    }
  } catch (error) {
    console.error('Error in analytics endpoint:', error);
    res.status(500).json({ error: 'Failed to fetch analytics data' });
  }
});

// POST initialize sample data
app.post('/api/analytics/init', async (req, res) => {
  try {
    const { db } = await connectToDatabase();
    
    const sampleData = [
      {
        year: 2027,
        semester: 4,
        data: {
          attendanceData: [
            { month: 'Jan', present: 85, absent: 15, total: 100 },
            { month: 'Feb', present: 88, absent: 12, total: 100 },
            { month: 'Mar', present: 82, absent: 18, total: 100 },
            { month: 'Apr', present: 90, absent: 10, total: 100 },
            { month: 'May', present: 87, absent: 13, total: 100 },
            { month: 'Jun', present: 91, absent: 9, total: 100 }
          ],
          performanceData: [
            { subject: 'Math', score: 85, grade: 'B' },
            { subject: 'Science', score: 92, grade: 'A' },
            { subject: 'English', score: 78, grade: 'C' },
            { subject: 'History', score: 88, grade: 'B+' },
            { subject: 'Computer', score: 95, grade: 'A+' }
          ],
          departmentData: [
            { department: 'Computer Science', students: 120 },
            { department: 'Electrical', students: 85 },
            { department: 'Mechanical', students: 95 },
            { department: 'Civil', students: 70 },
            { department: 'Electronics', students: 65 }
          ],
          gradeDistribution: [
            { grade: 'A+', count: 25 },
            { grade: 'A', count: 35 },
            { grade: 'B+', count: 45 },
            { grade: 'B', count: 55 },
            { grade: 'C', count: 30 },
            { grade: 'D', count: 10 }
          ],
          summaryData: {
            totalStudents: 435,
            averageAttendance: 87.5,
            averagePerformance: 85.2,
            topDepartment: 'Computer Science'
          }
        }
      },
      {
        year: 2027,
        semester: 3,
        data: {
          attendanceData: [
            { month: 'Jul', present: 83, absent: 17, total: 100 },
            { month: 'Aug', present: 86, absent: 14, total: 100 },
            { month: 'Sep', present: 89, absent: 11, total: 100 },
            { month: 'Oct', present: 84, absent: 16, total: 100 },
            { month: 'Nov', present: 88, absent: 12, total: 100 },
            { month: 'Dec', present: 90, absent: 10, total: 100 }
          ],
          performanceData: [
            { subject: 'Math', score: 82, grade: 'B-' },
            { subject: 'Science', score: 89, grade: 'B+' },
            { subject: 'English', score: 85, grade: 'B' },
            { subject: 'History', score: 86, grade: 'B' },
            { subject: 'Computer', score: 93, grade: 'A' }
          ],
          departmentData: [
            { department: 'Computer Science', students: 125 },
            { department: 'Electrical', students: 82 },
            { department: 'Mechanical', students: 98 },
            { department: 'Civil', students: 68 },
            { department: 'Electronics', students: 62 }
          ],
          gradeDistribution: [
            { grade: 'A+', count: 22 },
            { grade: 'A', count: 38 },
            { grade: 'B+', count: 42 },
            { grade: 'B', count: 52 },
            { grade: 'C', count: 32 },
            { grade: 'D', count: 11 }
          ],
          summaryData: {
            totalStudents: 435,
            averageAttendance: 86.7,
            averagePerformance: 84.8,
            topDepartment: 'Computer Science'
          }
        }
      },
      {
        year: 2026,
        semester: 6,
        data: {
          attendanceData: [
            { month: 'Jan', present: 92, absent: 8, total: 100 },
            { month: 'Feb', present: 94, absent: 6, total: 100 },
            { month: 'Mar', present: 90, absent: 10, total: 100 },
            { month: 'Apr', present: 93, absent: 7, total: 100 },
            { month: 'May', present: 95, absent: 5, total: 100 },
            { month: 'Jun', present: 96, absent: 4, total: 100 }
          ],
          performanceData: [
            { subject: 'Math', score: 91, grade: 'A-' },
            { subject: 'Science', score: 94, grade: 'A' },
            { subject: 'English', score: 89, grade: 'B+' },
            { subject: 'History', score: 92, grade: 'A-' },
            { subject: 'Computer', score: 96, grade: 'A+' }
          ],
          departmentData: [
            { department: 'Computer Science', students: 130 },
            { department: 'Electrical', students: 88 },
            { department: 'Mechanical', students: 102 },
            { department: 'Civil', students: 72 },
            { department: 'Electronics', students: 68 }
          ],
          gradeDistribution: [
            { grade: 'A+', count: 35 },
            { grade: 'A', count: 42 },
            { grade: 'B+', count: 38 },
            { grade: 'B', count: 48 },
            { grade: 'C', count: 25 },
            { grade: 'D', count: 8 }
          ],
          summaryData: {
            totalStudents: 460,
            averageAttendance: 93.3,
            averagePerformance: 91.2,
            topDepartment: 'Computer Science'
          }
        }
      },
      {
        year: 2025,
        semester: 4,
        data: {
          attendanceData: [
            { month: 'Jan', present: 87, absent: 13, total: 100 },
            { month: 'Feb', present: 89, absent: 11, total: 100 },
            { month: 'Mar', present: 85, absent: 15, total: 100 },
            { month: 'Apr', present: 88, absent: 12, total: 100 },
            { month: 'May', present: 86, absent: 14, total: 100 },
            { month: 'Jun', present: 90, absent: 10, total: 100 }
          ],
          performanceData: [
            { subject: 'Math', score: 86, grade: 'B' },
            { subject: 'Science', score: 90, grade: 'A-' },
            { subject: 'English', score: 84, grade: 'B' },
            { subject: 'History', score: 87, grade: 'B+' },
            { subject: 'Computer', score: 92, grade: 'A-' }
          ],
          departmentData: [
            { department: 'Computer Science', students: 118 },
            { department: 'Electrical', students: 80 },
            { department: 'Mechanical', students: 92 },
            { department: 'Civil', students: 66 },
            { department: 'Electronics', students: 60 }
          ],
          gradeDistribution: [
            { grade: 'A+', count: 28 },
            { grade: 'A', count: 36 },
            { grade: 'B+', count: 40 },
            { grade: 'B', count: 50 },
            { grade: 'C', count: 28 },
            { grade: 'D', count: 9 }
          ],
          summaryData: {
            totalStudents: 416,
            averageAttendance: 87.5,
            averagePerformance: 87.0,
            topDepartment: 'Computer Science'
          }
        }
      },
      {
        year: 2025,
        semester: 2,
        data: {
          attendanceData: [
            { month: 'Jul', present: 84, absent: 16, total: 100 },
            { month: 'Aug', present: 86, absent: 14, total: 100 },
            { month: 'Sep', present: 82, absent: 18, total: 100 },
            { month: 'Oct', present: 85, absent: 15, total: 100 },
            { month: 'Nov', present: 87, absent: 13, total: 100 },
            { month: 'Dec', present: 88, absent: 12, total: 100 }
          ],
          performanceData: [
            { subject: 'Math', score: 83, grade: 'B' },
            { subject: 'Science', score: 87, grade: 'B+' },
            { subject: 'English', score: 81, grade: 'B-' },
            { subject: 'History', score: 85, grade: 'B' },
            { subject: 'Computer', score: 89, grade: 'B+' }
          ],
          departmentData: [
            { department: 'Computer Science', students: 115 },
            { department: 'Electrical', students: 78 },
            { department: 'Mechanical', students: 89 },
            { department: 'Civil', students: 64 },
            { department: 'Electronics', students: 58 }
          ],
          gradeDistribution: [
            { grade: 'A+', count: 20 },
            { grade: 'A', count: 32 },
            { grade: 'B+', count: 38 },
            { grade: 'B', count: 48 },
            { grade: 'C', count: 30 },
            { grade: 'D', count: 12 }
          ],
          summaryData: {
            totalStudents: 404,
            averageAttendance: 85.3,
            averagePerformance: 84.2,
            topDepartment: 'Computer Science'
          }
        }
      },
      {
        year: 2024,
        semester: 4,
        data: {
          attendanceData: [
            { month: 'Jan', present: 81, absent: 19, total: 100 },
            { month: 'Feb', present: 83, absent: 17, total: 100 },
            { month: 'Mar', present: 79, absent: 21, total: 100 },
            { month: 'Apr', present: 82, absent: 18, total: 100 },
            { month: 'May', present: 84, absent: 16, total: 100 },
            { month: 'Jun', percent: 85, absent: 15, total: 100 }
          ],
          performanceData: [
            { subject: 'Math', score: 80, grade: 'B-' },
            { subject: 'Science', score: 84, grade: 'B' },
            { subject: 'English', score: 78, grade: 'C+' },
            { subject: 'History', score: 82, grade: 'B-' },
            { subject: 'Computer', score: 86, grade: 'B' }
          ],
          departmentData: [
            { department: 'Computer Science', students: 110 },
            { department: 'Electrical', students: 75 },
            { department: 'Mechanical', students: 85 },
            { department: 'Civil', students: 62 },
            { department: 'Electronics', students: 56 }
          ],
          gradeDistribution: [
            { grade: 'A+', count: 18 },
            { grade: 'A', count: 28 },
            { grade: 'B+', count: 35 },
            { grade: 'B', count: 45 },
            { grade: 'C', count: 32 },
            { grade: 'D', count: 15 }
          ],
          summaryData: {
            totalStudents: 388,
            averageAttendance: 82.3,
            averagePerformance: 81.2,
            topDepartment: 'Computer Science'
          }
        }
      }
    ];
    
    // Clear existing data
    await db.collection('analytics').deleteMany({});
    
    // Insert sample data
    const result = await db.collection('analytics').insertMany(sampleData);
    
    res.json({ 
      message: 'Sample data initialized successfully',
      insertedCount: result.insertedCount 
    });
  } catch (error) {
    console.error('Error initializing data:', error);
    res.status(500).json({ error: 'Failed to initialize data' });
  }
});

app.listen(PORT, () => {
  console.log(`Analytics API server running on port ${PORT}`);
});
