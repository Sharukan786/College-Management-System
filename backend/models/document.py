from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class Document(BaseModel):
    student_id: str = Field(alias="studentId")
    file_name: str = Field(alias="fileName")
    category: str
    file_url: str = Field(alias="fileUrl")
    uploaded_at: Optional[datetime] = Field(default=None, alias="uploadedAt")
