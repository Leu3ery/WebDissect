from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class Certificate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None            = Field(default=None, description="id of cert in the DB")
    subject_domain: str       = Field(description="Domain for which the certificate is issued")
    subject_organization: str = Field(description="Owner Organization")
    subject_country: str      = Field(description="Country in which the company resides")
    issuer_name: str          = Field(description="")
    issuer_organization: str  = Field(description="")
    issuer_country: str       = Field(description="")
    valid_from: datetime      = Field(description="")
    valid_to: datetime        = Field(description="")
    serial_number: str        = Field(description="")
    public_key_type: str      = Field(description="")
    fingerprint_sha256: str   = Field(description="sha256 fingerprint of the certificate")


