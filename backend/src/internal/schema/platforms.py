from datetime import datetime
from typing import Literal, Optional
import uuid

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
    description: Optional[str] = None
    limitations: Optional[str] = None
    logo_url: Optional[str] = None
    sort_order: int = 0


class UpdatePlatformRequest(BaseModel):
    """Request to update a platform — all fields optional (partial update)."""
    slug: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None
    content_types: Optional[list[ContentType]] = None
    requires_login: Optional[bool] = None
    supports_live: Optional[bool] = None
    description: Optional[str] = None
    limitations: Optional[str] = None
    logo_url: Optional[str] = None
    sort_order: Optional[int] = None


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
    description: Optional[str] = None
    limitations: Optional[str] = None
    logo_url: Optional[str] = None
    sort_order: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PlatformListResponse(BaseModel):
    platforms: list[PlatformResponse]
    total: int
