from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas.certificate import Certificate
from app.api.schemas.dns_entry import DNSEntry
from app.api.schemas.endpoint import Endpoint
from app.api.schemas.path_entry import PathEntry
from app.api.schemas.port import Port
from app.api.schemas.subdomain import Subdomain
from app.api.schemas.technology import Technology


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime


class TokenRead(BaseModel):
    token: str


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domain: str
    user_id: int


class ProjectFull(ProjectRead):
    certificates: list[Certificate] = Field(default_factory=list)
    dns_entries: list[DNSEntry] = Field(default_factory=list)
    technologies: list[Technology] = Field(default_factory=list)
    endpoints: list[Endpoint] = Field(default_factory=list)
    subdomains: list[Subdomain] = Field(default_factory=list)
    ports: list[Port] = Field(default_factory=list)
    path_entries: list[PathEntry] = Field(default_factory=list)
