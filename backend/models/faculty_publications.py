from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class PublicationType(str, Enum):
    JOURNAL = "journal"
    CONFERENCE = "conference"
    BOOK = "book"
    BOOK_CHAPTER = "book_chapter"
    PREPRINT = "preprint"
    WORKSHOP = "workshop"
    REPORT = "report"

class PublicationStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    PUBLISHED = "published"
    REJECTED = "rejected"

class Publication(BaseModel):
    pub_id: str = Field(default_factory=lambda: f"PUB-{datetime.utcnow().timestamp()}")
    faculty_id: str
    title: str
    authors: List[str]
    publication_type: PublicationType
    journal_or_conference_name: str
    publication_year: int
    publication_date: Optional[datetime] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    status: PublicationStatus = PublicationStatus.PUBLISHED
    impact_factor: Optional[float] = None
    citations_count: int = 0
    h_index_boost: float = 0  # Contribution to h-index
    is_open_access: bool = False
    author_position: int = 1  # 1 = first author, 2 = second, etc.
    corresponding_author: bool = False
    research_area: Optional[str] = None
    keywords: List[str] = []
    abstract: Optional[str] = None
    research_projects: List[str] = []  # Project IDs this publication is from
    submitted_date: Optional[datetime] = None
    acceptance_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class PublicationMetrics(BaseModel):
    metrics_id: str = Field(default_factory=lambda: f"PM-{datetime.utcnow().timestamp()}")
    faculty_id: str
    total_publications: int = 0
    by_type: Dict[str, int] = {}  # publication_type -> count
    journal_publications: int = 0
    conference_publications: int = 0
    first_author_publications: int = 0
    corresponding_author_publications: int = 0
    total_citations: int = 0
    average_citations_per_publication: float = 0
    h_index: float = 0  # H-index calculation
    g_index: float = 0  # G-index
    open_access_publications: int = 0
    open_access_percentage: float = 0
    average_impact_factor: Optional[float] = None
    top_publication_impact: Optional[float] = None
    yearly_publication_trend: Dict[int, int] = {}  # year -> count
    co_author_network_size: int = 0
    unique_co_authors: int = 0
    international_collaborations: int = 0
    last_publication_date: Optional[datetime] = None
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class CitationMetric(BaseModel):
    citation_id: str = Field(default_factory=lambda: f"CITE-{datetime.utcnow().timestamp()}")
    pub_id: str
    citing_publication_title: str
    citing_authors: List[str]
    citing_year: int
    database_source: str  # Google Scholar, CrossRef, Web of Science
    citation_date: datetime
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ResearchProductivity(BaseModel):
    prod_id: str = Field(default_factory=lambda: f"RP-{datetime.utcnow().timestamp()}")
    faculty_id: str
    department_id: str
    period: str  # "yearly", "3-year", "5-year"
    start_year: int
    end_year: int
    publications_count: int
    average_publications_per_year: float
    citation_count: int
    average_citations_per_publication: float
    h_index: float
    publications_per_year_data: Dict[int, int] = {}  # year -> publication count
    productivity_score: float  # 0-100
    trend: str  # "increasing", "stable", "declining"
    peer_comparison_percentile: float  # Percentile within department/institution
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class CollaborationNetwork(BaseModel):
    network_id: str = Field(default_factory=lambda: f"CN-{datetime.utcnow().timestamp()}")
    faculty_id: str
    co_authors: Dict[str, Dict]  # author_name -> {count: int, publications: List}
    institutions_collaborated: List[str]
    countries_collaborated: List[str]
    collaboration_strength: float  # 0-1, based on frequency and recency
    international_collaborations_percentage: float
    top_collaborators: List[str] = []
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class PublicationDashboard(BaseModel):
    dashboard_id: str = Field(default_factory=lambda: f"PD-{datetime.utcnow().timestamp()}")
    faculty_id: str
    department_id: str
    total_publications: int
    publication_by_type: Dict[str, int]
    total_citations: int
    h_index: float
    g_index: float
    publication_trend_chart_data: List[Dict]  # For visualization
    top_5_cited_publications: List[Dict]
    research_areas_distribution: Dict[str, int]
    recent_publications: List[Dict] = []
    upcoming_submissions: List[Dict] = []
    collaboration_metrics: Dict
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ImpactReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"IMPACT-{datetime.utcnow().timestamp()}")
    faculty_id: str
    report_period: str
    report_year: int
    total_publications: int
    total_citations: int
    h_index: float
    average_impact_factor: Optional[float]
    open_access_percentage: float
    most_cited_publication: Optional[Dict]
    collaboration_highlights: List[str] = []
    research_impact_statement: str
    recommendations_for_improvement: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
