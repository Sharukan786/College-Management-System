from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pymongo import ReturnDocument

from backend.db import get_db
from backend.dev_store import DEV_STORE
from backend.dev_store import create_exam as create_dev_exam
from backend.dev_store import delete_exam as delete_dev_exam
from backend.dev_store import list_items
from backend.dev_store import update_exam as update_dev_exam
from backend.schemas.academics import ExamCreate, ExamUpdate
from backend.utils.mongo import serialize_doc

router = APIRouter(prefix="/api/exams", tags=["academics:exams"])


def _id_query(id_value: str):
    query = {"id": id_value}
    if ObjectId.is_valid(id_value):
        query = {"$or": [{"_id": ObjectId(id_value)}, {"id": id_value}]}
    return query


def _now_iso():
    return datetime.utcnow().isoformat()


def _new_id(prefix: str):
    return f"{prefix}_{uuid4().hex[:12]}"


def _dev_list(key: str):
    return DEV_STORE.setdefault(key, [])


def _dev_get(key: str, item_id: str):
    return next((item for item in _dev_list(key) if str(item.get("id")) == str(item_id)), None)


@router.get("")
async def list_exams():
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {"success": True, "data": list_items("exams")}
        raise
    exams = []
    async for exam in db["exams"].find().sort("date", 1):
        exams.append(serialize_doc(exam))
    return {"success": True, "data": exams}


@router.post("")
async def create_exam(payload: ExamCreate):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {"success": True, "data": create_dev_exam(payload.model_dump())}
        raise
    result = await db["exams"].insert_one(payload.model_dump())
    created = await db["exams"].find_one({"_id": result.inserted_id})
    return {"success": True, "data": serialize_doc(created)}


@router.put("/{exam_id}")
async def update_exam(exam_id: str, payload: ExamUpdate):
    update_data = {key: value for key, value in payload.model_dump().items() if value is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            updated = update_dev_exam(exam_id, update_data)
            if not updated:
                raise HTTPException(status_code=404, detail="Exam not found")
            return {"success": True, "data": updated}
        raise

    updated = await db["exams"].find_one_and_update(
        _id_query(exam_id),
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Exam not found")

    return {"success": True, "data": serialize_doc(updated)}


@router.delete("/{exam_id}")
async def delete_exam(exam_id: str):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            deleted = delete_dev_exam(exam_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="Exam not found")
            return {"success": True, "message": "Exam deleted"}
        raise
    result = await db["exams"].delete_one(_id_query(exam_id))
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Exam not found")
    return {"success": True, "message": "Exam deleted"}


@router.patch("/{exam_id}/publish-results")
async def publish_exam_results(exam_id: str):
    patch = {"resultsPublished": True, "updatedAt": _now_iso()}
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            updated = update_dev_exam(exam_id, patch)
            if not updated:
                raise HTTPException(status_code=404, detail="Exam not found")
            return {"success": True, "data": updated}
        raise

    updated = await db["exams"].find_one_and_update(
        _id_query(exam_id),
        {"$set": patch},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Exam not found")
    return {"success": True, "data": serialize_doc(updated)}


@router.get("/registrations")
async def list_registrations(exam_id: Optional[str] = None, student_id: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_registrations")
            if exam_id:
                items = [item for item in items if str(item.get("examId")) == str(exam_id)]
            if student_id:
                items = [item for item in items if str(item.get("studentId")) == str(student_id)]
            return {"success": True, "data": items}
        raise

    query = {}
    if exam_id:
        query["examId"] = exam_id
    if student_id:
        query["studentId"] = student_id
    rows = []
    async for row in db["exam_registrations"].find(query).sort("registeredAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.post("/registrations")
async def create_registration(payload: dict):
    exam_id = payload.get("examId")
    student_id = payload.get("studentId")
    student_name = payload.get("studentName", "")
    if not exam_id or not student_id:
        raise HTTPException(status_code=400, detail="examId and studentId are required")

    data = {
        "id": payload.get("id") or _new_id("reg"),
        "examId": exam_id,
        "studentId": student_id,
        "studentName": student_name,
        "status": payload.get("status") or "Registered",
        "registeredAt": payload.get("registeredAt") or _now_iso(),
    }

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_registrations")
            duplicate = next((item for item in items if str(item.get("examId")) == str(exam_id) and str(item.get("studentId")) == str(student_id)), None)
            if duplicate:
                raise HTTPException(status_code=400, detail="Already registered for this exam")
            items.append(data)
            return {"success": True, "data": data}
        raise

    duplicate = await db["exam_registrations"].find_one({"examId": exam_id, "studentId": student_id})
    if duplicate:
        raise HTTPException(status_code=400, detail="Already registered for this exam")

    await db["exam_registrations"].insert_one(data)
    return {"success": True, "data": data}


@router.get("/marks")
async def list_marks(exam_id: Optional[str] = None, student_id: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_marks")
            if exam_id:
                items = [item for item in items if str(item.get("examId")) == str(exam_id)]
            if student_id:
                items = [item for item in items if str(item.get("studentId")) == str(student_id)]
            return {"success": True, "data": items}
        raise

    query = {}
    if exam_id:
        query["examId"] = exam_id
    if student_id:
        query["studentId"] = student_id
    rows = []
    async for row in db["exam_marks"].find(query).sort("updatedAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.put("/marks")
async def upsert_mark(payload: dict):
    exam_id = payload.get("examId")
    student_id = payload.get("studentId")
    if not exam_id or not student_id:
        raise HTTPException(status_code=400, detail="examId and studentId are required")

    data = {
        "examId": exam_id,
        "studentId": student_id,
        "marks": payload.get("marks"),
        "grade": payload.get("grade"),
        "enteredBy": payload.get("enteredBy", ""),
        "maxMarks": payload.get("maxMarks"),
        "updatedAt": _now_iso(),
    }

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_marks")
            existing = next((item for item in items if str(item.get("examId")) == str(exam_id) and str(item.get("studentId")) == str(student_id)), None)
            if existing:
                existing.update(data)
                existing["id"] = existing.get("id") or _new_id("mark")
                existing["enteredAt"] = existing.get("enteredAt") or _now_iso()
                return {"success": True, "data": existing}
            created = {"id": _new_id("mark"), "enteredAt": _now_iso(), **data}
            items.append(created)
            return {"success": True, "data": created}
        raise

    updated = await db["exam_marks"].find_one_and_update(
        {"examId": exam_id, "studentId": student_id},
        {"$set": data, "$setOnInsert": {"id": _new_id("mark"), "enteredAt": _now_iso()}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return {"success": True, "data": serialize_doc(updated)}


@router.get("/internal-marks")
async def list_internal_marks(exam_id: Optional[str] = None, student_id: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_internal_marks")
            if exam_id:
                items = [item for item in items if str(item.get("examId")) == str(exam_id)]
            if student_id:
                items = [item for item in items if str(item.get("studentId")) == str(student_id)]
            return {"success": True, "data": items}
        raise

    query = {}
    if exam_id:
        query["examId"] = exam_id
    if student_id:
        query["studentId"] = student_id
    rows = []
    async for row in db["exam_internal_marks"].find(query).sort("updatedAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.put("/internal-marks")
async def upsert_internal_mark(payload: dict):
    exam_id = payload.get("examId")
    student_id = payload.get("studentId")
    if not exam_id or not student_id:
        raise HTTPException(status_code=400, detail="examId and studentId are required")

    data = {
        "examId": exam_id,
        "studentId": student_id,
        "internalMarks": payload.get("internalMarks"),
        "maxInternal": payload.get("maxInternal"),
        "enteredBy": payload.get("enteredBy", ""),
        "updatedAt": _now_iso(),
    }

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_internal_marks")
            existing = next((item for item in items if str(item.get("examId")) == str(exam_id) and str(item.get("studentId")) == str(student_id)), None)
            if existing:
                existing.update(data)
                existing["id"] = existing.get("id") or _new_id("imark")
                existing["enteredAt"] = existing.get("enteredAt") or _now_iso()
                return {"success": True, "data": existing}
            created = {"id": _new_id("imark"), "enteredAt": _now_iso(), **data}
            items.append(created)
            return {"success": True, "data": created}
        raise

    updated = await db["exam_internal_marks"].find_one_and_update(
        {"examId": exam_id, "studentId": student_id},
        {"$set": data, "$setOnInsert": {"id": _new_id("imark"), "enteredAt": _now_iso()}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return {"success": True, "data": serialize_doc(updated)}


@router.get("/attendance")
async def list_exam_attendance(exam_id: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_attendance")
            if exam_id:
                items = [item for item in items if str(item.get("examId")) == str(exam_id)]
            return {"success": True, "data": items}
        raise

    query = {"examId": exam_id} if exam_id else {}
    rows = []
    async for row in db["exam_attendance"].find(query).sort("updatedAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.put("/attendance")
async def upsert_exam_attendance(payload: dict):
    exam_id = payload.get("examId")
    student_id = payload.get("studentId")
    if not exam_id or not student_id:
        raise HTTPException(status_code=400, detail="examId and studentId are required")

    data = {
        "examId": exam_id,
        "studentId": student_id,
        "status": payload.get("status") or "Present",
        "markedBy": payload.get("markedBy", ""),
        "updatedAt": _now_iso(),
    }

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_attendance")
            existing = next((item for item in items if str(item.get("examId")) == str(exam_id) and str(item.get("studentId")) == str(student_id)), None)
            if existing:
                existing.update(data)
                existing["id"] = existing.get("id") or _new_id("eatt")
                existing["markedAt"] = existing.get("markedAt") or _now_iso()
                return {"success": True, "data": existing}
            created = {"id": _new_id("eatt"), "markedAt": _now_iso(), **data}
            items.append(created)
            return {"success": True, "data": created}
        raise

    updated = await db["exam_attendance"].find_one_and_update(
        {"examId": exam_id, "studentId": student_id},
        {"$set": data, "$setOnInsert": {"id": _new_id("eatt"), "markedAt": _now_iso()}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return {"success": True, "data": serialize_doc(updated)}


@router.get("/invigilators")
async def list_invigilators(exam_id: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_invigilators")
            if exam_id:
                items = [item for item in items if str(item.get("examId")) == str(exam_id)]
            return {"success": True, "data": items}
        raise

    query = {"examId": exam_id} if exam_id else {}
    rows = []
    async for row in db["exam_invigilators"].find(query).sort("assignedAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.post("/invigilators")
async def assign_invigilator(payload: dict):
    exam_id = payload.get("examId")
    faculty_id = payload.get("facultyId")
    if not exam_id or not faculty_id:
        raise HTTPException(status_code=400, detail="examId and facultyId are required")

    data = {
        "id": payload.get("id") or _new_id("inv"),
        "examId": exam_id,
        "facultyId": faculty_id,
        "facultyName": payload.get("facultyName", ""),
        "assignedBy": payload.get("assignedBy", ""),
        "assignedAt": payload.get("assignedAt") or _now_iso(),
    }

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_invigilators")
            duplicate = next((item for item in items if str(item.get("examId")) == str(exam_id) and str(item.get("facultyId")) == str(faculty_id)), None)
            if duplicate:
                raise HTTPException(status_code=400, detail="Faculty already assigned to this exam")
            items.append(data)
            return {"success": True, "data": data}
        raise

    duplicate = await db["exam_invigilators"].find_one({"examId": exam_id, "facultyId": faculty_id})
    if duplicate:
        raise HTTPException(status_code=400, detail="Faculty already assigned to this exam")

    await db["exam_invigilators"].insert_one(data)
    return {"success": True, "data": data}


@router.delete("/invigilators/{assignment_id}")
async def remove_invigilator(assignment_id: str):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_invigilators")
            index = next((i for i, item in enumerate(items) if str(item.get("id")) == str(assignment_id)), None)
            if index is None:
                raise HTTPException(status_code=404, detail="Assignment not found")
            del items[index]
            return {"success": True, "message": "Invigilator removed"}
        raise

    result = await db["exam_invigilators"].delete_one(_id_query(assignment_id))
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"success": True, "message": "Invigilator removed"}


@router.get("/revaluations")
async def list_revaluations(student_id: Optional[str] = None, exam_id: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_revaluations")
            if student_id:
                items = [item for item in items if str(item.get("studentId")) == str(student_id)]
            if exam_id:
                items = [item for item in items if str(item.get("examId")) == str(exam_id)]
            return {"success": True, "data": items}
        raise

    query = {}
    if student_id:
        query["studentId"] = student_id
    if exam_id:
        query["examId"] = exam_id
    rows = []
    async for row in db["exam_revaluations"].find(query).sort("appliedAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.post("/revaluations")
async def create_revaluation(payload: dict):
    exam_id = payload.get("examId")
    student_id = payload.get("studentId")
    if not exam_id or not student_id:
        raise HTTPException(status_code=400, detail="examId and studentId are required")

    data = {
        "id": payload.get("id") or _new_id("reval"),
        "examId": exam_id,
        "studentId": student_id,
        "studentName": payload.get("studentName", ""),
        "reason": payload.get("reason", ""),
        "status": payload.get("status") or "Pending",
        "appliedAt": payload.get("appliedAt") or _now_iso(),
    }

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_revaluations")
            duplicate = next((item for item in items if str(item.get("examId")) == str(exam_id) and str(item.get("studentId")) == str(student_id)), None)
            if duplicate:
                raise HTTPException(status_code=400, detail="Already applied for revaluation")
            items.append(data)
            return {"success": True, "data": data}
        raise

    duplicate = await db["exam_revaluations"].find_one({"examId": exam_id, "studentId": student_id})
    if duplicate:
        raise HTTPException(status_code=400, detail="Already applied for revaluation")

    await db["exam_revaluations"].insert_one(data)
    return {"success": True, "data": data}


@router.get("/halls")
async def list_exam_halls():
    default_halls = [
        {"id": "hall_a", "name": "Hall A", "capacity": 100, "building": "Main Block"},
        {"id": "hall_b", "name": "Hall B", "capacity": 80, "building": "Main Block"},
        {"id": "lab_1", "name": "Lab 1", "capacity": 40, "building": "CS Block"},
        {"id": "lab_2", "name": "Lab 2", "capacity": 40, "building": "CS Block"},
        {"id": "room_101", "name": "Room 101", "capacity": 60, "building": "Admin Block"},
    ]
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            halls = _dev_list("exam_halls")
            if not halls:
                DEV_STORE["exam_halls"] = default_halls
                halls = DEV_STORE["exam_halls"]
            return {"success": True, "data": halls}
        raise

    rows = []
    async for row in db["exam_halls"].find().sort("name", 1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows if rows else default_halls}


@router.get("/seats")
async def list_seat_assignments(exam_id: Optional[str] = None, student_id: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_seat_assignments")
            if exam_id:
                items = [item for item in items if str(item.get("examId")) == str(exam_id)]
            if student_id:
                items = [item for item in items if str(item.get("studentId")) == str(student_id)]
            return {"success": True, "data": items}
        raise

    query = {}
    if exam_id:
        query["examId"] = exam_id
    if student_id:
        query["studentId"] = student_id
    rows = []
    async for row in db["exam_seat_assignments"].find(query).sort("updatedAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.put("/seats")
async def upsert_seat_assignment(payload: dict):
    exam_id = payload.get("examId")
    student_id = payload.get("studentId")
    if not exam_id or not student_id:
        raise HTTPException(status_code=400, detail="examId and studentId are required")

    data = {
        "examId": exam_id,
        "studentId": student_id,
        "seatNumber": payload.get("seatNumber", ""),
        "hallName": payload.get("hallName", ""),
        "updatedAt": _now_iso(),
    }

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_seat_assignments")
            existing = next((item for item in items if str(item.get("examId")) == str(exam_id) and str(item.get("studentId")) == str(student_id)), None)
            if existing:
                existing.update(data)
                existing["id"] = existing.get("id") or _new_id("seat")
                return {"success": True, "data": existing}
            created = {"id": _new_id("seat"), **data}
            items.append(created)
            return {"success": True, "data": created}
        raise

    updated = await db["exam_seat_assignments"].find_one_and_update(
        {"examId": exam_id, "studentId": student_id},
        {"$set": data, "$setOnInsert": {"id": _new_id("seat")}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return {"success": True, "data": serialize_doc(updated)}


@router.post("/seats/auto-assign")
async def auto_assign_seats(payload: dict):
    exam_id = payload.get("examId")
    hall_name = payload.get("hallName")
    if not exam_id or not hall_name:
        raise HTTPException(status_code=400, detail="examId and hallName are required")

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            regs = [item for item in _dev_list("exam_registrations") if str(item.get("examId")) == str(exam_id)]
            seats = _dev_list("exam_seat_assignments")
            assigned = 0
            seat_no = 1
            for reg in regs:
                existing = next((item for item in seats if str(item.get("examId")) == str(exam_id) and str(item.get("studentId")) == str(reg.get("studentId"))), None)
                if existing:
                    continue
                seats.append({
                    "id": _new_id("seat"),
                    "examId": exam_id,
                    "studentId": reg.get("studentId"),
                    "seatNumber": f"{hall_name[:1]}-{seat_no}",
                    "hallName": hall_name,
                    "updatedAt": _now_iso(),
                })
                assigned += 1
                seat_no += 1
            return {"success": True, "data": {"assigned": assigned}}
        raise

    regs = []
    async for row in db["exam_registrations"].find({"examId": exam_id}):
        regs.append(serialize_doc(row))

    assigned = 0
    seat_no = 1
    for reg in regs:
        student_id = reg.get("studentId")
        if not student_id:
            continue
        existing = await db["exam_seat_assignments"].find_one({"examId": exam_id, "studentId": student_id})
        if existing:
            continue
        await db["exam_seat_assignments"].insert_one({
            "id": _new_id("seat"),
            "examId": exam_id,
            "studentId": student_id,
            "seatNumber": f"{hall_name[:1]}-{seat_no}",
            "hallName": hall_name,
            "updatedAt": _now_iso(),
        })
        assigned += 1
        seat_no += 1

    return {"success": True, "data": {"assigned": assigned}}


@router.get("/sessions")
async def list_exam_sessions():
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {"success": True, "data": _dev_list("exam_sessions")}
        raise

    rows = []
    async for row in db["exam_sessions"].find().sort("createdAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.post("/sessions")
async def create_exam_session(payload: dict):
    data = {"id": payload.get("id") or _new_id("session"), "createdAt": _now_iso(), **payload}
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            _dev_list("exam_sessions").append(data)
            return {"success": True, "data": data}
        raise

    await db["exam_sessions"].insert_one(data)
    return {"success": True, "data": data}


@router.put("/sessions/{session_id}")
async def update_exam_session(session_id: str, payload: dict):
    patch = {**payload, "updatedAt": _now_iso()}
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            item = _dev_get("exam_sessions", session_id)
            if not item:
                raise HTTPException(status_code=404, detail="Session not found")
            item.update(patch)
            return {"success": True, "data": item}
        raise

    updated = await db["exam_sessions"].find_one_and_update(
        _id_query(session_id),
        {"$set": patch},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "data": serialize_doc(updated)}


@router.get("/timetable-drafts")
async def list_timetable_drafts():
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {"success": True, "data": _dev_list("exam_timetable_drafts")}
        raise

    rows = []
    async for row in db["exam_timetable_drafts"].find().sort("createdAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.post("/timetable-drafts")
async def create_timetable_draft(payload: dict):
    data = {
        "id": payload.get("id") or _new_id("tdraft"),
        "session": payload.get("session", ""),
        "semester": payload.get("semester", ""),
        "academicYear": payload.get("academicYear", ""),
        "exams": payload.get("exams") or [],
        "createdBy": payload.get("createdBy", ""),
        "status": payload.get("status") or "Draft",
        "createdAt": payload.get("createdAt") or _now_iso(),
    }
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            _dev_list("exam_timetable_drafts").append(data)
            return {"success": True, "data": data}
        raise

    await db["exam_timetable_drafts"].insert_one(data)
    return {"success": True, "data": data}


@router.patch("/timetable-drafts/{draft_id}/status")
async def update_timetable_draft_status(draft_id: str, payload: dict):
    patch = {
        "status": payload.get("status"),
        "reviewedBy": payload.get("reviewedBy"),
        "remarks": payload.get("remarks", ""),
        "reviewedAt": _now_iso(),
    }
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            item = _dev_get("exam_timetable_drafts", draft_id)
            if not item:
                raise HTTPException(status_code=404, detail="Draft not found")
            item.update(patch)
            return {"success": True, "data": item}
        raise

    updated = await db["exam_timetable_drafts"].find_one_and_update(
        _id_query(draft_id),
        {"$set": patch},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Draft not found")
    return {"success": True, "data": serialize_doc(updated)}


@router.get("/notifications")
async def list_exam_notifications(student_id: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_notifications")
            if student_id:
                items = [item for item in items if str(item.get("studentId")) == str(student_id)]
            items = sorted(items, key=lambda item: item.get("createdAt", ""), reverse=True)
            return {"success": True, "data": items}
        raise

    query = {"studentId": student_id} if student_id else {}
    rows = []
    async for row in db["exam_notifications"].find(query).sort("createdAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.post("/notifications")
async def create_exam_notification(payload: dict):
    data = {
        "id": payload.get("id") or _new_id("notif"),
        "studentId": payload.get("studentId"),
        "message": payload.get("message", ""),
        "type": payload.get("type") or "info",
        "read": False,
        "createdAt": payload.get("createdAt") or _now_iso(),
    }
    if not data["studentId"]:
        raise HTTPException(status_code=400, detail="studentId is required")

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            _dev_list("exam_notifications").append(data)
            return {"success": True, "data": data}
        raise

    await db["exam_notifications"].insert_one(data)
    return {"success": True, "data": data}


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_as_read(notification_id: str):
    patch = {"read": True, "updatedAt": _now_iso()}
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            item = _dev_get("exam_notifications", notification_id)
            if not item:
                raise HTTPException(status_code=404, detail="Notification not found")
            item.update(patch)
            return {"success": True, "data": item}
        raise

    updated = await db["exam_notifications"].find_one_and_update(
        _id_query(notification_id),
        {"$set": patch},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True, "data": serialize_doc(updated)}


@router.patch("/notifications/mark-all-read")
async def mark_all_notifications_as_read(payload: dict):
    student_id = payload.get("studentId")
    if not student_id:
        raise HTTPException(status_code=400, detail="studentId is required")

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            items = _dev_list("exam_notifications")
            for item in items:
                if str(item.get("studentId")) == str(student_id):
                    item["read"] = True
                    item["updatedAt"] = _now_iso()
            return {"success": True, "message": "Notifications marked as read"}
        raise

    await db["exam_notifications"].update_many(
        {"studentId": student_id},
        {"$set": {"read": True, "updatedAt": _now_iso()}},
    )
    return {"success": True, "message": "Notifications marked as read"}
