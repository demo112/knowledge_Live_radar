from typing import Generic, TypeVar, List, Any, Optional
from pydantic import BaseModel

T = TypeVar("T")

class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: PaginatedData[T]
