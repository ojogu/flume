import uuid

from fastapi import APIRouter, Depends

from src.service.api import ApiKeyService
from src.core.dependency import get_current_user, get_api_key_service
from src.model.user import User
from src.schema.api import (
    ApiKeyResponse,
    ApiKeyCreatedResponse,
    ApiKeyListResponse,
    CreateApiKeyRequest,
    UpdateApiKeyRequest,
)
from src.utils.response import success

# ── API key CRUD ──────────────────────────────────────────────────────────────
# Authenticated endpoints for managing programmatic keys.
# Thin controller: routes delegate all logic to ApiKeyService, wrap results in response schemas.

api_key_route = APIRouter(prefix="/keys", tags=["api-keys"])


@api_key_route.post("")
async def create_api_key(
    body: CreateApiKeyRequest,
    user: User = Depends(get_current_user),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    api_key, full_key = await api_key_service.create_key(
        user_id=user.id, name=body.name, expires_at=body.expires_at
    )
    return success(
        data=ApiKeyCreatedResponse(
            **api_key.to_dict(),
            full_key=full_key,
        ).model_dump(),
        message="API key created",
    )


@api_key_route.get("")
async def list_api_keys(
    user: User = Depends(get_current_user),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    keys = await api_key_service.get_keys(user_id=user.id)
    return success(
        data=ApiKeyListResponse(
            keys=[ApiKeyResponse(**k.to_dict()) for k in keys],
            total=len(keys),
        ).model_dump()
    )


@api_key_route.get("/{key_id}")
async def get_api_key(
    key_id: str,
    user: User = Depends(get_current_user),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    api_key = await api_key_service.get_key(key_id=uuid.UUID(key_id), user_id=user.id)
    return success(
        data=ApiKeyResponse(**api_key.to_dict()).model_dump()
    )


@api_key_route.patch("/{key_id}")
async def update_api_key(
    key_id: str,
    body: UpdateApiKeyRequest,
    user: User = Depends(get_current_user),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    # exclude_unset=True so we only update fields the client explicitly sent
    api_key = await api_key_service.update_key(
        key_id=uuid.UUID(key_id),
        user_id=user.id,
        data=body.model_dump(exclude_unset=True),
    )
    return success(
        data=ApiKeyResponse(**api_key.to_dict()).model_dump(),
        message="API key updated",
    )


@api_key_route.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    user: User = Depends(get_current_user),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    api_key = await api_key_service.revoke_key(key_id=uuid.UUID(key_id), user_id=user.id)
    return success(
        data=ApiKeyResponse(**api_key.to_dict()).model_dump(),
        message="API key revoked",
    )
