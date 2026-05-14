from fastapi import APIRouter
from datetime import datetime

from backend.db import get_db
from backend.schemas.fees_schema import AssignFee
from backend.utils.fee_calculator import calculate_fee

router = APIRouter(prefix="/fees", tags=["Fees"])


@router.post("/assign")
async def assign_fee(data: AssignFee):

    db = get_db()

    fees_collection = db["fees_structure"]

    fee = calculate_fee(
        data.first_graduate,
        data.hostel_required
    )

    record = {
        "student_id": data.student_id,
        "student_name": data.student_name,
        "course": data.course,
        "semester": data.semester,
        "first_graduate": data.first_graduate,
        "hostel_required": data.hostel_required,
        "fee_breakdown": fee,
        "total_fee": fee["total"],
        "assigned_date": datetime.now(),
        "payment_status": "Pending"
    }

    result = await fees_collection.insert_one(record)

    return {
        "message": "Fee assigned successfully",
        "collection": "fees_structure",
        "id": str(result.inserted_id),
        "total": fee["total"]
    }