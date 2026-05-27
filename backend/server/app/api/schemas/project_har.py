from pydantic import BaseModel, Field


class ProjectHar(BaseModel):
    project_id: int = Field()
    har_id: int     = Field()


