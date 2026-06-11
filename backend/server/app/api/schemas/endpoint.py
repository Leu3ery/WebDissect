from pydantic import BaseModel, ConfigDict, Field

class Endpoint(BaseModel):
    """
    Representation of a single HTTP endpoint (URL + HTTP Method)
    """
    model_config = ConfigDict(from_attributes=True)

    id: int | None    = Field(default=None, description="id of the endpoint in the DB")
    method: str       = Field(description="HTTP Method accepted by the endpoint")
    path: str         = Field(description="Path of the endpoint")
    status: int       = Field(description="HTTP Status code of the response")
    content_type: str = Field(description="Response content type")


