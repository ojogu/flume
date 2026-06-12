from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi import status
from src.schema.response import SuccessResponse


# Thin helper wrapping SuccessResponse into a JSONResponse with consistent envelope
def success(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    role: Optional[str] = None,
) -> JSONResponse:
    body = SuccessResponse(message=message, data=data, role=role)
    return JSONResponse(content=body.model_dump(mode="json"), status_code=status_code)
