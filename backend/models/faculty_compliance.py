from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AlertPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AlertType(str, Enum):
    CONTRACT_RENEWAL = "contract_renewal"
    COMPLIANCE_DEADLINE = "compliance_deadline"
    CERTIFICATION_EXPIRY = "certification_expiry"
    EVALUATION_DUE = "evaluation_due"
    DOCUMENT_EXPIRY = "document_expiry"
    PROMOTION_ELIGIBILITY = "promotion_eligibility"
    SABBATICAL_ELIGIBILITY = "sabbatical_eligibility"
    TRAINING_REQUIRED = "training_required"

class ComplianceRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"CR-{datetime.utcnow().timestamp()}")
    name: str
    category: str  # "contractual", "regulatory", "institutional", "certification"
    department_id: Optional[str] = None
    faculty_id: Optional[str] = None  # If null, applies to all faculty
    description: str
    frequency: str  # "annually", "biannually", "once", "custom"
    deadline_months_before: int  # How many months before deadline to alert
    is_mandatory: bool = True
    documentation_required: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ContractInfo(BaseModel):
    contract_id: str = Field(default_factory=lambda: f"CTR-{datetime.utcnow().timestamp()}")
    faculty_id: str
    contract_type: str  # "permanent", "temporary", "contract"
    start_date: datetime
    end_date: datetime
    position: str
    department_id: str
    contract_status: str = "active"  # active, expiring, expired, renewed
    renewal_terms: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ComplianceRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"COMP-{datetime.utcnow().timestamp()}")
    faculty_id: str
    requirement_id: str
    requirement_name: str
    requirement_category: str
    due_date: datetime
    completion_date: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, overdue
    evidence_document: Optional[str] = None
    verified: bool = False
    verified_by: Optional[str] = None
    verified_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ComplianceAlert(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"ALERT-{datetime.utcnow().timestamp()}")
    faculty_id: str
    alert_type: AlertType
    priority: AlertPriority
    title: str
    description: str
    related_record_id: Optional[str] = None
    due_date: datetime
    days_remaining: int
    action_required: str
    is_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    notifications_sent: int = 0
    last_notification_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Certification(BaseModel):
    certification_id: str = Field(default_factory=lambda: f"CERT-{datetime.utcnow().timestamp()}")
    faculty_id: str
    certification_name: str
    issuing_organization: str
    issue_date: datetime
    expiry_date: datetime
    certification_number: str
    is_active: bool = True
    renewal_available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class DocumentExpiry(BaseModel):
    doc_id: str = Field(default_factory=lambda: f"DOC-{datetime.utcnow().timestamp()}")
    faculty_id: str
    document_type: str  # "passport", "visa", "license", "permit"
    issue_date: datetime
    expiry_date: datetime
    issuing_authority: str
    identifier_number: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ComplianceDashboard(BaseModel):
    faculty_id: str
    total_requirements: int = 0
    completed_requirements: int = 0
    pending_requirements: int = 0
    overdue_requirements: int = 0
    compliance_percentage: float = 0
    critical_alerts: int = 0
    high_alerts: int = 0
    expiring_documents: List[str] = []
    contract_expiry_date: Optional[datetime] = None
    days_until_contract_expiry: Optional[int] = None
    last_evaluation_date: Optional[datetime] = None
    next_evaluation_due: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
