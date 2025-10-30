from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

# Generic type variable for response data
T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    """
    Standardized success response wrapper.
    
    Attributes:
        data: The actual payload/response data
        message: Optional human-readable success message
        status_code: HTTP status code (default: 200)
    """
    data: T
    message: Optional[str] = Field(None, description="Success message")
    status_code: int = Field(200, description="HTTP status code")


class ErrorResponse(BaseModel):
    """
    Standardized error response wrapper.
    
    Attributes:
        error: User-facing error message
        status_code: HTTP status code (default: 500)
        details: Optional additional context (use sparingly in production)
    """
    error: str = Field(..., description="Human-readable error message")
    status_code: int = Field(500, description="HTTP status code")
    details: Optional[Any] = Field(None, description="Additional error context")

