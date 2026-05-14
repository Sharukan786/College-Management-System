from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ResearchStatus(str, Enum):
    PROPOSAL = "proposal"
    ACTIVE = "active"
    COMPLETED = "completed"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class FundingStatus(str, Enum):
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    FUNDED = "funded"
    COMPLETED = "completed"

class ResearchProject(BaseModel):
    project_id: str = Field(default_factory=lambda: f"RP-{datetime.utcnow().timestamp()}")
    title: str
    description: str
    principal_investigator_id: str
    co_investigators: List[str] = []
    department_id: str
    status: ResearchStatus = ResearchStatus.ACTIVE
    research_area: str
    start_date: datetime
    end_date: Optional[datetime] = None
    total_budget: Optional[float] = None
    publications_target: int = 0
    publications_achieved: int = 0
    keywords: List[str] = []
    collaborating_departments: List[str] = []
    collaborating_institutions: List[str] = []
    abstract: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class FundingGrant(BaseModel):
    grant_id: str = Field(default_factory=lambda: f"GRANT-{datetime.utcnow().timestamp()}")
    project_id: str
    faculty_id: str  # Primary grant holder
    grant_name: str
    funding_agency: str
    grant_amount: float
    currency: str = "USD"
    status: FundingStatus = FundingStatus.SUBMITTED
    submission_date: datetime
    approval_date: Optional[datetime] = None
    start_date: datetime
    end_date: datetime
    grant_period_months: int
    co_investigators: List[str] = []
    budget_allocation: dict = {}  # category -> amount
    utilization_percentage: float = 0
    publications_funded: List[str] = []
    reports_submitted: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ResearchCollaborator(BaseModel):
    collaborator_id: str = Field(default_factory=lambda: f"COLLAB-{datetime.utcnow().timestamp()}")
    project_id: str
    faculty_id: str
    name: str
    email: str
    affiliation: str  # Department or external institution
    role: str  # "co-investigator", "collaborator", "consultant"
    contribution_percentage: float = Field(..., ge=0, le=100)
    expertise_areas: List[str] = []
    contribution_description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    is_external: bool = False
    added_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ResearchMilestone(BaseModel):
    milestone_id: str = Field(default_factory=lambda: f"MILE-{datetime.utcnow().timestamp()}")
    project_id: str
    title: str
    description: Optional[str] = None
    scheduled_date: datetime
    completion_date: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, delayed
    deliverables: List[str] = []
    responsible_faculty: List[str] = []
    progress_percentage: float = 0
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ResearchPublication(BaseModel):
    publication_id: str = Field(default_factory=lambda: f"PUB-{datetime.utcnow().timestamp()}")
    project_id: str
    title: str
    authors: List[str]
    publication_type: str  # journal, conference, book, preprint
    journal_name: Optional[str] = None
    conference_name: Optional[str] = None
    publication_date: datetime
    doi: Optional[str] = None
    url: Optional[str] = None
    impact_factor: Optional[float] = None
    citations_count: int = 0
    is_open_access: bool = False
    funding_acknowledged: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ResearchCollaborationNetwork(BaseModel):
    network_id: str = Field(default_factory=lambda: f"RCN-{datetime.utcnow().timestamp()}")
    faculty_id: str
    department_id: str
    collaborator_count: int = 0
    active_projects: int = 0
    total_publications: int = 0
    total_grant_amount: float = 0
    internal_collaborations: int = 0
    external_collaborations: int = 0
    international_collaborations: int = 0
    h_index: Optional[float] = None
    research_impact_score: Optional[float] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
