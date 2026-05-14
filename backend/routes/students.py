from copy import deepcopy

from fastapi import APIRouter, HTTPException
from pymongo import ReturnDocument

from backend.db import get_db
from backend.dev_store import DEV_STORE
from backend.schemas.common import StudentRecord
from backend.utils.mongo import serialize_doc

router = APIRouter(prefix="/api/students", tags=["students"])


def _seed_dev_students() -> None:
    if DEV_STORE.get("students"):
        return

    DEV_STORE["students"] = [
        {
            "id": "STU-2024-1547",
            "rollNumber": "STU-2024-1547",
            "name": "John Anderson",
            "email": "john.anderson@mit.edu",
            "phone": "+91 90123 45678",
            "department": "Computer Science",
            "year": "3rd Year",
            "semester": 6,
            "section": "A",
            "cgpa": 8.7,
            "attendancePct": 92,
            "feeStatus": "Pending",
            "status": "Active",
            "enrollDate": "2022-08-01",
            "address": "18, Lake View Road, Bangalore, Karnataka",
            "guardian": "Michael Anderson",
            "guardianPhone": "+91 90123 45000",
            "avatar": "https://ui-avatars.com/api/?name=John+Anderson&background=2563eb&color=fff&size=128",
            "subjects": [
                {"code": "CS301", "name": "Data Structures", "grade": "A", "total": 86},
                {"code": "CS302", "name": "Operating Systems", "grade": "A", "total": 82},
                {"code": "CS303", "name": "Database Systems", "grade": "A", "total": 86},
                {"code": "CS304", "name": "Computer Networks", "grade": "B+", "total": 72},
                {"code": "MA301", "name": "Discrete Mathematics", "grade": "A", "total": 84},
            ],
            "fees": [
                {"id": "FEE-101", "type": "Tuition Fee", "amount": 75000, "paid": 75000, "due": 0, "date": "2024-07-15", "status": "Paid"},
                {"id": "FEE-102", "type": "Hostel Fee", "amount": 45000, "paid": 30000, "due": 15000, "date": "2024-07-20", "status": "Partial"},
                {"id": "FEE-103", "type": "Exam Fee", "amount": 5000, "paid": 0, "due": 5000, "date": "-", "status": "Unpaid"},
            ],
            "documents": [
                {"id": "DOC-101", "name": "10th Marksheet", "type": "pdf", "uploadDate": "2022-08-01", "size": "1.1 MB"},
                {"id": "DOC-102", "name": "12th Marksheet", "type": "pdf", "uploadDate": "2022-08-01", "size": "1.3 MB"},
                {"id": "DOC-103", "name": "Aadhar Card", "type": "pdf", "uploadDate": "2022-08-02", "size": "0.8 MB"},
                {"id": "DOC-104", "name": "Passport Photo", "type": "image", "uploadDate": "2022-08-02", "size": "0.4 MB"},
            ],
            "attendanceMonthly": [
                {"month": "Jul", "present": 22, "total": 24},
                {"month": "Aug", "present": 23, "total": 26},
            ],
        },
        {
            "id": "STU-2024-001",
            "rollNumber": "STU-2024-001",
            "name": "Aarav Kumar",
            "email": "aarav.kumar@mit.edu",
            "phone": "+91 98765 43210",
            "department": "Computer Science",
            "year": "3rd Year",
            "semester": 6,
            "section": "A",
            "cgpa": 8.7,
            "attendancePct": 92,
            "feeStatus": "Paid",
            "status": "Active",
            "enrollDate": "2022-08-01",
            "address": "12, MG Road, Bangalore, Karnataka",
            "guardian": "Rajesh Kumar",
            "guardianPhone": "+91 98765 43200",
            "avatar": "https://ui-avatars.com/api/?name=Aarav+Kumar&background=2563eb&color=fff&size=128",
            "subjects": [
                {"code": "CS301", "name": "Data Structures", "grade": "A+", "total": 90},
            ],
            "fees": [
                {"id": "FEE-001", "type": "Tuition Fee", "amount": 75000, "paid": 75000, "due": 0, "date": "2024-07-15", "status": "Paid"},
            ],
            "documents": [
                {"id": "DOC-001", "name": "10th Marksheet", "type": "pdf", "uploadDate": "2022-08-01", "size": "1.2 MB"},
            ],
            "attendanceMonthly": [
                {"month": "Jul", "present": 22, "total": 24},
            ],
        },
        {
            "id": "STU-2024-042",
            "rollNumber": "STU-2024-042",
            "name": "Priya Sharma",
            "email": "priya.sharma@mit.edu",
            "phone": "+91 87654 32109",
            "department": "Computer Science",
            "year": "3rd Year",
            "semester": 6,
            "section": "A",
            "cgpa": 9.1,
            "attendancePct": 96,
            "feeStatus": "Paid",
            "status": "Active",
            "enrollDate": "2022-08-01",
            "address": "45, Residency Road, Bangalore",
            "guardian": "Suresh Sharma",
            "guardianPhone": "+91 87654 32100",
            "avatar": "https://ui-avatars.com/api/?name=Priya+Sharma&background=7c3aed&color=fff&size=128",
            "subjects": [
                {"code": "CS301", "name": "Data Structures", "grade": "A+", "total": 94},
            ],
            "fees": [],
            "documents": [],
            "attendanceMonthly": [],
        },
        {
            "id": "STU-2024-118",
            "rollNumber": "STU-2024-118",
            "name": "Vikram Singh",
            "email": "vikram.singh@mit.edu",
            "phone": "+91 76543 21098",
            "department": "Mechanical",
            "year": "2nd Year",
            "semester": 4,
            "section": "B",
            "cgpa": 7.4,
            "attendancePct": 74,
            "feeStatus": "Pending",
            "status": "Active",
            "enrollDate": "2023-08-01",
            "address": "78, Koramangala, Bangalore",
            "guardian": "Harinder Singh",
            "guardianPhone": "+91 76543 21000",
            "avatar": "https://ui-avatars.com/api/?name=Vikram+Singh&background=ea580c&color=fff&size=128",
            "subjects": [
                {"code": "ME201", "name": "Thermodynamics", "grade": "B", "total": 65},
            ],
            "fees": [],
            "documents": [],
            "attendanceMonthly": [],
        },
        {
            "id": "STU-2024-089",
            "rollNumber": "STU-2024-089",
            "name": "Ananya Patel",
            "email": "ananya.patel@mit.edu",
            "phone": "+91 65432 10987",
            "department": "Electronics",
            "year": "4th Year",
            "semester": 8,
            "section": "A",
            "cgpa": 8.2,
            "attendancePct": 88,
            "feeStatus": "Paid",
            "status": "Active",
            "enrollDate": "2021-08-01",
            "address": "23, Indiranagar, Bangalore",
            "guardian": "Mahesh Patel",
            "guardianPhone": "+91 65432 10900",
            "avatar": "https://ui-avatars.com/api/?name=Ananya+Patel&background=059669&color=fff&size=128",
            "subjects": [],
            "fees": [],
            "documents": [],
            "attendanceMonthly": [],
        },
        {
            "id": "STU-2024-203",
            "rollNumber": "STU-2024-203",
            "name": "Rohan Mehta",
            "email": "rohan.mehta@mit.edu",
            "phone": "+91 54321 09876",
            "department": "Computer Science",
            "year": "2nd Year",
            "semester": 4,
            "section": "B",
            "cgpa": 7.9,
            "attendancePct": 81,
            "feeStatus": "Paid",
            "status": "Active",
            "enrollDate": "2023-08-01",
            "address": "56, Whitefield, Bangalore",
            "guardian": "Deepak Mehta",
            "guardianPhone": "+91 54321 09800",
            "avatar": "https://ui-avatars.com/api/?name=Rohan+Mehta&background=0891b2&color=fff&size=128",
            "subjects": [],
            "fees": [],
            "documents": [],
            "attendanceMonthly": [],
        },
        {
            "id": "STU-2024-155",
            "rollNumber": "STU-2024-155",
            "name": "Sneha Reddy",
            "email": "sneha.reddy@mit.edu",
            "phone": "+91 43210 98765",
            "department": "Civil",
            "year": "3rd Year",
            "semester": 6,
            "section": "A",
            "cgpa": 8.5,
            "attendancePct": 90,
            "feeStatus": "Paid",
            "status": "Active",
            "enrollDate": "2022-08-01",
            "address": "89, Jayanagar, Bangalore",
            "guardian": "Venkat Reddy",
            "guardianPhone": "+91 43210 98700",
            "avatar": "https://ui-avatars.com/api/?name=Sneha+Reddy&background=dc2626&color=fff&size=128",
            "subjects": [],
            "fees": [],
            "documents": [],
            "attendanceMonthly": [],
        },
        {
            "id": "STU-2024-077",
            "rollNumber": "STU-2024-077",
            "name": "Karthik Nair",
            "email": "karthik.nair@mit.edu",
            "phone": "+91 32109 87654",
            "department": "Mechanical",
            "year": "4th Year",
            "semester": 8,
            "section": "A",
            "cgpa": 6.8,
            "attendancePct": 68,
            "feeStatus": "Overdue",
            "status": "Active",
            "enrollDate": "2021-08-01",
            "address": "34, Electronic City, Bangalore",
            "guardian": "Ramesh Nair",
            "guardianPhone": "+91 32109 87600",
            "avatar": "https://ui-avatars.com/api/?name=Karthik+Nair&background=b91c1c&color=fff&size=128",
            "subjects": [],
            "fees": [],
            "documents": [],
            "attendanceMonthly": [],
        },
        {
            "id": "STU-2024-190",
            "rollNumber": "STU-2024-190",
            "name": "Divya Iyer",
            "email": "divya.iyer@mit.edu",
            "phone": "+91 21098 76543",
            "department": "Electronics",
            "year": "2nd Year",
            "semester": 4,
            "section": "A",
            "cgpa": 8.9,
            "attendancePct": 94,
            "feeStatus": "Paid",
            "status": "Active",
            "enrollDate": "2023-08-01",
            "address": "67, HSR Layout, Bangalore",
            "guardian": "Subramaniam Iyer",
            "guardianPhone": "+91 21098 76500",
            "avatar": "https://ui-avatars.com/api/?name=Divya+Iyer&background=7c3aed&color=fff&size=128",
            "subjects": [],
            "fees": [],
            "documents": [],
            "attendanceMonthly": [],
        },
        {
            "id": "STU-2023-310",
            "rollNumber": "STU-2023-310",
            "name": "Arjun Desai",
            "email": "arjun.desai@mit.edu",
            "phone": "+91 10987 65432",
            "department": "Computer Science",
            "year": "4th Year",
            "semester": 8,
            "section": "A",
            "cgpa": 7.6,
            "attendancePct": 78,
            "feeStatus": "Pending",
            "status": "Active",
            "enrollDate": "2021-08-01",
            "address": "12, BTM Layout, Bangalore",
            "guardian": "Nikhil Desai",
            "guardianPhone": "+91 10987 65400",
            "avatar": "https://ui-avatars.com/api/?name=Arjun+Desai&background=0d9488&color=fff&size=128",
            "subjects": [],
            "fees": [],
            "documents": [],
            "attendanceMonthly": [],
        },
        {
            "id": "STU-2024-245",
            "rollNumber": "STU-2024-245",
            "name": "Meera Joshi",
            "email": "meera.joshi@mit.edu",
            "phone": "+91 09876 54321",
            "department": "Civil",
            "year": "2nd Year",
            "semester": 4,
            "section": "B",
            "cgpa": 8.0,
            "attendancePct": 85,
            "feeStatus": "Paid",
            "status": "Active",
            "enrollDate": "2023-08-01",
            "address": "90, Marathahalli, Bangalore",
            "guardian": "Anil Joshi",
            "guardianPhone": "+91 09876 54300",
            "avatar": "https://ui-avatars.com/api/?name=Meera+Joshi&background=2563eb&color=fff&size=128",
            "subjects": [],
            "fees": [],
            "documents": [],
            "attendanceMonthly": [],
        },
    ]


@router.get("")
async def list_students():
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            _seed_dev_students()
            return deepcopy(DEV_STORE["students"])
        raise

    rows = []
    async for row in db["students"].find().sort("_id", -1):
        rows.append(serialize_doc(row))
    return rows


@router.get("/{student_id}")
async def get_student(student_id: str):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            _seed_dev_students()
            row = next(
                (
                    item
                    for item in DEV_STORE["students"]
                    if item.get("id") == student_id or item.get("rollNumber") == student_id
                ),
                None,
            )
            if not row:
                raise HTTPException(status_code=404, detail="Student not found")
            return deepcopy(row)
        raise

    row = await db["students"].find_one(
        {"$or": [{"id": student_id}, {"rollNumber": student_id}]}
    )
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")
    return serialize_doc(row)


@router.post("", status_code=201)
async def create_student(payload: StudentRecord):
    data = payload.model_dump()

    if not data.get("rollNumber"):
        data["rollNumber"] = data["id"]

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            _seed_dev_students()
            exists = next(
                (
                    item
                    for item in DEV_STORE["students"]
                    if item.get("id") == data["id"] or item.get("rollNumber") == data["rollNumber"]
                ),
                None,
            )
            if exists:
                raise HTTPException(status_code=400, detail="Student with this id already exists")
            DEV_STORE["students"].insert(0, deepcopy(data))
            return data
        raise

    exists = await db["students"].find_one(
        {"$or": [{"id": data["id"]}, {"rollNumber": data["rollNumber"]}]}
    )
    if exists:
        raise HTTPException(status_code=400, detail="Student with this id already exists")

    result = await db["students"].insert_one(data)
    created = await db["students"].find_one({"_id": result.inserted_id})
    return serialize_doc(created)


@router.put("/{student_id}")
async def update_student(student_id: str, payload: dict):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            _seed_dev_students()
            target = next(
                (
                    item
                    for item in DEV_STORE["students"]
                    if item.get("id") == student_id or item.get("rollNumber") == student_id
                ),
                None,
            )
            if not target:
                raise HTTPException(status_code=404, detail="Student not found")
            target.update(payload)
            return deepcopy(target)
        raise

    result = await db["students"].find_one_and_update(
        {"$or": [{"id": student_id}, {"rollNumber": student_id}]},
        {"$set": payload},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Student not found")
    return serialize_doc(result)


@router.delete("/{student_id}")
async def delete_student(student_id: str):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            _seed_dev_students()
            before = len(DEV_STORE["students"])
            DEV_STORE["students"] = [
                item
                for item in DEV_STORE["students"]
                if item.get("id") != student_id and item.get("rollNumber") != student_id
            ]
            if len(DEV_STORE["students"]) == before:
                raise HTTPException(status_code=404, detail="Student not found")
            return {"message": "Student deleted"}
        raise

    result = await db["students"].delete_one(
        {"$or": [{"id": student_id}, {"rollNumber": student_id}]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted"}

@router.post("/{student_id}/subjects")
async def add_student_subject(student_id: str, subject: dict):
    """Adds a new academic record (subject) to a student."""
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            _seed_dev_students()
            target = next(
                (item for item in DEV_STORE["students"] 
                 if item.get("id") == student_id or item.get("rollNumber") == student_id),
                None
            )
            if not target:
                raise HTTPException(status_code=404, detail="Student not found")
            if "subjects" not in target:
                target["subjects"] = []
            target["subjects"].append(subject)
            return subject
        raise

    result = await db["students"].find_one_and_update(
        {"$or": [{"id": student_id}, {"rollNumber": student_id}]},
        {"$push": {"subjects": subject}},
        return_document=ReturnDocument.AFTER
    )
    if not result:
        raise HTTPException(status_code=404, detail="Student not found")
    return subject
