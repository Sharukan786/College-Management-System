from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class Report(BaseModel):
    report_type: str = Field(alias="reportType")
    generated_by: str = Field(alias="generatedBy")
    generated_at: Optional[datetime] = Field(default=None, alias="generatedAt")
    file_url: str = Field(default="", alias="fileUrl")
