from pydantic import BaseModel, Field
from datetime import datetime


class Certificate(BaseModel):
    id: int                   = Field()
    subject_domain: str       = Field()
    subject_organization: str = Field()
    subject_country: str      = Field()
    issuer_name: str          = Field()
    issuer_organization: str  = Field()
    issuer_country: str       = Field()
    valid_from: datetime      = Field()
    valid_to: datetime        = Field()
    serial_number: str        = Field()
    public_key_type: str      = Field()
    fingerprint_sha256: str   = Field()


