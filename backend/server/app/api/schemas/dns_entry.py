from pydantic import BaseModel, Field
from enum import StrEnum

class EntryType(StrEnum):
    IPv4 = "A"
    IPv6 = "AAAA"
    MX = "MX"
    NS = "NS"
    TXT = "TXT"
    SOA = "SOA"
    SRV = "SRV"
    CNAME = "CNAME"


class DNSEntry(BaseModel):
    id: int | None  = Field(description="id of DNS entry in the DB", default=None)
    type: EntryType = Field(description="")
    domain: str     = Field(description="")
    value: str      = Field(description="Text value of the DNS entry")
    ttl: int        = Field(description="Time to live of the DNS entry")


