from datetime import date

from pydantic import BaseModel, Field


class Attendance(BaseModel):
    student_id: str = Field(alias="studentId")
    date: date
    status: str = "present"
    subject: str = ""
