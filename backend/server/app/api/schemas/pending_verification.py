from pydantic import BaseModel, Field

from datetime import datetime


class PendingVerification(BaseModel):
    id: int              = Field()
    email: str           = Field()
    code: str            = Field()
    expires_at: datetime = Field()
    attempts: int        = Field()


