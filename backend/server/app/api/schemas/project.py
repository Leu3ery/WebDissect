from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlparse


class Project(BaseModel):
    id: int | None      = Field(description="Project ID", default=None)
    name: str           = Field(description="Project Name")
    domain: str         = Field(description="Domain of the analyzed website")
    user_id: int | None = Field(description="id of the project owner", default=None)

    @field_validator("domain", mode="before")
    @classmethod
    def format_domain(cls, v: str) -> str:
        if "//" not in v:
            v = f"//{v}"
        return urlparse(v).netloc


