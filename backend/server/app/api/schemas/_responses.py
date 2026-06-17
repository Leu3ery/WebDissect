from typing import Any, TypeVar, Generic
from pydantic import BaseModel, Field

from .project import Project

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    is_success: bool          = Field(serialization_alias="isSuccess", default=True)
    error_message: str | None = Field(serialization_alias="errorMessage", default=None)
    data: T                   = Field()



class AnalysisStartData(BaseModel):
    analysis_id: int = Field(serialization_alias="analysisId")

class AnalysisStart(BaseResponse[AnalysisStartData]):
    data: AnalysisStartData



class Projects(BaseModel):
    projects: list[Project]

class ProjectsData(BaseResponse[Projects]):
    data: Projects


class ProjectData(BaseResponse[Project]):
    data: Project


