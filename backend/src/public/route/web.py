from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from src.core.dependency import get_api_key_service
from src.service.api import ApiKeyService
from src.utils.response import success


class SessionResponse(BaseModel):
    api_key: str
    expires_at: str
    jobs_remaining: int


web_route = APIRouter(prefix="/web", tags=["web"])


@web_route.post("/session", status_code=status.HTTP_201_CREATED)
async def create_session(
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    """Create a short-lived session API key for anonymous web users (24h, 5 jobs/day)."""
    api_key, full_key = await api_key_service.create_session_key()

    return success(
        data=SessionResponse(
            api_key=full_key,
            expires_at=api_key.expires_at.isoformat(),
            jobs_remaining=5,
        ).model_dump(),
        message="Session key created",
        status_code=status.HTTP_201_CREATED,
    )
