from typing import Any, Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    resolution: Optional[str] = None
    data: Optional[Any] = None
    role: Optional[str] = None

class SuccessResponse(BaseModel):
    status:str = "success"
    message:str
    data: Optional[Any] = None
    role: Optional[str] = None