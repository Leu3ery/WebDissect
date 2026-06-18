from pydantic import BaseModel, Field, field_validator, ConfigDict
import tldextract


# Build once at import. Empty suffix_list_urls => use the snapshot bundled
# with tldextract instead of fetching the PSL over the network at runtime.
_extract = tldextract.TLDExtract(suffix_list_urls=())


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None      = Field(description="Project ID", default=None)
    name: str           = Field(description="Project Name")
    domain: str         = Field(description="Domain of the analyzed website")

    @field_validator("domain", mode="before")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        v = v.strip().lower().rstrip(".")

        ext = tldextract.extract(v)
        if not ext.domain or not ext.suffix:
            raise ValueError("Invalid domain structure.")
        if ext.subdomain:
            raise ValueError("enter the apex domain, not a subdomain")

        return ext.top_domain_under_public_suffix  # normalized "example.co.uk"


