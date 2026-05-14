from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Payroll Models

class PayrollComponent(BaseModel):
    base_salary: float = Field(default=0.0, alias="baseSalary")
    teaching_allowance: float = Field(default=0.0, alias="teachingAllowance")
    research_allowance: float = Field(default=0.0, alias="researchAllowance")
    performance_bonus: float = Field(default=0.0, alias="performanceBonus")
    other_allowances: float = Field(default=0.0, alias="otherAllowances")
    total_earnings: Optional[float] = Field(default=None, alias="totalEarnings")
    
    class Config:
        populate_by_name = True


class DeductionComponent(BaseModel):
    income_tax: float = Field(default=0.0, alias="incomeTax")
    provident_fund: float = Field(default=0.0, alias="providentFund")
    professional_tax: float = Field(default=0.0, alias="professionalTax")
    other_deductions: float = Field(default=0.0, alias="otherDeductions")
    total_deductions: Optional[float] = Field(default=None, alias="totalDeductions")
    
    class Config:
        populate_by_name = True


class TaxCalculation(BaseModel):
    taxable_income: float = Field(default=0.0, alias="taxableIncome")
    tax_rate: float = Field(default=0.0, alias="taxRate")
    tax_amount: float = Field(default=0.0, alias="taxAmount")
    tax_regime: str = Field(default="Old", alias="taxRegime")  # Old or New
    
    class Config:
        populate_by_name = True


class Payroll(BaseModel):
    faculty_id: str = Field(alias="facultyId")
    semester: str
    academic_year: str = Field(alias="academicYear")
    
    # Earnings
    base_salary: float = Field(default=0.0, alias="baseSalary")
    teaching_allowance: float = Field(default=0.0, alias="teachingAllowance")
    research_allowance: float = Field(default=0.0, alias="researchAllowance")
    performance_bonus: float = Field(default=0.0, alias="performanceBonus")
    other_allowances: float = Field(default=0.0, alias="otherAllowances")
    total_earnings: float = Field(default=0.0, alias="totalEarnings")
    
    # Deductions
    income_tax: float = Field(default=0.0, alias="incomeTax")
    provident_fund: float = Field(default=0.0, alias="providentFund")
    professional_tax: float = Field(default=0.0, alias="professionalTax")
    other_deductions: float = Field(default=0.0, alias="otherDeductions")
    total_deductions: float = Field(default=0.0, alias="totalDeductions")
    
    # Net Salary
    net_salary: float = Field(default=0.0, alias="netSalary")
    
    # Tax Details
    tax_calculation: Optional[TaxCalculation] = Field(default=None, alias="taxCalculation")
    
    # Metadata
    payment_date: datetime = Field(default_factory=datetime.now, alias="paymentDate")
    created_date: datetime = Field(default_factory=datetime.now, alias="createdDate")
    updated_date: datetime = Field(default_factory=datetime.now, alias="updatedDate")
    
    class Config:
        populate_by_name = True
    
    def __init__(self, **data):
        super().__init__(**data)
        # Auto-calculate totals
        self.total_earnings = (
            self.base_salary + self.teaching_allowance + 
            self.research_allowance + self.performance_bonus + 
            self.other_allowances
        )
        self.total_deductions = (
            self.income_tax + self.provident_fund + 
            self.professional_tax + self.other_deductions
        )
        self.net_salary = self.total_earnings - self.total_deductions


class PayslipRequest(BaseModel):
    semester: str
    academic_year: str = Field(alias="academicYear")
    
    class Config:
        populate_by_name = True


# Professional Development Models

class ProfessionalDevelopmentActivity(BaseModel):
    activity_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()), alias="activityId")
    faculty_id: str = Field(alias="facultyId")
    activity_type: str = Field(alias="activityType")  # Conference, Workshop, Online Course, Certification, etc.
    title: str
    description: str
    organization: str
    start_date: datetime = Field(alias="startDate")
    end_date: datetime = Field(alias="endDate")
    hours: float = Field(default=0.0)
    certificate_url: Optional[str] = Field(default=None, alias="certificateUrl")
    budget_allocated: float = Field(default=0.0, alias="budgetAllocated")
    budget_spent: float = Field(default=0.0, alias="budgetSpent")
    status: str = Field(default="Completed", alias="status")  # Completed, Ongoing, Planned
    created_date: datetime = Field(default_factory=datetime.now, alias="createdDate")
    
    class Config:
        populate_by_name = True


class ResearchContribution(BaseModel):
    research_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()), alias="researchId")
    faculty_id: str = Field(alias="facultyId")
    project_title: str = Field(alias="projectTitle")
    research_area: str = Field(alias="researchArea")
    funding_agency: str = Field(alias="fundingAgency")
    grant_amount: float = Field(default=0.0, alias="grantAmount")
    start_date: datetime = Field(alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    publications: int = Field(default=0)
    collaborators: List[str] = Field(default=[], alias="collaborators")
    status: str = Field(default="Ongoing", alias="status")  # Ongoing, Completed, Proposed
    created_date: datetime = Field(default_factory=datetime.now, alias="createdDate")
    
    class Config:
        populate_by_name = True


class DepartmentInitiative(BaseModel):
    initiative_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()), alias="initiativeId")
    department_id: str = Field(alias="departmentId")
    initiative_name: str = Field(alias="initiativeName")
    description: str
    objective: str
    assigned_faculty: List[str] = Field(default=[], alias="assignedFaculty")
    start_date: datetime = Field(alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    budget: float = Field(default=0.0)
    status: str = Field(default="Proposed", alias="status")  # Proposed, Approved, Ongoing, Completed
    outcomes: Optional[str] = Field(default=None, alias="outcomes")
    created_date: datetime = Field(default_factory=datetime.now, alias="createdDate")
    
    class Config:
        populate_by_name = True


class CareerPathway(BaseModel):
    pathway_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()), alias="pathwayId")
    faculty_id: str = Field(alias="facultyId")
    current_designation: str = Field(alias="currentDesignation")
    target_designation: str = Field(alias="targetDesignation")
    target_years: int = Field(alias="targetYears")
    required_qualifications: List[str] = Field(default=[], alias="requiredQualifications")
    completed_milestones: List[str] = Field(default=[], alias="completedMilestones")
    pending_milestones: List[str] = Field(default=[], alias="pendingMilestones")
    mentors: List[str] = Field(default=[], alias="mentors")
    status: str = Field(default="Active", alias="status")
    created_date: datetime = Field(default_factory=datetime.now, alias="createdDate")
    updated_date: datetime = Field(default_factory=datetime.now, alias="updatedDate")
    
    class Config:
        populate_by_name = True


# Faculty Analytics Models

class FacultyPerformanceMetrics(BaseModel):
    faculty_id: str = Field(alias="facultyId")
    academic_year: str = Field(alias="academicYear")
    
    # Teaching Metrics
    student_satisfaction: float = Field(default=0.0, alias="studentSatisfaction")  # 0-5 scale
    course_completion_rate: float = Field(default=0.0, alias="courseCompletionRate")  # percentage
    student_pass_rate: float = Field(default=0.0, alias="studentPassRate")  # percentage
    
    # Research Metrics
    publications_count: int = Field(default=0, alias="publicationsCount")
    citations_count: int = Field(default=0, alias="citationsCount")
    h_index: float = Field(default=0.0, alias="hIndex")
    research_grant_value: float = Field(default=0.0, alias="researchGrantValue")
    
    # Administrative Metrics
    committee_participation: int = Field(default=0, alias="committeeParticipation")
    mentoring_effectiveness: float = Field(default=0.0, alias="mentoringEffectiveness")
    
    # Overall Performance
    overall_score: float = Field(default=0.0, alias="overallScore")
    performance_category: str = Field(alias="performanceCategory")  # Excellent, Good, Average, Needs Improvement
    
    created_date: datetime = Field(default_factory=datetime.now, alias="createdDate")
    
    class Config:
        populate_by_name = True
    
    def __init__(self, **data):
        super().__init__(**data)
        # Auto-calculate overall score
        teaching_weight = 0.35
        research_weight = 0.35
        admin_weight = 0.30
        
        teaching_score = self.student_satisfaction  # 0-5 scale
        research_score = min(self.h_index * 0.5 + min(self.citations_count / 50, 5), 5)
        admin_score = min((self.committee_participation * 0.5 + self.mentoring_effectiveness) / 2, 5)
        
        self.overall_score = (
            teaching_score * teaching_weight +
            research_score * research_weight +
            admin_score * admin_weight
        )
        
        # Categorize performance
        if self.overall_score >= 4.5:
            self.performance_category = "Excellent"
        elif self.overall_score >= 3.5:
            self.performance_category = "Good"
        elif self.overall_score >= 2.5:
            self.performance_category = "Average"
        else:
            self.performance_category = "Needs Improvement"
