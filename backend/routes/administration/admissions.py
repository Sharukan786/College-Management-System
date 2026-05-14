from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from backend.db import get_db
from backend.schemas.admission_schema import AdmissionCreate

router = APIRouter(prefix="/admissions", tags=["Admissions"])


def _admissions_collection():
    return get_db()["admissions"]


def _to_float(value: Any, fallback: float = 0.0) -> float:
    if value is None:
        return fallback
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("%", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return fallback
    return fallback


def _to_int(value: Any, fallback: int = 0) -> int:
    if value is None:
        return fallback
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        cleaned = value.strip()
        try:
            return int(cleaned)
        except ValueError:
            return fallback
    return fallback


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_ymd() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _build_lookup_query(admission_id: str) -> dict[str, Any]:
    lookup: list[dict[str, Any]] = [
        {"id": admission_id},
        {"admission_id": admission_id},
    ]
    if ObjectId.is_valid(admission_id):
        lookup.append({"_id": ObjectId(admission_id)})
    return {"$or": lookup}


def _serialize_admission(item: dict[str, Any]) -> dict[str, Any]:
    serialized = dict(item)
    serialized["_id"] = str(serialized["_id"])

    if not serialized.get("id"):
        serialized["id"] = serialized.get("admission_id") or serialized["_id"]
    if not serialized.get("admission_id"):
        serialized["admission_id"] = serialized["id"]

    payment_status = (
        serialized.get("paymentStatus")
        or serialized.get("payment_status")
        or (serialized.get("payment") or {}).get("status")
        or "Pending"
    )
    serialized["payment_status"] = payment_status
    serialized["paymentStatus"] = payment_status

    if not serialized.get("name") and serialized.get("fullName"):
        serialized["name"] = serialized["fullName"]
    if not serialized.get("fullName") and serialized.get("name"):
        serialized["fullName"] = serialized["name"]

    return serialized


def _normalize_from_flat_payload(payload: dict[str, Any]) -> dict[str, Any]:
    generated_id = f"STU-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
    admission_id = payload.get("id") or payload.get("admission_id") or generated_id

    name = (payload.get("name") or payload.get("fullName") or "").strip()
    email = (payload.get("email") or "").strip()
    phone = (payload.get("phone") or "").strip()

    payment_status = payload.get("paymentStatus") or payload.get("payment_status") or "Pending"

    normalized = {
        "id": admission_id,
        "admission_id": admission_id,
        "role": "student",
        "type": "student",
        "status": payload.get("status") or "Pending",
        "createdDate": payload.get("createdDate") or _today_ymd(),
        "created_at": _utc_now_iso(),
        "name": name,
        "fullName": payload.get("fullName") or name,
        "email": email,
        "phone": phone,
        "dateOfBirth": payload.get("dateOfBirth") or payload.get("dob") or "",
        "gender": payload.get("gender") or "",
        "previousSchool": payload.get("previousSchool") or "",
        "board": payload.get("board") or "",
        "yearOfPassing": _to_int(payload.get("yearOfPassing")),
        "marksPercentage": _to_float(payload.get("marksPercentage")),
        "courseCategory": payload.get("courseCategory") or "",
        "course": payload.get("course") or "",
        "quota": payload.get("quota") or "",
        "accommodation": payload.get("accommodation") or "",
        "roomType": payload.get("roomType") or "",
        "documents": {
            "passport_photo": payload.get("passportPhoto"),
            "aadhaar_card": payload.get("aadhaarCard"),
            "marksheet": payload.get("marksheet"),
            "transfer_certificate": payload.get("transferCertificate"),
        },
        "payment": {
            "application_fee": _to_float(payload.get("applicationFee"), 500.0),
            "payment_method": payload.get("paymentMethod"),
            "transaction_id": payload.get("transactionId"),
            "payment_datetime": payload.get("paymentDateTime"),
            "status": payment_status,
        },
        "payment_status": payment_status,
        "paymentStatus": payment_status,
    }

    # Keep nested structure for backwards compatibility with any existing API consumers.
    normalized["personal"] = {
        "full_name": normalized["fullName"],
        "gender": normalized["gender"],
        "dob": normalized["dateOfBirth"],
        "email": normalized["email"],
        "phone": normalized["phone"],
        "student_id": normalized["id"],
        "address": payload.get("address") or "",
        "city": payload.get("city") or "",
        "state": payload.get("state") or "",
        "pincode": payload.get("pincode") or "",
    }
    normalized["academic"] = {
        "previous_school": normalized["previousSchool"],
        "board": normalized["board"],
        "year_of_passing": normalized["yearOfPassing"],
        "marks_percentage": normalized["marksPercentage"],
    }
    normalized["course_info"] = {
        "category": normalized["courseCategory"],
        "course": normalized["course"],
    }

    return normalized


def _normalize_from_nested_payload(payload: dict[str, Any]) -> dict[str, Any]:
    validated = AdmissionCreate.model_validate(payload)
    admission = validated.model_dump()

    personal = admission.get("personal") or {}
    academic = admission.get("academic") or {}
    course = admission.get("course") or {}
    payment = admission.get("payment") or {}

    admission_id = personal.get("student_id") or f"STU-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
    payment_status = admission.get("payment_status") or payment.get("status") or "Pending"

    admission.update(
        {
            "id": admission_id,
            "admission_id": admission_id,
            "type": "student" if admission.get("role") == "student" else admission.get("role"),
            "status": admission.get("status") or "Pending",
            "createdDate": _today_ymd(),
            "created_at": _utc_now_iso(),
            "name": personal.get("full_name") or "",
            "fullName": personal.get("full_name") or "",
            "email": personal.get("email") or "",
            "phone": personal.get("phone") or "",
            "dateOfBirth": personal.get("dob") or "",
            "gender": personal.get("gender") or "",
            "previousSchool": academic.get("previous_school") or "",
            "board": academic.get("board") or "",
            "yearOfPassing": academic.get("year_of_passing") or 0,
            "marksPercentage": academic.get("marks_percentage") or 0,
            "courseCategory": course.get("category") or "",
            "payment_status": payment_status,
            "paymentStatus": payment_status,
            "course_info": {
                "category": course.get("category") or "",
                "course": course.get("course") or "",
            },
        }
    )

    return admission


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if "personal" in payload and "academic" in payload and "course" in payload:
        return _normalize_from_nested_payload(payload)

    if payload.get("name") or payload.get("fullName"):
        return _normalize_from_flat_payload(payload)

    raise HTTPException(
        status_code=422,
        detail="Unsupported admission payload. Provide nested admission payload or student add form payload.",
    )


@router.post("/create")
async def create_admission(payload: dict[str, Any]):
    try:
        admissions_collection = _admissions_collection()
        admission = _normalize_payload(payload)

        result = await admissions_collection.insert_one(admission)

        return {
            "message": "Admission created successfully",
            "mongo_id": str(result.inserted_id),
            "id": admission.get("id"),
            "admission_id": admission.get("admission_id"),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating admission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating admission: {str(e)}")


@router.get("/")
async def get_all_admissions():
    admissions_collection = _admissions_collection()
    data: list[dict[str, Any]] = []

    async for item in admissions_collection.find().sort("created_at", -1):
        data.append(_serialize_admission(item))

    return data


@router.get("/students")
async def get_student_admissions():
    admissions_collection = _admissions_collection()
    data: list[dict[str, Any]] = []

    query = {"$or": [{"role": "student"}, {"type": "student"}]}
    async for item in admissions_collection.find(query).sort("created_at", -1):
        data.append(_serialize_admission(item))

    return data


@router.get("/students/approved-for-fees")
async def get_approved_students_for_fees():
    """Get only APPROVED students with valid ID fields - ready for fee assignment.
    STRICT validation: Only returns students that can be found with exact ID match."""
    admissions_collection = _admissions_collection()
    data: list[dict[str, Any]] = []

    # Query: only approved students
    query = {
        "$and": [
            {"$or": [{"role": "student"}, {"type": "student"}]},
            {"status": "Approved"}
        ]
    }
    
    async for item in admissions_collection.find(query).sort("created_at", -1):
        serialized = _serialize_admission(item)
        student_id = serialized.get("id")
        
        # STRICT VALIDATION: Verify using EXACT field match (not $or queries)
        # This prevents false positives from corrupted records
        if student_id:
            # Try exact match on 'id' field first (most reliable)
            exact_match = await admissions_collection.find_one({"id": student_id})
            
            if exact_match:
                # Double-check this is the same student (compare MongoDB IDs)
                if str(exact_match.get("_id")) == str(item.get("_id")):
                    data.append(serialized)

    return {"approved_students": data, "count": len(data)}


@router.delete("/purge-invalid-approved")
async def purge_invalid_approved():
    """Admin endpoint: Remove approved students with invalid/non-existent IDs."""
    admissions_collection = _admissions_collection()
    removed_count = 0
    to_delete = []

    # Find all approved students
    query = {
        "$and": [
            {"$or": [{"role": "student"}, {"type": "student"}]},
            {"status": "Approved"}
        ]
    }
    
    async for item in admissions_collection.find(query):
        student_id = item.get("id") or item.get("admission_id")
        
        if not student_id:
            # No ID field at all - mark for deletion
            to_delete.append(item.get("_id"))
        else:
            # ID exists, verify it can be found
            exact_match = await admissions_collection.find_one({"id": student_id})
            
            # If ID doesn't match exactly, it's corrupted - delete
            if not exact_match or str(exact_match.get("_id")) != str(item.get("_id")):
                to_delete.append(item.get("_id"))

    # Delete invalid records
    if to_delete:
        result = await admissions_collection.delete_many({"_id": {"$in": to_delete}})
        removed_count = result.deleted_count
        print(f"[PURGE] Removed {removed_count} invalid approved students")

    return {
        "message": f"Purged {removed_count} invalid records",
        "removed_count": removed_count
    }


@router.put("/approve/{admission_id}")
async def approve_admission(admission_id: str):
    admissions_collection = _admissions_collection()
    
    # First, fetch the admission to check if it has an ID
    admission = await admissions_collection.find_one(_build_lookup_query(admission_id))
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    
    # Ensure the admission has an ID field (for fee assignment lookup)
    update_data = {
        "status": "Approved",
        "updated_at": _utc_now_iso()
    }
    
    # If no ID field exists, generate one
    if not admission.get("id") and not admission.get("admission_id"):
        new_id = f"STU-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        update_data["id"] = new_id
        update_data["admission_id"] = new_id
    
    result = await admissions_collection.update_one(
        _build_lookup_query(admission_id),
        {"$set": update_data},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Admission not found")

    return {"message": "Admission approved successfully", "id": admission_id}


@router.put("/reject/{admission_id}")
async def reject_admission(admission_id: str):
    admissions_collection = _admissions_collection()
    result = await admissions_collection.update_one(
        _build_lookup_query(admission_id),
        {"$set": {"status": "Rejected", "updated_at": _utc_now_iso()}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Admission not found")

    return {"message": "Admission rejected successfully", "id": admission_id}


@router.delete("/{admission_id}")
async def delete_admission(admission_id: str):
    admissions_collection = _admissions_collection()
    result = await admissions_collection.delete_one(_build_lookup_query(admission_id))

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Admission not found")

    return {"message": "Admission deleted successfully", "id": admission_id}


# -----------------
# Faculty Admissions Routes
# -----------------

def _faculty_admissions_collection():
    return get_db()["faculty_admissions"]


async def _get_faculty_collection():
    db = get_db()
    return db["faculty"]


def _serialize_faculty_admission(item: dict[str, Any]) -> dict[str, Any]:
    """Serialize faculty admission document"""
    serialized = dict(item)
    serialized["_id"] = str(serialized["_id"])
    
    if not serialized.get("id"):
        serialized["id"] = serialized.get("admission_id") or serialized["_id"]
    if not serialized.get("admission_id"):
        serialized["admission_id"] = serialized["id"]
    
    return serialized


def _build_faculty_lookup_query(faculty_admission_id: str) -> dict[str, Any]:
    """Build query for finding faculty admission by multiple fields"""
    lookup: list[dict[str, Any]] = [
        {"id": faculty_admission_id},
        {"admission_id": faculty_admission_id},
    ]
    if ObjectId.is_valid(faculty_admission_id):
        lookup.append({"_id": ObjectId(faculty_admission_id)})
    return {"$or": lookup}


@router.get("/faculty")
async def get_faculty_admissions():
    """Get all faculty admissions"""
    faculty_admissions_collection = _faculty_admissions_collection()
    data: list[dict[str, Any]] = []
    
    async for item in faculty_admissions_collection.find().sort("created_at", -1):
        data.append(_serialize_faculty_admission(item))
    
    return data


@router.get("/faculty/{faculty_admission_id}")
async def get_faculty_admission(faculty_admission_id: str):
    """Get specific faculty admission by ID"""
    faculty_admissions_collection = _faculty_admissions_collection()
    
    # Try to find by multiple ID formats
    doc = None
    try:
        obj_id = ObjectId(faculty_admission_id)
        doc = await faculty_admissions_collection.find_one({"_id": obj_id})
    except:
        pass
    
    if not doc:
        doc = await faculty_admissions_collection.find_one(
            {"$or": [{"id": faculty_admission_id}, {"admission_id": faculty_admission_id}]}
        )
    
    if not doc:
        raise HTTPException(status_code=404, detail="Faculty admission not found")
    
    return _serialize_faculty_admission(doc)


@router.put("/faculty/approve/{faculty_admission_id}")
async def approve_faculty_admission(faculty_admission_id: str):
    """Approve faculty admission"""
    faculty_admissions_collection = _faculty_admissions_collection()
    
    result = await faculty_admissions_collection.update_one(
        _build_faculty_lookup_query(faculty_admission_id),
        {"$set": {"status": "Approved", "updated_at": _utc_now_iso()}},
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Faculty admission not found")
    
    return {"message": "Faculty admission approved successfully", "id": faculty_admission_id}


@router.put("/faculty/reject/{faculty_admission_id}")
async def reject_faculty_admission(faculty_admission_id: str):
    """Reject faculty admission"""
    faculty_admissions_collection = _faculty_admissions_collection()
    
    result = await faculty_admissions_collection.update_one(
        _build_faculty_lookup_query(faculty_admission_id),
        {"$set": {"status": "Rejected", "updated_at": _utc_now_iso()}},
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Faculty admission not found")
    
    return {"message": "Faculty admission rejected successfully", "id": faculty_admission_id}


@router.delete("/faculty/{faculty_admission_id}")
async def delete_faculty_admission(faculty_admission_id: str):
    """Delete faculty admission"""
    faculty_admissions_collection = _faculty_admissions_collection()
    
    result = await faculty_admissions_collection.delete_one(
        _build_faculty_lookup_query(faculty_admission_id)
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Faculty admission not found")
    
    return {"message": "Faculty admission deleted successfully", "id": faculty_admission_id}