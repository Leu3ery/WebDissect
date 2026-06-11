from pydantic import BaseModel, ConfigDict, Field


class Subdomain(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None, description="id in the DB")
    name: str      = Field(description="Fully qualified subdomain name")
    ip: str        = Field(default="", description="Resolved IP address, if any")
    source: str    = Field(default="crt.sh", description="Discovery source")
