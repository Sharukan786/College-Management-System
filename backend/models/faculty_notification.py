from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FacultyWorkload(BaseModel):
    faculty_id: str = Field(alias="facultyId")
    semester: str
    academic_year: str
    
    # Teaching Load
    total_courses: int = 0
    total_credit_hours: int = 0
    total_student_count: int = 0
    lab_hours: int = 0
    
    # Research Load
    active_research_projects: int = 0
    research_hours: int = 0
    
    # Administrative Load
    committee_roles: int = 0
    mentoring_students: int = 0
    
    # Normalized Workload (0-100)
    workload_percentage: float = 0
    max_recommended_workload: int = 100
    
    # Status
    status: str = "Normal"  # Overloaded, Normal, Underloaded
    notes: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class WorkloadAlert(BaseModel):
    faculty_id: str = Field(alias="facultyId")
    semester: str
    academic_year: str
    alert_type: str  # Overload, Underload, Imbalance
    current_workload: float
    threshold: float
    message: str
    status: str = "Active"  # Active, Acknowledged, Resolved
    created_date: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class Notification(BaseModel):
    recipient_id: str  # faculty_id or admin_id
    recipient_type: str  # faculty, admin
    title: str
    message: str
    notification_type: str  # LeaveApproval, WorkloadAlert, Performance, Development, System
    reference_id: Optional[str] = None  # ID of related resource (leave_id, etc)
    is_read: bool = False
    created_date: datetime = Field(default_factory=datetime.utcnow)
    expires_date: Optional[datetime] = None
    action_url: Optional[str] = None
    
    class Config:
        populate_by_name = True
