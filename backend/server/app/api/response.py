from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Envelope every endpoint returns, matching the frontend `ApiResponse<T>`."""

    data: T | None = None
    message: str = ""
    isSuccess: bool = True


def ok(data: T = None, message: str = "") -> ApiResponse[T]:
    return ApiResponse[T](data=data, message=message, isSuccess=True)


def fail(message: str, data: T = None) -> ApiResponse[T]:
    return ApiResponse[T](data=data, message=message, isSuccess=False)
