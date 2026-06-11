from pydantic import BaseModel, ConfigDict, Field


class Port(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None, description="id in the DB")
    port: int      = Field(description="TCP port number")
    protocol: str  = Field(default="tcp", description="Transport protocol")
    state: str     = Field(default="open", description="Port state")
    service: str   = Field(default="", description="Detected service name")
    version: str   = Field(default="", description="Detected service/version banner")
    banner: str    = Field(default="", description="Raw banner snippet")
