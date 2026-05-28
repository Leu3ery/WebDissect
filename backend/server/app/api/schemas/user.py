from datetime import datetime
from pydantic import BaseModel, Field


class User(BaseModel):
    id: int              = Field()
    email: str           = Field()
    password_hash: str   = Field()
    created_at: datetime = Field()


