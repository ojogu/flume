from typing import Any

from pydantic import BaseModel

# Standard response envelope — every endpoint returns {status, message, data, role}
# Success and error responses share this same shape for consistent client-side handling.

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: str | None = None
    resolution: str | None = None
    data: Any | None = None
    role: str | None = None

# Standard envelope: every response (success or error) follows {status, message, data, role}
class SuccessResponse(BaseModel):
    status:str = "success"
    message:str
    data: Any | None = None
    role: str | None = None