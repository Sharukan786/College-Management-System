from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class SkillCategory(str, Enum):
    TECHNICAL = "technical"
    PEDAGOGICAL = "pedagogical"
    RESEARCH = "research"
    ADMINISTRATIVE = "administrative"
    SOFT_SKILLS = "soft_skills"
    DIGITAL = "digital"

class Skill(BaseModel):
    skill_id: str
    name: str
    category: SkillCategory
    description: Optional[str] = None
    is_critical: bool = False  # Critical skills for department/role
    certification_available: bool = False

class FacultySkill(BaseModel):
    skill_id: str
    skill_name: str
    category: SkillCategory
    current_level: SkillLevel
    proficiency_score: float = Field(..., ge=0, le=100)
    years_of_experience: Optional[int] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    certification: Optional[str] = None
    certification_date: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class SkillMatrix(BaseModel):
    matrix_id: str = Field(default_factory=lambda: f"SM-{datetime.utcnow().timestamp()}")
    faculty_id: str
    department_id: str
    skills: List[FacultySkill]
    total_skills: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class SkillGap(BaseModel):
    skill_id: str
    skill_name: str
    category: SkillCategory
    current_level: SkillLevel
    required_level: SkillLevel
    gap_severity: str  # "critical", "high", "medium", "low"
    priority: int = Field(..., ge=1, le=5)
    recommended_training: List[str] = []

class SkillGapAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: f"SGA-{datetime.utcnow().timestamp()}")
    faculty_id: str
    department_id: str
    role: str
    academic_year: str
    skill_gaps: List[SkillGap]
    critical_gaps: int = 0
    gap_coverage_score: float = Field(..., ge=0, le=100)  # % of required skills
    recommended_training_plan: List[str] = []
    estimated_training_hours: int = 0
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    next_review_date: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class DepartmentSkillMap(BaseModel):
    """Mapping of required vs available skills at department level"""
    map_id: str = Field(default_factory=lambda: f"DSM-{datetime.utcnow().timestamp()}")
    department_id: str
    required_skills: List[Skill]
    skill_coverage: dict = {}  # skill_id -> % of faculty with that skill
    critical_shortages: List[str] = []  # List of critical skill IDs with low coverage
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class TrainingRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"TR-{datetime.utcnow().timestamp()}")
    faculty_id: str
    skill_gap_id: str
    skill_name: str
    training_type: str  # online_course, workshop, certification, mentoring
    provider: str
    duration_hours: int
    cost: Optional[float] = None
    priority: int = Field(..., ge=1, le=5)
    deadline: Optional[datetime] = None
    status: str = "pending"  # pending, approved, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
