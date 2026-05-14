from pydantic import BaseModel, Field


class Department(BaseModel):
    name: str
    code: str = Field(min_length=1)
    head_of_department: str = Field(default="", alias="headOfDepartment")
