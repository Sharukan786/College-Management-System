from datetime import date

from pydantic import BaseModel, Field


class Fee(BaseModel):
    student_id: str = Field(alias="studentId")
    fee_type: str = Field(alias="feeType")
    receipt_number: str = Field(default="", alias="receiptNumber")
    due_amount: float = Field(alias="dueAmount", ge=0)
    paid_amount: float = Field(default=0, alias="paidAmount", ge=0)
    status: str = "pending"
    date: date
