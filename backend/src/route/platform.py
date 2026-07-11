import uuid

from fastapi import APIRouter, Depends

from src.core.dependency import get_current_user, get_platform_service
from src.model.user import User
from src.schema.platform import (
    CreatePlatformRequest,
    UpdatePlatformRequest,
    PlatformResponse,
    PlatformListResponse,
)
from src.service.platform import PlatformService
from src.utils.response import success

# ── Platform CRUD ─────────────────────────────────────────────────────────────
# Authenticated endpoints for managing supported media platforms.
# Thin controller: routes delegate all logic to PlatformService, wrap results
# in response schemas. Mounted on /internal/platforms (JWT auth, dashboard only).

platform_route = APIRouter(prefix="/platforms", tags=["platforms"])


@platform_route.post("")
async def create_platform(
    body: CreatePlatformRequest,
    user: User = Depends(get_current_user),
    platform_service: PlatformService = Depends(get_platform_service),
):
    platform = await platform_service.create_platform(data=body.model_dump())
    return success(
        data=PlatformResponse(**platform.to_dict()).model_dump(),
        message="Platform created",
    )


@platform_route.get("")
async def list_platforms(
    user: User = Depends(get_current_user),
    platform_service: PlatformService = Depends(get_platform_service),
    active_only: bool = False,
):
    platforms = await platform_service.get_platforms(active_only=active_only)
    return success(
        data=PlatformListResponse(
            platforms=[PlatformResponse(**p.to_dict()) for p in platforms],
            total=len(platforms),
        ).model_dump(),
    )


@platform_route.get("/{platform_id}")
async def get_platform(
    platform_id: uuid.UUID,
    user: User = Depends(get_current_user),
    platform_service: PlatformService = Depends(get_platform_service),
):
    platform = await platform_service.get_platform(platform_id=platform_id)
    return success(
        data=PlatformResponse(**platform.to_dict()).model_dump(),
    )


@platform_route.patch("/{platform_id}")
async def update_platform(
    platform_id: uuid.UUID,
    body: UpdatePlatformRequest,
    user: User = Depends(get_current_user),
    platform_service: PlatformService = Depends(get_platform_service),
):
    platform = await platform_service.update_platform(
        platform_id=platform_id,
        data=body.model_dump(exclude_unset=True),
    )
    return success(
        data=PlatformResponse(**platform.to_dict()).model_dump(),
        message="Platform updated",
    )


@platform_route.delete("/{platform_id}")
async def delete_platform(
    platform_id: uuid.UUID,
    user: User = Depends(get_current_user),
    platform_service: PlatformService = Depends(get_platform_service),
):
    await platform_service.delete_platform(platform_id=platform_id)
    return success(
        message="Platform deleted",
    )
