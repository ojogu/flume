from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel

from src.core.dependency import get_analytics_service
from src.service.analytics import PageViewService
from src.utils.log import get_logger
from src.utils.response import success

logger = get_logger(__name__)

analytics_route = APIRouter(prefix="/analytics", tags=["analytics"])


class PageViewRequest(BaseModel):
    path: str
    referrer: str | None = None


class PageViewResponse(BaseModel):
    recorded: bool


@analytics_route.post("/pageview", status_code=status.HTTP_201_CREATED)
async def record_page_view(
    body: PageViewRequest,
    request: Request,
    analytics_service: PageViewService = Depends(get_analytics_service),
):
    """Record a page view — fire-and-forget, no auth required.

    Deduplicated by (visitor_hash, path) within 5 minutes via Redis.
    """
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent")

    recorded = await analytics_service.record_visit(
        path=body.path,
        ip=ip,
        user_agent=user_agent,
        referrer=body.referrer,
    )

    return success(
        data=PageViewResponse(recorded=recorded).model_dump(),
        message="Page view recorded",
    )
