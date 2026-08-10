import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

# ── Platform CRUD schemas ─────────────────────────────────────────────────────
# Request/response bodies for platform management endpoints.
# Content types are validated against the fixed set: single, playlist, vod.

ContentType = Literal["single", "playlist", "vod"]


class CreatePlatformRequest(BaseModel):
    """Request to create a new supported platform."""
    slug: str
    name: str
    url: str
    is_active: bool = True
    content_types: list[ContentType] = ["single"]
    requires_login: bool = False
    supports_live: bool = False
    description: str | None = None
    limitations: str | None = None
    logo_url: str | None = None
    sort_order: int = 0


class UpdatePlatformRequest(BaseModel):
    """Request to update a platform — all fields optional (partial update)."""
    slug: str | None = None
    name: str | None = None
    url: str | None = None
    is_active: bool | None = None
    content_types: list[ContentType] | None = None
    requires_login: bool | None = None
    supports_live: bool | None = None
    description: str | None = None
    limitations: str | None = None
    logo_url: str | None = None
    sort_order: int | None = None


class PlatformResponse(BaseModel):
    """Platform response — returned by all platform endpoints."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    slug: str
    name: str
    url: str
    is_active: bool
    content_types: list
    requires_login: bool
    supports_live: bool
    description: str | None = None
    limitations: str | None = None
    logo_url: str | None = None
    sort_order: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PlatformListResponse(BaseModel):
    platforms: list[PlatformResponse]
    total: int
