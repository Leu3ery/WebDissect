from typing import TypeVar, Generic, Optional
from pydantic import BaseModel, Field

from .project import Project

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    is_success: bool             = Field(serialization_alias="isSuccess", default=True)
    error_message: Optional[str] = Field(serialization_alias="errorMessage", default=None)
    data: Optional[T]            = Field(default=None)

    @classmethod
    def ok(cls, data: T | None = None) -> "BaseResponse[T]":
        return cls(is_success=True, data=data)

    @classmethod
    def fail(cls, message: str) -> "BaseResponse[T]":
        return cls(is_success=False, error_message=message)


class CreateProject(BaseModel):
    project_id: int = Field(serialization_alias="projectId")


class AnalysisStart(BaseModel):
    analysis_id: int = Field(serialization_alias="analysisId")


class Projects(BaseModel):
    projects: list[Project] = Field()


class FileUpload(BaseModel):
    entry_count: int = Field(serialization_alias="entryCount")

