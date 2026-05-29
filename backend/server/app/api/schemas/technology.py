from pydantic import BaseModel, Field

class Technology(BaseModel):
    id: int          = Field()
    name: str        = Field()
    description: str = Field()
    icon_url: str    = Field()


