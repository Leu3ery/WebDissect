from pydantic import BaseModel, Field, model_validator, ValidationError


class PatchProject(BaseModel):
    name: str | None   = Field(default=None)
    domain: str | None = Field(default=None)

    @model_validator(mode="before")
    def require_name_or_domain(cls, d: dict) -> dict:
        if not (d.get("name") or d.get("domain")):
            raise ValidationError({"name": "Must provide either a name or a domain"})
        return d

