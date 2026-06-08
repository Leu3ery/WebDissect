from pydantic import BaseModel, Field

from datetime import datetime


class PendingVerification(BaseModel):
    id: int              = Field(description="")
    email: str           = Field(description="Email address that received the verification code")
    code: str            = Field(description="Verification Code")
    expires_at: datetime = Field(description="")
    attempts: int        = Field(description="Attempts of entering the code")


