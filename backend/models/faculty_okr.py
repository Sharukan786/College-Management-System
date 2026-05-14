from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class KPICategory(str, Enum):
    TEACHING = "teaching"
    RESEARCH = "research"
    SERVICE = "service"
    MENTORING = "mentoring"
    INNOVATION = "innovation"
    COMMUNITY_ENGAGEMENT = "community_engagement"

class ObjectiveStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class KeyResult(BaseModel):
    kr_id: str = Field(default_factory=lambda: f"KR-{datetime.utcnow().timestamp()}")
    title: str
    description: Optional[str] = None
    target_value: float
    current_value: float = 0
    unit: str  # "number", "percentage", "hours", "count"
    progress_percentage: float = 0
    status: ObjectiveStatus = ObjectiveStatus.NOT_STARTED
    weighting: float = Field(..., ge=0, le=1)  # Weight in overall objective score
    start_date: datetime
    target_date: datetime
    milestone_dates: List[datetime] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Objective(BaseModel):
    objective_id: str = Field(default_factory=lambda: f"OB-{datetime.utcnow().timestamp()}")
    title: str
    description: str
    category: KPICategory
    key_results: List[KeyResult]
    status: ObjectiveStatus = ObjectiveStatus.NOT_STARTED
    owner_id: str  # Faculty ID
    aligned_with: Optional[str] = None  # Department or institution goal
    overall_score: float = 0  # Weighted average of key results
    priority: int = Field(..., ge=1, le=5)
    start_date: datetime
    end_date: datetime
    review_frequency: str = "monthly"  # monthly, quarterly, semi-annual
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class OKRCycle(BaseModel):
    cycle_id: str = Field(default_factory=lambda: f"OKRC-{datetime.utcnow().timestamp()}")
    cycle_name: str  # "Q1 2024", "FY 2024-2025"
    department_id: Optional[str] = None
    faculty_id: Optional[str] = None
    start_date: datetime
    end_date: datetime
    objectives: List[Objective]
    cycle_status: str = "planning"  # planning, active, review, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class KPITemplate(BaseModel):
    template_id: str = Field(default_factory=lambda: f"KPIT-{datetime.utcnow().timestamp()}")
    name: str
    category: KPICategory
    description: str
    default_target: float
    unit: str
    benchmark_low: float
    benchmark_medium: float
    benchmark_high: float
    frequency: str  # How often to measure
    department_id: Optional[str] = None  # If null, applies organization-wide
    is_mandatory: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class KPIReview(BaseModel):
    review_id: str = Field(default_factory=lambda: f"KPIR-{datetime.utcnow().timestamp()}")
    objective_id: str
    faculty_id: str
    review_period: str  # "monthly", "quarterly"
    review_date: datetime
    key_results_progress: dict  # kr_id -> current_value
    overall_status: ObjectiveStatus
    progress_summary: str
    achievements: List[str] = []
    challenges: List[str] = []
    next_steps: List[str] = []
    reviewer_id: Optional[str] = None
    reviewer_comments: Optional[str] = None
    approval_status: str = "pending"  # pending, approved, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class DepartmentKPIMetrics(BaseModel):
    metrics_id: str = Field(default_factory=lambda: f"DKPI-{datetime.utcnow().timestamp()}")
    department_id: str
    cycle_id: str
    total_objectives: int = 0
    completed_objectives: int = 0
    on_track_objectives: int = 0
    at_risk_objectives: int = 0
    department_avg_score: float = 0
    category_performance: dict = {}  # category -> avg_score
    top_performer_ids: List[str] = []
    underperforming_ids: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class PerformanceRating(BaseModel):
    rating_id: str = Field(default_factory=lambda: f"PR-{datetime.utcnow().timestamp()}")
    faculty_id: str
    cycle_id: str
    okr_score: float = Field(..., ge=0, le=5)  # Based on OKR completion
    competency_score: float = Field(..., ge=0, le=5)  # Behavioral competencies
    overall_rating: float = Field(..., ge=0, le=5)
    rating_level: str  # "exceptional", "exceeds", "meets", "developing", "needs_improvement"
    feedback: str
    development_areas: List[str] = []
    promotion_eligible: bool = False
    promotion_recommendation: Optional[str] = None
    rater_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
