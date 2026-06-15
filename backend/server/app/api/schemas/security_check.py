from pydantic import BaseModel, ConfigDict, Field


class SecurityCheck(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None, description="id in the DB")
    category: str  = Field(description="header | tls | cookie")
    name: str      = Field(description="Check name")
    status: str    = Field(description="ok | warn | fail | info")
    severity: str  = Field(default="info", description="high | medium | low | info")
    detail: str    = Field(default="", description="Human readable detail / recommendation")
