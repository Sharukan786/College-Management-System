from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class InvoiceItem(BaseModel):
    description: str
    amount: float

class InvoiceBase(BaseModel):
    payroll_id: Optional[str] = None
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    staff_name: Optional[str] = None
    pay_period: Optional[str] = None
    total_amount: float
    payment_status: str = "Draft"
    items: Optional[List[InvoiceItem]] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    payment_status: Optional[str] = None
    paid_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None

class InvoiceResponse(InvoiceBase):
    id: str = Field(alias="_id")
    invoice_id: str
    generated_date: datetime

    class Config:
        populate_by_name = True
