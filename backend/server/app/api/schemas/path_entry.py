from pydantic import BaseModel, ConfigDict, Field


class PathEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None    = Field(default=None, description="id in the DB")
    path: str         = Field(description="Discovered path")
    status: int       = Field(description="HTTP status code")
    content_type: str = Field(default="", description="Response content type")
    length: int       = Field(default=0, description="Response body length in bytes")
