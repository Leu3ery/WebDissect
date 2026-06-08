from pydantic import BaseModel, Field

class Technology(BaseModel):
    id: int          = Field(description="Internal technology ID")
    name: str        = Field(description="Human readable technology name")
    description: str = Field(description="Technology description")
    icon_url: str    = Field(description="Icon URL")


