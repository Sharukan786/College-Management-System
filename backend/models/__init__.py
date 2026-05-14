"""Pydantic model schemas used by the FastAPI backend."""

from .academic_result import AcademicResult
from .attendance import Attendance
from .department import Department
from .document import Document
from .faculty import Faculty
from .fee import Fee
from .report import Report
from .student import Student
from .system_setting import SystemSetting

__all__ = [
    "AcademicResult",
    "Attendance",
    "Department",
    "Document",
    "Faculty",
    "Fee",
    "Report",
    "Student",
    "SystemSetting",
]
