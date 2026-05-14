from pydantic import BaseModel, Field


class AcademicResult(BaseModel):
    student_id: str = Field(alias="studentId")
    semester: int = Field(ge=1, le=10)
    subject_code: str = Field(alias="subjectCode")
    subject_name: str = Field(alias="subjectName")
    credits: int = Field(ge=0)
    grade: str
    status: str = "Pass"

