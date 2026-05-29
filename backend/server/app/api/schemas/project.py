from pydantic import BaseModel, Field


class Project(BaseModel):
    id: int      = Field()
    name: str    = Field()
    domain: str  = Field()
    user_id: int = Field()

