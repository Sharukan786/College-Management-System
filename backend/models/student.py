from typing import Optional
from datetime import date

from pydantic import BaseModel, Field


class Student(BaseModel):
    roll_number: str = Field(alias="rollNumber")
    department_id: str = Field(alias="departmentId")
    year: int = Field(ge=1, le=5)
    semester: int = Field(ge=1, le=10)
    status: str = "active"
    name: str = ""
    email: str = ""
    phone: str = ""
    gender: str = ""
    dob: Optional[date] = None
    address: str = ""
    avatar: str = ""
    section: str = ""
    cgpa: float = 0
    attendance_pct: float = Field(default=0, alias="attendancePct")
    fee_status: str = Field(default="pending", alias="feeStatus")
    guardian: str = ""
    guardian_phone: str = Field(default="", alias="guardianPhone")
    enroll_date: Optional[date] = Field(default=None, alias="enrollDate")
