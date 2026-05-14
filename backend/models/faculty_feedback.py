from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class FeedbackSourceType(str, Enum):
    PEER = "peer"
    SUPERVISOR = "supervisor"
    SUBORDINATE = "subordinate"
    SELF = "self"
    STUDENT = "student"

class FeedbackCategory(str, Enum):
    TEACHING = "teaching"
    RESEARCH = "research"
    ADMINISTRATION = "administration"
    COMMUNICATION = "communication"
    COLLABORATION = "collaboration"

class PeerReview(BaseModel):
    reviewer_id: str = Field(alias="reviewerId")
    reviewee_id: str = Field(alias="revieweeId")
    rating: float = 0.0  # e.g., out of 5.0
    feedback: str
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    status: str = "Submitted"  # Draft, Submitted
    review_date: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class FeedbackRound(BaseModel):
    faculty_id: str = Field(alias="facultyId")
    academic_year: str
    start_date: datetime
    end_date: datetime
    evaluators: List[str] = []
    status: str = "Active"  # Active, Closed, Draft
    description: Optional[str] = None
    feedback_categories: List[str] = []
    
    class Config:
        populate_by_name = True

class Faculty360Feedback(BaseModel):
    faculty_id: str = Field(alias="facultyId")
    round_id: str = Field(alias="roundId")
    source_type: FeedbackSourceType
    source_id: str = Field(alias="sourceId")
    category: FeedbackCategory
    rating: float  # 1-5
    comments: str
    strengths: Optional[List[str]] = None
    improvements: Optional[List[str]] = None
    submitted_date: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class FeedbackSummary(BaseModel):
    faculty_id: str = Field(alias="facultyId")
    round_id: str = Field(alias="roundId")
    average_rating: float
    total_responses: int
    by_category: dict
    by_source: dict
    key_strengths: List[str] = []
    key_improvements: List[str] = []
    generated_date: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
