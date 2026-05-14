from copy import deepcopy

from fastapi import APIRouter, HTTPException

from backend.db import get_db
from backend.dev_store import DEV_STORE
from backend.utils.mongo import serialize_doc

router = APIRouter(prefix="/api/staff", tags=["staff"])


def _seed_dev_staff() -> None:
    if DEV_STORE.get("staff"):
        return

    DEV_STORE["staff"] = [
        {
            "staffId": "FAC-204",
            "staffName": "Dr. Rajesh Iyer",
            "designation": "Professor",
            "department": "Computer Science",
            "category": "Teaching",
            "basicSalary": 75000,
            "hra": 15000,
            "allowance": 5000,
            "pf": 3000,
            "tax": 3500,
        },
        {
            "staffId": "FAC-201",
            "staffName": "Dr. Ravi Kumar",
            "designation": "Associate Professor",
            "department": "Computer Science",
            "category": "Teaching",
            "basicSalary": 68000,
            "hra": 12000,
            "allowance": 4500,
            "pf": 2800,
            "tax": 3000,
        },
        {
            "staffId": "ADM-105",
            "staffName": "Meena S",
            "designation": "Accountant",
            "department": "Administration",
            "category": "Non-Teaching",
            "basicSalary": 42000,
            "hra": 9000,
            "allowance": 3000,
            "pf": 2000,
            "tax": 1500,
        },
    ]


@router.get("")
async def get_all_staff():
    try:
        db = get_db()
    except HTTPException as error:
        if error.status_code == 503:
            _seed_dev_staff()
            return deepcopy(DEV_STORE["staff"])
        raise

    staff = []
    async for member in db["staff_Details"].find():
        staff.append(serialize_doc(member))
    return staff
