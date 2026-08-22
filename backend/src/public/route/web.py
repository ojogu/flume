from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel

from src.core.dependency import get_api_key_service
from src.service.api import WEB_SESSION_MONTHLY_LIMIT, ApiKeyService
from src.utils.response import success


class SessionResponse(BaseModel):
    api_key: str
    expires_at: str
    jobs_remaining: int


web_route = APIRouter(prefix="/web", tags=["web"])


@web_route.post("/session", status_code=status.HTTP_201_CREATED)
async def create_session(
    request: Request,
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    """Create or refresh a short-lived session API key for anonymous web users (35-day TTL, 5 jobs/month).

    If the caller sends a valid, unexpired `web_` key via `X-API-Key`, we return
    that same key with its true `jobs_remaining` (5 - jobs in last 24h). Otherwise
    we mint a brand-new key (the historical behaviour for first-time visitors).
    """
    raw_key = request.headers.get("X-API-Key")
    if raw_key and raw_key.startswith("web_"):
        existing = await api_key_service.verify_key(raw_key)
        if existing:
            count = await api_key_service.count_jobs_this_month(existing.id)
            remaining = max(0, WEB_SESSION_MONTHLY_LIMIT - count)
            return success(
                data=SessionResponse(
                    api_key=raw_key,
                    expires_at=existing.expires_at.isoformat() if existing.expires_at else "",
                    jobs_remaining=remaining,
                ).model_dump(),
                message="Session refreshed",
            )

    api_key, full_key = await api_key_service.create_session_key()

    return success(
        data=SessionResponse(
            api_key=full_key,
            expires_at=api_key.expires_at.isoformat(),
            jobs_remaining=WEB_SESSION_MONTHLY_LIMIT,
        ).model_dump(),
        message="Session key created",
        status_code=status.HTTP_201_CREATED,
    )
