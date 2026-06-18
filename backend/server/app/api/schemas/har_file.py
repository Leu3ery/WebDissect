from pydantic import BaseModel, Field


class HarFile(BaseModel):
    id: int | None = Field(description="id of the Har File in the DB")
    filename: str  = Field(description="Filename on the server")
    project_id: int | None = Field()
