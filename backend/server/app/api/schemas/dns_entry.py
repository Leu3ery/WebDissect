from pydantic import BaseModel, Field, ConfigDict
from enum import StrEnum

class DNSEntryType(StrEnum):
    IPv4 = "A"
    IPv6 = "AAAA"
    MX = "MX"
    NS = "NS"
    TXT = "TXT"
    SOA = "SOA"
    SRV = "SRV"
    CNAME = "CNAME"


class DNSEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None     = Field(description="id of DNS entry in the DB", default=None)
    type: DNSEntryType = Field(description="")
    domain: str        = Field(description="")
    value: str         = Field(description="Text value of the DNS entry")
    ttl: int           = Field(description="Time to live of the DNS entry")


