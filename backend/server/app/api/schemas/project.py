from pydantic import BaseModel, Field


class Project(BaseModel):
    id: int | None = Field(description="Project ID")
    name: str      = Field(description="Project Name")
    domain: str    = Field(description="Domain of the analyzed website")
    user_id: int   = Field(description="id of the project owner")

