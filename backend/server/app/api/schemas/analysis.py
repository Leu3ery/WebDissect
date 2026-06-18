from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class Analysis(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int                          = Field()
    project_id: int                  = Field()
    started_at: datetime             = Field(default_factory=datetime.now)
    is_dns_analysis_completed: bool  = Field(default=False)   # TODO: remove
    is_cert_analysis_completed: bool = Field(default=False)   # TODO: remove


