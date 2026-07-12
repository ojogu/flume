from fastapi import APIRouter, Depends

from src.core.dependency import get_api_key_from_header, get_platform_service
from src.model.api import ApiKey
from src.internal.schema.platforms import PlatformResponse, PlatformListResponse
from src.public.schema.utils import EventInfo, EventListResponse, VerifyKeyResponse
from src.service.platform import PlatformService
from src.service.util import UtilService
from src.utils.response import success

# ── Public utility routes ─────────────────────────────────────────────────────
# Discovery and verification endpoints for API consumers.
# Platform and event endpoints require no auth. Verify-key uses the
# X-API-Key header via the existing get_api_key_from_header dependency.
# Mounted on /v1/utils.

utils_route = APIRouter(prefix="/utils", tags=["utils"])


@utils_route.get("/platforms")
async def list_platforms(
    platform_service: PlatformService = Depends(get_platform_service),
):
    """List all active supported platforms."""
    platforms = await platform_service.get_platforms(active_only=True)
    return success(
        data=PlatformListResponse(
            platforms=[PlatformResponse(**p.to_dict()) for p in platforms],
            total=len(platforms),
        ).model_dump(),
    )


@utils_route.get("/events")
async def list_events():
    """List all webhook event types with descriptions and payload schemas."""
    events = UtilService.get_events()
    return success(
        data=EventListResponse(
            events=[EventInfo(**e) for e in events],
        ).model_dump(),
    )


@utils_route.get("/verify-key")
async def verify_api_key(
    api_key: ApiKey = Depends(get_api_key_from_header),
):
    """Verify the API key from the X-API-Key header and return its metadata.

    This is a read-only check — it does NOT update last_used_at.
    The key is already resolved by get_api_key_from_header; we just
    return its metadata without touching the database.
    """
    return success(
        data=VerifyKeyResponse(
            valid=True,
            key_prefix=api_key.key_prefix,
            name=api_key.name,
            expires_at=api_key.expires_at,
            last_used_at=api_key.last_used_at,
            status=api_key.status,
        ).model_dump(),
    )
