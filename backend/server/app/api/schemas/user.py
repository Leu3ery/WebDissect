from datetime import datetime
from pydantic import BaseModel, Field


class User(BaseModel):
    id: int | None       = Field(description="User ID")
    email: str           = Field(description="User Email")
    password_hash: str   = Field(description="User Password Hash")
    created_at: datetime = Field(description="When the user was created")


