from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalysisRunRead(BaseModel):
    """A single point in a project's analysis history."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    kind: str = "analysis"
    counts: dict[str, int] = Field(default_factory=dict)
