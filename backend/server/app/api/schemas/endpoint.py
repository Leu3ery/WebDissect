from pydantic import BaseModel, Field

class Endpoint(BaseModel):
    id: int           = Field()
    method: str       = Field()
    path: str         = Field()
    status: int       = Field()
    content_type: str = Field()


