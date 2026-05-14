from fastapi import APIRouter, HTTPException, Query, Body, Path
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel

from backend.db import get_db
from backend.utils.mongo import serialize_doc
from backend.models.faculty import Faculty
from backend.models.faculty_activity import CourseAssignment, PerformanceMetric, ProfessionalDevelopment, FacultyMentorship, ResearchProject
from backend.models.faculty_leave import FacultyLeave
from backend.models.faculty_feedback import PeerReview
from backend.models.faculty_notification import Notification

router = APIRouter(prefix="/api/faculty", tags=["faculty"])

# Helper functions
async def get_faculty_collection():
    db = get_db()
    return db["faculty"]

async def get_faculty_activity_collection(collection_name: str):
    db = get_db()
    return db[collection_name]

# -----------------
# Seed Data Route
# -----------------

@router.post("/seed/data")
async def seed_faculty_data():
    """Seed the database with sample faculty data with detailed metrics"""
    collection = await get_faculty_collection()
    
    # Sample faculty data with detailed information matching analytics
    faculty_data = [
        # Computer Science Department
        {
            "name": "Dr. Ramesh Kumar",
            "employeeId": "FAC001",
            "email": "ramesh.kumar@mit.edu",
            "phone": "+91-9876543210",
            "designation": "Professor",
            "subject": "Database Systems",
            "department_id": "CS",
            "departmentId": "Computer Science",
            "qualification": "Ph.D. in Computer Science",
            "employment_status": "Active",
            "joining_date": datetime(2012, 8, 15),
            "experience_years": 12,
            "attendance_rate": 91,
            "pass_rate": 93,
            "specialization": "Database Management",
            "status": "Top",
            "cgpa": 8.4,
            "office_location": "Building A, Room 301",
        },
        {
            "name": "Prof. Lakshmi Nair",
            "employeeId": "FAC002",
            "email": "lakshmi.nair@mit.edu",
            "phone": "+91-9876543211",
            "designation": "Associate Professor",
            "subject": "Data Structures",
            "department_id": "CS",
            "departmentId": "Computer Science",
            "qualification": "Ph.D. in Software Engineering",
            "employment_status": "Active",
            "joining_date": datetime(2016, 7, 1),
            "experience_years": 8,
            "attendance_rate": 88,
            "pass_rate": 90,
            "specialization": "Algorithms",
            "status": "Top",
            "cgpa": 8.3,
            "office_location": "Building A, Room 302",
        },
        {
            "name": "Dr. Anil Verma",
            "employeeId": "FAC003",
            "email": "anil.verma@mit.edu",
            "phone": "+91-9876543212",
            "designation": "Assistant Professor",
            "subject": "OS & Networks",
            "department_id": "CS",
            "departmentId": "Computer Science",
            "qualification": "Ph.D. in Computer Networks",
            "employment_status": "Active",
            "joining_date": datetime(2020, 1, 15),
            "experience_years": 5,
            "attendance_rate": 85,
            "pass_rate": 87,
            "specialization": "Networking",
            "status": "Good",
            "cgpa": 8.1,
            "office_location": "Building A, Room 303",
        },
        # Electronics Department
        {
            "name": "Dr. Sunita Sharma",
            "employeeId": "FAC004",
            "email": "sunita.sharma@mit.edu",
            "phone": "+91-9876543213",
            "designation": "Professor",
            "subject": "Quantum Mechanics",
            "department_id": "ECE",
            "departmentId": "Electronics & Communication",
            "qualification": "Ph.D. in Electronics",
            "employment_status": "Active",
            "joining_date": datetime(2011, 6, 1),
            "experience_years": 14,
            "attendance_rate": 89,
            "pass_rate": 86,
            "specialization": "Quantum Engineering",
            "status": "Good",
            "cgpa": 8.2,
            "office_location": "Building B, Room 201",
        },
        {
            "name": "Prof. Vikram Iyer",
            "employeeId": "FAC005",
            "email": "vikram.iyer@mit.edu",
            "phone": "+91-9876543214",
            "designation": "Associate Professor",
            "subject": "Thermodynamics",
            "department_id": "ECE",
            "departmentId": "Electronics & Communication",
            "qualification": "Ph.D. in Signal Processing",
            "employment_status": "Active",
            "joining_date": datetime(2017, 9, 1),
            "experience_years": 9,
            "attendance_rate": 84,
            "pass_rate": 82,
            "specialization": "Signal Processing",
            "status": "Good",
            "cgpa": 8.0,
            "office_location": "Building B, Room 202",
        },
        {
            "name": "Dr. Meena Pillai",
            "employeeId": "FAC006",
            "email": "meena.pillai@mit.edu",
            "phone": "+91-9876543215",
            "designation": "Assistant Professor",
            "subject": "Electromagnetism",
            "department_id": "ECE",
            "departmentId": "Electronics & Communication",
            "qualification": "Ph.D. in Electronics",
            "employment_status": "Active",
            "joining_date": datetime(2019, 1, 15),
            "experience_years": 4,
            "attendance_rate": 80,
            "pass_rate": 79,
            "specialization": "EMC Design",
            "status": "Watch",
            "cgpa": 7.8,
            "office_location": "Building B, Room 203",
        },
        # Physics Department
        {
            "name": "Prof. Suresh Babu",
            "employeeId": "FAC007",
            "email": "suresh.babu@mit.edu",
            "phone": "+91-9876543216",
            "designation": "Professor",
            "subject": "VLSI Design",
            "department_id": "ECE",
            "departmentId": "Electronics & Communication",
            "qualification": "Ph.D. in VLSI",
            "employment_status": "Active",
            "joining_date": datetime(2010, 5, 1),
            "experience_years": 13,
            "attendance_rate": 92,
            "pass_rate": 92,
            "specialization": "Chip Design",
            "status": "Top",
            "cgpa": 8.5,
            "office_location": "Building B, Room 210",
        },
        {
            "name": "Prof. Rekha Joshi",
            "employeeId": "FAC008",
            "email": "rekha.joshi@mit.edu",
            "phone": "+91-9876543217",
            "designation": "Associate Professor",
            "subject": "Signal Processing",
            "department_id": "ECE",
            "departmentId": "Electronics & Communication",
            "qualification": "Ph.D. in DSP",
            "employment_status": "Active",
            "joining_date": datetime(2015, 9, 1),
            "experience_years": 9,
            "attendance_rate": 89,
            "pass_rate": 89,
            "specialization": "Digital Filters",
            "status": "Top",
            "cgpa": 8.3,
            "office_location": "Building B, Room 211",
        },
        # Mathematics Department
        {
            "name": "Dr. Deepak Gupta",
            "employeeId": "FAC009",
            "email": "deepak.gupta@mit.edu",
            "phone": "+91-9876543218",
            "designation": "Professor",
            "subject": "Linear Algebra",
            "department_id": "MATH",
            "departmentId": "Mathematics",
            "qualification": "Ph.D. in Mathematics",
            "employment_status": "Active",
            "joining_date": datetime(2013, 8, 1),
            "experience_years": 11,
            "attendance_rate": 87,
            "pass_rate": 88,
            "specialization": "Matrix Theory",
            "status": "Good",
            "cgpa": 8.1,
            "office_location": "Building C, Room 301",
        },
        {
            "name": "Prof. Anjali Mehta",
            "employeeId": "FAC010",
            "email": "anjali.mehta@mit.edu",
            "phone": "+91-9876543219",
            "designation": "Associate Professor",
            "subject": "Calculus",
            "department_id": "MATH",
            "departmentId": "Mathematics",
            "qualification": "Ph.D. in Pure Mathematics",
            "employment_status": "Active",
            "joining_date": datetime(2017, 7, 1),
            "experience_years": 7,
            "attendance_rate": 85,
            "pass_rate": 85,
            "specialization": "Analysis",
            "status": "Good",
            "cgpa": 8.0,
            "office_location": "Building C, Room 302",
        },
        {
            "name": "Ms. Divya Krishnan",
            "employeeId": "FAC011",
            "email": "divya.krishnan@mit.edu",
            "phone": "+91-9876543220",
            "designation": "Assistant Professor",
            "subject": "Statistics",
            "department_id": "MATH",
            "departmentId": "Mathematics",
            "qualification": "M.Phil in Statistics",
            "employment_status": "Active",
            "joining_date": datetime(2021, 1, 15),
            "experience_years": 3,
            "attendance_rate": 81,
            "pass_rate": 81,
            "specialization": "Probability",
            "status": "Watch",
            "cgpa": 7.9,
            "office_location": "Building C, Room 303",
        },
        # Mechanical Engineering Department
        {
            "name": "Dr. Venkat Reddy",
            "employeeId": "FAC012",
            "email": "venkat.reddy@mit.edu",
            "phone": "+91-9876543221",
            "designation": "Professor",
            "subject": "Thermofluids",
            "department_id": "ME",
            "departmentId": "Mechanical Engineering",
            "qualification": "Ph.D. in Thermal Engineering",
            "employment_status": "Active",
            "joining_date": datetime(2010, 8, 1),
            "experience_years": 10,
            "attendance_rate": 88,
            "pass_rate": 88,
            "specialization": "Heat Transfer",
            "status": "Top",
            "cgpa": 8.3,
            "office_location": "Building D, Room 301",
        },
        {
            "name": "Prof. Smitha Das",
            "employeeId": "FAC013",
            "email": "smitha.das@mit.edu",
            "phone": "+91-9876543222",
            "designation": "Associate Professor",
            "subject": "Machine Design",
            "department_id": "ME",
            "departmentId": "Mechanical Engineering",
            "qualification": "Ph.D. in Mechanical Design",
            "employment_status": "Active",
            "joining_date": datetime(2016, 9, 1),
            "experience_years": 8,
            "attendance_rate": 84,
            "pass_rate": 85,
            "specialization": "CAD/CAM",
            "status": "Good",
            "cgpa": 8.1,
            "office_location": "Building D, Room 302",
        },
        {
            "name": "Dr. Rahul Nair",
            "employeeId": "FAC014",
            "email": "rahul.nair@mit.edu",
            "phone": "+91-9876543223",
            "designation": "Assistant Professor",
            "subject": "Manufacturing",
            "department_id": "ME",
            "departmentId": "Mechanical Engineering",
            "qualification": "Ph.D. in Manufacturing",
            "employment_status": "Active",
            "joining_date": datetime(2020, 1, 15),
            "experience_years": 4,
            "attendance_rate": 81,
            "pass_rate": 82,
            "specialization": "Additive Manufacturing",
            "status": "Watch",
            "cgpa": 7.9,
            "office_location": "Building D, Room 303",
        },
        # Additional Computer Science Faculty
        {
            "name": "Prof. Rajesh Gupta",
            "employeeId": "FAC015",
            "email": "rajesh.gupta@mit.edu",
            "phone": "+91-9876543224",
            "designation": "Professor",
            "subject": "Artificial Intelligence",
            "department_id": "CS",
            "departmentId": "Computer Science",
            "qualification": "Ph.D. in AI/ML",
            "employment_status": "Active",
            "joining_date": datetime(2008, 3, 15),
            "experience_years": 16,
            "attendance_rate": 93,
            "pass_rate": 94,
            "specialization": "Deep Learning",
            "status": "Top",
            "cgpa": 8.6,
            "office_location": "Building A, Room 401",
        },
        {
            "name": "Dr. Priya Sharma",
            "employeeId": "FAC016",
            "email": "priya.sharma@mit.edu",
            "phone": "+91-9876543225",
            "designation": "Associate Professor",
            "subject": "Web Development",
            "department_id": "CS",
            "departmentId": "Computer Science",
            "qualification": "Ph.D. in Computer Science",
            "employment_status": "Active",
            "joining_date": datetime(2015, 6, 1),
            "experience_years": 9,
            "attendance_rate": 89,
            "pass_rate": 91,
            "specialization": "Full Stack Development",
            "status": "Top",
            "cgpa": 8.4,
            "office_location": "Building A, Room 305",
        },
        {
            "name": "Mr. Arjun Singh",
            "employeeId": "FAC017",
            "email": "arjun.singh@mit.edu",
            "phone": "+91-9876543226",
            "designation": "Assistant Professor",
            "subject": "Cybersecurity",
            "department_id": "CS",
            "departmentId": "Computer Science",
            "qualification": "M.Tech in Cybersecurity",
            "employment_status": "Active",
            "joining_date": datetime(2021, 8, 15),
            "experience_years": 2,
            "attendance_rate": 86,
            "pass_rate": 84,
            "specialization": "Network Security",
            "status": "Good",
            "cgpa": 8.2,
            "office_location": "Building A, Room 306",
        },
        # Additional ECE Faculty
        {
            "name": "Prof. Harsha Kapoor",
            "employeeId": "FAC018",
            "email": "harsha.kapoor@mit.edu",
            "phone": "+91-9876543227",
            "designation": "Professor",
            "subject": "Power Systems",
            "department_id": "ECE",
            "departmentId": "Electronics & Communication",
            "qualification": "Ph.D. in Power Electronics",
            "employment_status": "Active",
            "joining_date": datetime(2009, 5, 1),
            "experience_years": 15,
            "attendance_rate": 90,
            "pass_rate": 88,
            "specialization": "Renewable Energy",
            "status": "Top",
            "cgpa": 8.3,
            "office_location": "Building B, Room 401",
        },
        {
            "name": "Dr. Neha Kapadia",
            "employeeId": "FAC019",
            "email": "neha.kapadia@mit.edu",
            "phone": "+91-9876543228",
            "designation": "Associate Professor",
            "subject": "Communications",
            "department_id": "ECE",
            "departmentId": "Electronics & Communication",
            "qualification": "Ph.D. in Wireless Communications",
            "employment_status": "Active",
            "joining_date": datetime(2016, 7, 1),
            "experience_years": 8,
            "attendance_rate": 87,
            "pass_rate": 86,
            "specialization": "5G Networks",
            "status": "Good",
            "cgpa": 8.2,
            "office_location": "Building B, Room 405",
        },
        {
            "name": "Ms. Sneha Patel",
            "employeeId": "FAC020",
            "email": "sneha.patel@mit.edu",
            "phone": "+91-9876543229",
            "designation": "Assistant Professor",
            "subject": "Embedded Systems",
            "department_id": "ECE",
            "departmentId": "Electronics & Communication",
            "qualification": "M.Tech in Electronics",
            "employment_status": "Active",
            "joining_date": datetime(2020, 9, 1),
            "experience_years": 3,
            "attendance_rate": 83,
            "pass_rate": 80,
            "specialization": "IoT Devices",
            "status": "Watch",
            "cgpa": 7.9,
            "office_location": "Building B, Room 406",
        },
        # Additional Mathematics Faculty
        {
            "name": "Prof. Vijay Kumar",
            "employeeId": "FAC021",
            "email": "vijay.kumar@mit.edu",
            "phone": "+91-9876543230",
            "designation": "Professor",
            "subject": "Complex Analysis",
            "department_id": "MATH",
            "departmentId": "Mathematics",
            "qualification": "Ph.D. in Mathematics",
            "employment_status": "Active",
            "joining_date": datetime(2011, 4, 1),
            "experience_years": 13,
            "attendance_rate": 88,
            "pass_rate": 87,
            "specialization": "Mathematical Analysis",
            "status": "Good",
            "cgpa": 8.2,
            "office_location": "Building C, Room 401",
        },
        {
            "name": "Dr. Meera Singh",
            "employeeId": "FAC022",
            "email": "meera.singh@mit.edu",
            "phone": "+91-9876543231",
            "designation": "Associate Professor",
            "subject": "Numerical Methods",
            "department_id": "MATH",
            "departmentId": "Mathematics",
            "qualification": "Ph.D. in Computational Mathematics",
            "employment_status": "Active",
            "joining_date": datetime(2017, 8, 1),
            "experience_years": 7,
            "attendance_rate": 86,
            "pass_rate": 84,
            "specialization": "Scientific Computing",
            "status": "Good",
            "cgpa": 8.1,
            "office_location": "Building C, Room 405",
        },
        # Additional Mechanical Engineering Faculty
        {
            "name": "Prof. Ashok Verma",
            "employeeId": "FAC023",
            "email": "ashok.verma@mit.edu",
            "phone": "+91-9876543232",
            "designation": "Professor",
            "subject": "Robotics",
            "department_id": "ME",
            "departmentId": "Mechanical Engineering",
            "qualification": "Ph.D. in Mechanical Engineering",
            "employment_status": "Active",
            "joining_date": datetime(2009, 9, 1),
            "experience_years": 14,
            "attendance_rate": 89,
            "pass_rate": 90,
            "specialization": "Industrial Automation",
            "status": "Top",
            "cgpa": 8.4,
            "office_location": "Building D, Room 401",
        },
        {
            "name": "Dr. Divya Menon",
            "employeeId": "FAC024",
            "email": "divya.menon@mit.edu",
            "phone": "+91-9876543233",
            "designation": "Associate Professor",
            "subject": "Fluid Mechanics",
            "department_id": "ME",
            "departmentId": "Mechanical Engineering",
            "qualification": "Ph.D. in Fluid Dynamics",
            "employment_status": "Active",
            "joining_date": datetime(2016, 5, 1),
            "experience_years": 8,
            "attendance_rate": 85,
            "pass_rate": 83,
            "specialization": "Aerodynamics",
            "status": "Good",
            "cgpa": 8.0,
            "office_location": "Building D, Room 405",
        },
        {
            "name": "Mr. Karan Reddy",
            "employeeId": "FAC025",
            "email": "karan.reddy@mit.edu",
            "phone": "+91-9876543234",
            "designation": "Lecturer",
            "subject": "Materials Science",
            "department_id": "ME",
            "departmentId": "Mechanical Engineering",
            "qualification": "B.Tech in Mechanical Engineering",
            "employment_status": "Active",
            "joining_date": datetime(2022, 1, 15),
            "experience_years": 1,
            "attendance_rate": 92,
            "pass_rate": 88,
            "specialization": "Material Testing",
            "status": "Good",
            "cgpa": 8.0,
            "office_location": "Building D, Room 406",
        },
        # Additional ECE Faculty
        {
            "name": "Prof. Ravi Teja",
            "employeeId": "FAC026",
            "email": "ravi.teja@mit.edu",
            "phone": "+91-9876543235",
            "designation": "Professor",
            "subject": "Control Systems",
            "department_id": "ECE",
            "departmentId": "Electronics & Communication",
            "qualification": "Ph.D. in Control Systems",
            "employment_status": "Active",
            "joining_date": datetime(2010, 2, 1),
            "experience_years": 14,
            "attendance_rate": 91,
            "pass_rate": 89,
            "specialization": "Process Control",
            "status": "Top",
            "cgpa": 8.3,
            "office_location": "Building B, Room 407",
        },
        {
            "name": "Dr. Anjana Das",
            "employeeId": "FAC027",
            "email": "anjana.das@mit.edu",
            "phone": "+91-9876543236",
            "designation": "Associate Professor",
            "subject": "Microelectronics",
            "department_id": "ECE",
            "departmentId": "Electronics & Communication",
            "qualification": "Ph.D. in Electronics",
            "employment_status": "Active",
            "joining_date": datetime(2015, 10, 1),
            "experience_years": 8,
            "attendance_rate": 88,
            "pass_rate": 87,
            "specialization": "Semiconductor Devices",
            "status": "Good",
            "cgpa": 8.2,
            "office_location": "Building B, Room 408",
        },
        # Additional Computer Science Faculty
        {
            "name": "Prof. Suresh Nair",
            "employeeId": "FAC028",
            "email": "suresh.nair@mit.edu",
            "phone": "+91-9876543237",
            "designation": "Professor",
            "subject": "Cloud Computing",
            "department_id": "CS",
            "departmentId": "Computer Science",
            "qualification": "Ph.D. in Computer Science",
            "employment_status": "Active",
            "joining_date": datetime(2007, 7, 1),
            "experience_years": 17,
            "attendance_rate": 92,
            "pass_rate": 91,
            "specialization": "Distributed Systems",
            "status": "Top",
            "cgpa": 8.5,
            "office_location": "Building A, Room 307",
        },
        {
            "name": "Dr. Swati Varma",
            "employeeId": "FAC029",
            "email": "swati.varma@mit.edu",
            "phone": "+91-9876543238",
            "designation": "Associate Professor",
            "subject": "Mobile Computing",
            "department_id": "CS",
            "departmentId": "Computer Science",
            "qualification": "Ph.D. in Software Engineering",
            "employment_status": "Active",
            "joining_date": datetime(2016, 3, 1),
            "experience_years": 8,
            "attendance_rate": 87,
            "pass_rate": 89,
            "specialization": "Android Development",
            "status": "Good",
            "cgpa": 8.2,
            "office_location": "Building A, Room 308",
        },
        {
            "name": "Ms. Priya Dutta",
            "employeeId": "FAC030",
            "email": "priya.dutta@mit.edu",
            "phone": "+91-9876543239",
            "designation": "Assistant Professor",
            "subject": "Data Mining",
            "department_id": "CS",
            "departmentId": "Computer Science",
            "qualification": "M.Tech in Computer Science",
            "employment_status": "Active",
            "joining_date": datetime(2021, 1, 1),
            "experience_years": 3,
            "attendance_rate": 84,
            "pass_rate": 82,
            "specialization": "Big Data Analytics",
            "status": "Good",
            "cgpa": 8.1,
            "office_location": "Building A, Room 309",
        }
    ]
    
    try:
        # Delete existing data
        await collection.delete_many({})
        
        # Insert new data
        result = await collection.insert_many(faculty_data)
        
        return {
            "status": "success",
            "message": f"Inserted {len(result.inserted_ids)} faculty members with detailed metrics",
            "count": len(result.inserted_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------
# Faculty CRUD
# -----------------

@router.get("")
async def list_faculty(
    department_id: Optional[str] = Query(None, alias="departmentId"),
    designation: Optional[str] = None,
    employment_status: Optional[str] = Query(None, alias="employmentStatus"),
    search: Optional[str] = None
):
    collection = await get_faculty_collection()
    perf_col = await get_faculty_activity_collection("faculty_performance")
    leave_col = await get_faculty_activity_collection("faculty_leave")
    career_col = await get_faculty_activity_collection("career_pathways")
    
    query = {}
    if department_id:
        query["departmentId"] = department_id
    if designation:
        query["designation"] = designation
    if employment_status:
        query["employment_status"] = employment_status
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"employeeId": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
        
    cursor = collection.find(query)
    faculty_list = []
    async for doc in cursor:
        faculty_doc = serialize_doc(doc)
        emp_id = faculty_doc.get("employeeId")

        if emp_id:
            performance_records = await perf_col.find({"facultyId": emp_id}).to_list(100)
            leave_records = await leave_col.find({"facultyId": emp_id}).to_list(200)
            career_path = await career_col.find_one(
                {"faculty_id": emp_id, "status": "Active"}
            )
            if not career_path:
                career_path = await career_col.find_one({"faculty_id": emp_id})

            avg_feedback = 0
            if performance_records:
                scored = [
                    float(record.get("student_feedback_score", 0) or 0)
                    for record in performance_records
                ]
                avg_feedback = round(sum(scored) / len(scored), 2)

            approved_leaves = [
                record for record in leave_records if str(record.get("status", "")).lower() == "approved"
            ]
            pending_leaves = [
                record for record in leave_records if str(record.get("status", "")).lower() == "pending"
            ]

            total_leave_days = 0
            for leave in approved_leaves:
                try:
                    start_date = leave.get("start_date")
                    end_date = leave.get("end_date")
                    if isinstance(start_date, datetime) and isinstance(end_date, datetime):
                        total_leave_days += max((end_date - start_date).days + 1, 0)
                    else:
                        total_leave_days += int(leave.get("number_of_days", 0) or 0)
                except Exception:
                    continue

            next_role = None
            designation = str(faculty_doc.get("designation", "")).lower()
            if designation:
                if "assistant" in designation:
                    next_role = "Associate Professor"
                elif "associate" in designation:
                    next_role = "Professor"
                elif "professor" in designation:
                    next_role = "HOD / Dean Track"
                else:
                    next_role = "Senior Faculty"

            faculty_doc["performance_summary"] = {
                "overall_status": faculty_doc.get("status", "Good"),
                "pass_rate": faculty_doc.get("pass_rate", 0),
                "attendance_rate": faculty_doc.get("attendance_rate", 0),
                "avg_feedback_score": avg_feedback,
                "records_count": len(performance_records),
            }

            faculty_doc["career_path_summary"] = {
                "current_designation": faculty_doc.get("designation"),
                "next_role": (career_path or {}).get("target_designation") or next_role,
                "status": (career_path or {}).get("status") or "Not Started",
                "target_years": (career_path or {}).get("target_years"),
            }

            faculty_doc["leave_attendance_summary"] = {
                "employment_status": faculty_doc.get("employment_status", "Active"),
                "attendance_rate": faculty_doc.get("attendance_rate", 0),
                "leave_requests_count": len(leave_records),
                "approved_leaves": len(approved_leaves),
                "pending_leaves": len(pending_leaves),
                "total_leave_days": total_leave_days,
            }

        faculty_list.append(faculty_doc)
    return faculty_list

@router.post("")
async def create_faculty(faculty: Faculty):
    collection = await get_faculty_collection()
    
    # Check if employee_id already exists
    existing = await collection.find_one({"employeeId": faculty.employee_id})
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
        
    faculty_dict = faculty.dict(by_alias=True)
    result = await collection.insert_one(faculty_dict)
    
    created_doc = await collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_doc)


@router.post("/admission/submit")
async def submit_faculty_admission(faculty_data: dict = Body(...)):
    """Submit faculty admission from modal form"""
    collection = await get_faculty_collection()
    
    # Allow duplicate submissions (no uniqueness check)
    result = await collection.insert_one(faculty_data)
    
    created_doc = await collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_doc)


@router.get("/{faculty_id}")
async def get_faculty(faculty_id: str = Path(...)):
    collection = await get_faculty_collection()
    try:
        obj_id = ObjectId(faculty_id)
        doc = await collection.find_one({"_id": obj_id})
    except:
        doc = await collection.find_one({"employeeId": faculty_id})
        
    if not doc:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Fetch related data
    doc_serialized = serialize_doc(doc)
    emp_id = doc_serialized.get("employeeId")
    
    # Courses
    courses_col = await get_faculty_activity_collection("faculty_courses")
    courses = []
    if emp_id:
        async for c in courses_col.find({"facultyId": emp_id}):
            courses.append(serialize_doc(c))
    doc_serialized["teaching_load"] = courses
    
    # Performance
    perf_col = await get_faculty_activity_collection("faculty_performance")
    performance = []
    if emp_id:
        async for p in perf_col.find({"facultyId": emp_id}):
            performance.append(serialize_doc(p))
    doc_serialized["performance_metrics"] = performance
    
    # Development
    dev_col = await get_faculty_activity_collection("faculty_development")
    devs = []
    if emp_id:
        async for d in dev_col.find({"facultyId": emp_id}):
            devs.append(serialize_doc(d))
    doc_serialized["professional_development"] = devs
    
    # Leave Requests
    leave_col = await get_faculty_activity_collection("faculty_leave")
    leaves = []
    if emp_id:
        async for l in leave_col.find({"facultyId": emp_id}):
            leaves.append(serialize_doc(l))
    doc_serialized["leave_requests"] = leaves
    
    # Mentorships
    mentor_col = await get_faculty_activity_collection("faculty_mentorship")
    mentorships = []
    if emp_id:
        async for m in mentor_col.find({"$or": [{"mentorId": emp_id}, {"menteeId": emp_id}]}):
            mentorships.append(serialize_doc(m))
    doc_serialized["mentorships"] = mentorships
    
    # Research Projects
    research_col = await get_faculty_activity_collection("faculty_research")
    research = []
    if emp_id:
        async for r in research_col.find({"$or": [{"leadFacultyId": emp_id}, {"collaboratorIds": emp_id}]}):
            research.append(serialize_doc(r))
    doc_serialized["research_projects"] = research
    
    # Peer Reviews
    review_col = await get_faculty_activity_collection("faculty_peer_reviews")
    reviews = []
    if emp_id:
        async for pr in review_col.find({"revieweeId": emp_id}):
            reviews.append(serialize_doc(pr))
    doc_serialized["peer_reviews"] = reviews
    
    return doc_serialized

@router.put("/{faculty_id}")
async def update_faculty(faculty_id: str, updates: Dict[str, Any] = Body(...)):
    collection = await get_faculty_collection()
    try:
        query = {"_id": ObjectId(faculty_id)}
    except:
        query = {"employeeId": faculty_id}
        
    # Prevent updating _id or core immutable fields if needed
    if "_id" in updates:
        del updates["_id"]
        
    result = await collection.update_one(query, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Faculty not found")
        
    updated_doc = await collection.find_one(query)
    return serialize_doc(updated_doc)

@router.delete("/{faculty_id}")
async def delete_faculty(faculty_id: str):
    collection = await get_faculty_collection()
    try:
        query = {"_id": ObjectId(faculty_id)}
    except:
        query = {"employeeId": faculty_id}
        
    result = await collection.delete_one(query)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Faculty not found")
        
    return {"status": "success", "message": "Faculty deleted"}


# -----------------
# Faculty Course Mapping
# -----------------

@router.post("/{faculty_id}/courses")
async def assign_course(faculty_id: str, assignment: CourseAssignment):
    collection = await get_faculty_activity_collection("faculty_courses")
    
    # Validate faculty exists
    fac_col = await get_faculty_collection()
    try:
        query = {"_id": ObjectId(faculty_id)}
    except:
        query = {"employeeId": faculty_id}
    if not await fac_col.find_one(query):
        raise HTTPException(status_code=404, detail="Faculty not found")
        
    # Ensure facultyId matches
    assignment_dict = assignment.dict(by_alias=True)
    if assignment_dict["facultyId"] != faculty_id:
        if assignment_dict["facultyId"] == "string": # Default swagger value
            assignment_dict["facultyId"] = faculty_id
        else:
            raise HTTPException(status_code=400, detail="Faculty ID mismatch")
            
    result = await collection.insert_one(assignment_dict)
    doc = await collection.find_one({"_id": result.inserted_id})
    return serialize_doc(doc)


# -----------------
# Faculty Performance
# -----------------

@router.post("/{faculty_id}/performance")
async def add_performance_metric(faculty_id: str, metric: PerformanceMetric):
    collection = await get_faculty_activity_collection("faculty_performance")
    
    metric_dict = metric.dict(by_alias=True)
    if metric_dict["facultyId"] != faculty_id:
        if metric_dict["facultyId"] == "string":
            metric_dict["facultyId"] = faculty_id
        else:
            raise HTTPException(status_code=400, detail="Faculty ID mismatch")
            
    result = await collection.insert_one(metric_dict)
    doc = await collection.find_one({"_id": result.inserted_id})
    return serialize_doc(doc)


# -----------------
# Professional Development
# -----------------

@router.post("/{faculty_id}/development")
async def add_development_record(faculty_id: str, dev: ProfessionalDevelopment):
    collection = await get_faculty_activity_collection("faculty_development")
    
    dev_dict = dev.dict(by_alias=True)
    if dev_dict["facultyId"] != faculty_id:
         if dev_dict["facultyId"] == "string":
             dev_dict["facultyId"] = faculty_id
         else:
             raise HTTPException(status_code=400, detail="Faculty ID mismatch")
             
    result = await collection.insert_one(dev_dict)
    doc = await collection.find_one({"_id": result.inserted_id})
    return serialize_doc(doc)

# -----------------
# Leave Management
# -----------------

@router.post("/{faculty_id}/leave")
async def request_leave(faculty_id: str, leave: FacultyLeave):
    collection = await get_faculty_activity_collection("faculty_leave")
    
    leave_dict = leave.dict(by_alias=True)
    if leave_dict["facultyId"] != faculty_id:
        if leave_dict["facultyId"] == "string":
            leave_dict["facultyId"] = faculty_id
        else:
            raise HTTPException(status_code=400, detail="Faculty ID mismatch")
            
    result = await collection.insert_one(leave_dict)
    doc = await collection.find_one({"_id": result.inserted_id})
    return serialize_doc(doc)

@router.get("/{faculty_id}/leave")
async def get_leave_requests(faculty_id: str):
    collection = await get_faculty_activity_collection("faculty_leave")
    
    requests = []
    async for req in collection.find({"facultyId": faculty_id}):
        requests.append(serialize_doc(req))
    return requests

@router.put("/leave/{leave_id}")
async def update_leave_status(leave_id: str, updates: Dict[str, Any] = Body(...)):
    collection = await get_faculty_activity_collection("faculty_leave")
    
    result = await collection.update_one(
        {"_id": ObjectId(leave_id)},
        {"$set": updates}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Leave request not found")
        
    updated_doc = await collection.find_one({"_id": ObjectId(leave_id)})
    return serialize_doc(updated_doc)

# -----------------
# Mentorship
# -----------------

@router.post("/{faculty_id}/mentorship")
async def add_mentorship(faculty_id: str, mentorship: FacultyMentorship):
    collection = await get_faculty_activity_collection("faculty_mentorship")
    mentorship_dict = mentorship.dict(by_alias=True)
    if mentorship_dict["mentorId"] != faculty_id and mentorship_dict["menteeId"] != faculty_id:
        if mentorship_dict["mentorId"] == "string":
            mentorship_dict["mentorId"] = faculty_id
        else:
            raise HTTPException(status_code=400, detail="Faculty ID mismatch")
            
    result = await collection.insert_one(mentorship_dict)
    doc = await collection.find_one({"_id": result.inserted_id})
    return serialize_doc(doc)

@router.get("/{faculty_id}/mentorship")
async def get_mentorships(faculty_id: str):
    collection = await get_faculty_activity_collection("faculty_mentorship")
    mentorships = []
    async for m in collection.find({"$or": [{"mentorId": faculty_id}, {"menteeId": faculty_id}]}):
        mentorships.append(serialize_doc(m))
    return mentorships

# -----------------
# Research Collaboration
# -----------------

@router.post("/research")
async def add_research_project(project: ResearchProject):
    collection = await get_faculty_activity_collection("faculty_research")
    project_dict = project.dict(by_alias=True)
    result = await collection.insert_one(project_dict)
    doc = await collection.find_one({"_id": result.inserted_id})
    return serialize_doc(doc)

@router.get("/{faculty_id}/research")
async def get_research_projects(faculty_id: str):
    collection = await get_faculty_activity_collection("faculty_research")
    projects = []
    async for p in collection.find({"$or": [{"leadFacultyId": faculty_id}, {"collaboratorIds": faculty_id}]}):
        projects.append(serialize_doc(p))
    return projects

# -----------------
# Peer Review
# -----------------

@router.post("/{faculty_id}/peer-review")
async def add_peer_review(faculty_id: str, review: PeerReview):
    collection = await get_faculty_activity_collection("faculty_peer_reviews")
    review_dict = review.dict(by_alias=True)
    if review_dict["reviewerId"] != faculty_id and review_dict["revieweeId"] != faculty_id:
        if review_dict["reviewerId"] == "string":
             review_dict["reviewerId"] = faculty_id
        else:
             raise HTTPException(status_code=400, detail="Faculty ID mismatch")
             
    result = await collection.insert_one(review_dict)
    doc = await collection.find_one({"_id": result.inserted_id})
    return serialize_doc(doc)

@router.get("/{faculty_id}/peer-review")
async def get_peer_reviews(faculty_id: str):
    collection = await get_faculty_activity_collection("faculty_peer_reviews")
    reviews = []
    async for r in collection.find({"revieweeId": faculty_id}):
        reviews.append(serialize_doc(r))
    return reviews

# -----------------
# Compliance & Notifications
# -----------------

@router.get("/{faculty_id}/notifications")
async def get_notifications(faculty_id: str):
    collection = await get_faculty_activity_collection("faculty_notifications")
    notifications = []
    async for n in collection.find({"recipient_id": faculty_id}):
        notifications.append(serialize_doc(n))
    return notifications

@router.post("/check-compliance")
async def check_compliance():
    faculty_col = await get_faculty_collection()
    notices_col = await get_faculty_activity_collection("faculty_notifications")
    
    current_date = datetime.utcnow()
    count = 0
    
    # Check all active faculty
    async for f in faculty_col.find({"employment_status": "Active"}):
        contract_end = f.get("contract_end_date")
        if contract_end:
            try:
                # Assuming YYYY-MM-DD
                end_date = datetime.strptime(contract_end, "%Y-%m-%d")
                days_left = (end_date - current_date).days
                
                if days_left <= 30 and days_left > 0:
                    # Create notification if it doesn't exist for this period
                    notif = Notification(
                        recipient_id=f.get("employeeId", str(f["_id"])),
                        recipient_type="faculty",
                        title="Contract Renewal Upcoming",
                        message=f"Your contract will expire in {days_left} days on {contract_end}.",
                        notification_type="System"
                    )
                    
                    # Prevent exact duplicate notification
                    existing = await notices_col.find_one({
                        "recipient_id": notif.recipient_id, 
                        "title": notif.title,
                        "is_read": False
                    })
                    
                    if not existing:
                        await notices_col.insert_one(notif.dict())
                        count += 1
                        
            except ValueError:
                pass # ignore poorly formatted dates
                
    return {"status": "success", "notifications_generated": count}

