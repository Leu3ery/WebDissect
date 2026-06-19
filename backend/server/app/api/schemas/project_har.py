from pydantic import BaseModel, Field


class ProjectHar(BaseModel):
    project_id: int = Field(description="ID of the project")
    har_id: int     = Field(description="ID of the har file")


