from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MentorshipGoal(str, Enum):
    RESEARCH = "research"
    TEACHING = "teaching"
    CAREER_DEVELOPMENT = "career_development"
    WORK_LIFE_BALANCE = "work_life_balance"
    PUBLICATION = "publication"
    MENTORING_SKILLS = "mentoring_skills"
    LEADERSHIP = "leadership"

class MentorshipStatus(str, Enum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    TERMINATED = "terminated"

class MentorProfile(BaseModel):
    faculty_id: str
    expertise_areas: List[str]
    mentoring_experience_years: int = 0
    max_mentees: int = 3
    availability_hours_per_month: int = 10
    mentoring_style: Optional[str] = None
    languages: List[str] = ["English"]
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class MenteeProfile(BaseModel):
    faculty_id: str
    career_stage: str  # "junior", "mid-career", "senior"
    mentorship_goals: List[MentorshipGoal]
    preferred_mentor_expertise: List[str]
    challenges: Optional[List[str]] = None
    commitment_hours_per_month: int = 5
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class MentorshipMatch(BaseModel):
    match_id: str = Field(default_factory=lambda: f"MM-{datetime.utcnow().timestamp()}")
    mentor_id: str
    mentor_name: str
    mentee_id: str
    mentee_name: str
    department_id: str
    match_score: float = Field(..., ge=0, le=100)
    compatibility_factors: dict  # expertise match, availability, goals alignment
    mentorship_goals: List[MentorshipGoal]
    status: MentorshipStatus = MentorshipStatus.PROPOSED
    duration_months: int = 6
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    meeting_frequency: str = "bi-weekly"  # weekly, bi-weekly, monthly
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class MentorshipSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"MS-{datetime.utcnow().timestamp()}")
    match_id: str
    mentor_id: str
    mentee_id: str
    session_date: datetime
    duration_minutes: int
    topics_discussed: List[str]
    session_notes: str
    action_items: List[str] = []
    mentee_feedback: Optional[str] = None
    mentor_observations: Optional[str] = None
    recorded: bool = False
    session_status: str = "scheduled"  # scheduled, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class MentorshipProgress(BaseModel):
    progress_id: str = Field(default_factory=lambda: f"MP-{datetime.utcnow().timestamp()}")
    match_id: str
    mentor_id: str
    mentee_id: str
    reporting_period: str  # "monthly", "quarterly"
    goals_achieved: List[str] = []
    goals_in_progress: List[str] = []
    challenges_faced: List[str] = []
    next_steps: List[str] = []
    mentee_satisfaction_score: Optional[float] = None  # 1-5
    mentor_satisfaction_score: Optional[float] = None  # 1-5
    overall_progress_percentage: float = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class MentorshipMatchingAlgorithm(BaseModel):
    """Configuration for matching algorithm"""
    expertise_weight: float = 0.4
    availability_weight: float = 0.2
    goals_alignment_weight: float = 0.2
    department_diversity_weight: float = 0.15
    personality_compatibility_weight: float = 0.05
    min_match_score: float = 70.0  # Minimum score to consider as match
