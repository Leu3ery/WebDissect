from pydantic import BaseModel, Field

class HarFile(BaseModel):
    id: int       = Field()
    filename: str = Field()


