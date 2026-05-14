from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from typing import Optional
from fastapi import APIRouter, HTTPException
from pymongo import ReturnDocument

from backend.db import get_db
from backend.dev_store import create_attendance as create_dev_attendance
from backend.dev_store import create_od_request as create_dev_od_request
from backend.dev_store import list_attendance as list_dev_attendance
from backend.dev_store import list_attendance_markings as list_dev_attendance_markings
from backend.dev_store import list_od_requests as list_dev_od_requests
from backend.dev_store import list_weekly_attendance
from backend.dev_store import delete_od_request as delete_dev_od_request
from backend.dev_store import update_od_request as update_dev_od_request
from backend.dev_store import update_od_request_status as update_dev_od_request_status
from backend.dev_store import upsert_attendance_marking as upsert_dev_attendance_marking
from backend.schemas.academics import AttendanceRecord, WeeklyAttendancePoint
from backend.schemas.academics import AttendanceMarkRecord, OdRequestPayload, OdRequestStatusUpdate
from backend.utils.mongo import serialize_doc

router = APIRouter(prefix="/api/academics/attendance", tags=["academics:attendance"])


@router.get("")
async def list_attendance(role: Optional[str] = None, person_id: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {"success": True, "data": list_dev_attendance(role, person_id)}
        raise
    query = {}
    if role:
        query["role"] = role
    if person_id:
        query["personId"] = person_id

    records = []
    async for record in db["academic_attendance"].find(query).sort("name", 1):
        records.append(serialize_doc(record))
    return {"success": True, "data": records}


@router.post("")
async def create_attendance(payload: AttendanceRecord):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {"success": True, "data": create_dev_attendance(payload.model_dump())}
        raise
    result = await db["academic_attendance"].insert_one(payload.model_dump())
    created = await db["academic_attendance"].find_one({"_id": result.inserted_id})
    return {"success": True, "data": serialize_doc(created)}


@router.get("/weekly")
async def get_weekly_attendance(role: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {"success": True, "data": list_weekly_attendance()}
        raise
    query = {"role": role} if role else {}
    points = []
    async for point in db["academic_attendance_weekly"].find(query).sort("day", 1):
        points.append(serialize_doc(point))

    if points:
        return {"success": True, "data": points}

    default_points = [
        WeeklyAttendancePoint(day="Mon", attendance=92).model_dump(),
        WeeklyAttendancePoint(day="Tue", attendance=88).model_dump(),
        WeeklyAttendancePoint(day="Wed", attendance=90).model_dump(),
        WeeklyAttendancePoint(day="Thu", attendance=86).model_dump(),
        WeeklyAttendancePoint(day="Fri", attendance=94).model_dump(),
    ]
    return {"success": True, "data": default_points}


@router.get("/markings")
async def list_attendance_markings(
    class_id: Optional[str] = None,
    date: Optional[str] = None,
    hour: Optional[str] = None,
    student_id: Optional[str] = None,
):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {
                "success": True,
                "data": list_dev_attendance_markings(class_id, date, hour, student_id),
            }
        raise

    query = {}
    if class_id:
        query["classId"] = class_id
    if date:
        query["date"] = date
    if hour:
        query["hour"] = hour
    if student_id:
        query["entries.studentId"] = student_id

    rows = []
    async for row in db["academic_attendance_markings"].find(query).sort("date", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.put("/markings")
async def upsert_attendance_marking(payload: AttendanceMarkRecord):
    data = payload.model_dump()
    query = {
        "classId": data["classId"],
        "date": data["date"],
        "hour": data["hour"],
    }

    if not data.get("markedAt"):
        data["markedAt"] = datetime.utcnow().isoformat()

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {"success": True, "data": upsert_dev_attendance_marking(data)}
        raise

    updated = await db["academic_attendance_markings"].find_one_and_update(
        query,
        {"$set": data},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return {"success": True, "data": serialize_doc(updated)}


@router.get("/od-requests")
async def list_od_requests(student_id: Optional[str] = None, status: Optional[str] = None):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {"success": True, "data": list_dev_od_requests(student_id, status)}
        raise

    query = {}
    if student_id:
        query["studentId"] = student_id
    if status and status != "All":
        query["status"] = status

    rows = []
    async for row in db["academic_od_requests"].find(query).sort("createdAt", -1):
        rows.append(serialize_doc(row))
    return {"success": True, "data": rows}


@router.post("/od-requests")
async def create_od_request(payload: OdRequestPayload):
    data = payload.model_dump()
    request_id = data.get("requestId") or f"od-{uuid4().hex[:12]}"
    data["requestId"] = request_id
    if not data.get("createdAt"):
        data["createdAt"] = datetime.utcnow().isoformat()

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            return {"success": True, "data": create_dev_od_request(data)}
        raise

    result = await db["academic_od_requests"].insert_one(data)
    created = await db["academic_od_requests"].find_one({"_id": result.inserted_id})
    return {"success": True, "data": serialize_doc(created)}


@router.put("/od-requests/{request_id}")
async def update_od_request(request_id: str, payload: OdRequestPayload):
    data = payload.model_dump()
    data["requestId"] = request_id
    data["updatedAt"] = datetime.utcnow().isoformat()

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            updated = update_dev_od_request(request_id, data)
            if not updated:
                raise HTTPException(status_code=404, detail="OD request not found")
            return {"success": True, "data": updated}
        raise

    updated = await db["academic_od_requests"].find_one_and_update(
        {"requestId": request_id},
        {"$set": data},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="OD request not found")
    return {"success": True, "data": serialize_doc(updated)}


@router.patch("/od-requests/{request_id}/status")
async def update_od_request_status(request_id: str, payload: OdRequestStatusUpdate):
    status = payload.status
    if status not in {"Pending", "Approved", "Rejected"}:
        raise HTTPException(status_code=400, detail="Invalid OD status")

    patch = {
        "status": status,
        "reviewedBy": payload.reviewedBy,
        "reviewedAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
    }

    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            updated = update_dev_od_request_status(request_id, status, payload.reviewedBy)
            if not updated:
                raise HTTPException(status_code=404, detail="OD request not found")
            return {"success": True, "data": updated}
        raise

    updated = await db["academic_od_requests"].find_one_and_update(
        {"requestId": request_id},
        {"$set": patch},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="OD request not found")
    return {"success": True, "data": serialize_doc(updated)}


@router.delete("/od-requests/{request_id}")
async def delete_od_request(request_id: str):
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            deleted = delete_dev_od_request(request_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="OD request not found")
            return {"success": True, "message": "OD request deleted"}
        raise

    result = await db["academic_od_requests"].delete_one({"requestId": request_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="OD request not found")
    return {"success": True, "message": "OD request deleted"}
