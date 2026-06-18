from enum import StrEnum
from pydantic import BaseModel, Field, ConfigDict


class HTTPMethod(StrEnum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'


class Endpoint(BaseModel):
    """
    Representation of a single HTTP endpoint (URL + HTTP Method)
    """
    model_config = ConfigDict(from_attributes=True)

    id: int | None     = Field(description="id of the endpoint in the DB", default=None)
    analysis_id: int   = Field()
    method: HTTPMethod = Field(description="HTTP Method accepted by the endpoint")
    path: str          = Field(description="Path of the endpoint")
    status: int        = Field(description="HTTP Status code of the response")
    content_type: str  = Field(description="Response content type")



