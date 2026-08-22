from fastapi import APIRouter, Depends, Query

from src.core.dependency import get_analytics_service, get_current_admin
from src.model.user import User
from src.service.analytics import PageViewService
from src.utils.log import get_logger
from src.utils.response import success

logger = get_logger(__name__)

stats_route = APIRouter(prefix="/stats", tags=["stats"])


@stats_route.get("")
async def get_stats(
    days: int = Query(30, ge=1, le=365),
    _admin: User = Depends(get_current_admin),
    analytics_service: PageViewService = Depends(get_analytics_service),
):
    """Return aggregated stats for the admin dashboard — admin-only.

    Includes page views, unique visitors, top paths, top referrers,
    and job breakdown by origin and status.
    """
    stats = await analytics_service.get_stats(days=days)
    return success(data=stats)
