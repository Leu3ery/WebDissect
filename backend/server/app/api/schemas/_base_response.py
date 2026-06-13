from typing import Any
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    is_success: bool          = Field(serialization_alias="isSuccess", default=True)
    error_message: str | None = Field(serialization_alias="errorMessage", default=None)
    data: Any | None          = Field(default={})


