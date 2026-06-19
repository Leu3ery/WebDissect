from pydantic import BaseModel, ConfigDict, Field

class Technology(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None   = Field(default=None, description="Internal technology ID")
    name: str        = Field(description="Human readable technology name")
    description: str = Field(default="", description="Technology description")
    icon_url: str    = Field(default="", description="Icon URL")


