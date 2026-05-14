from typing import Optional, Any

from pydantic import BaseModel, Field


class SystemSetting(BaseModel):
    key: str
    value: Any
    description: str = ""
    updated_at: Optional[str] = Field(default=None, alias="updatedAt")
