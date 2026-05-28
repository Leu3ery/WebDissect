from pydantic import BaseModel, Field

class DNSEntry(BaseModel):
    id: int     = Field()
    type: str   = Field()
    domain: str = Field()
    value: str  = Field()
    ttl: int    = Field()


