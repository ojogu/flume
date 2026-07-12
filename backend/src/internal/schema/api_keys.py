from datetime import datetime
from typing import Optional
import uuid
import enum

from pydantic import BaseModel


class ApiKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


class CreateApiKeyRequest(BaseModel):
    """Request to create a new API key — name, optional expiry."""
    name: str
    expires_at: Optional[datetime] = None


class UpdateApiKeyRequest(BaseModel):
    """Request to update an API key — name and/or expiry."""
    name: Optional[str] = None
    expires_at: Optional[datetime] = None


class ApiKeyResponse(BaseModel):
    """API key response (full_key excluded — only returned once at creation)."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    key_prefix: str
    status: ApiKeyStatus
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


# Extends ApiKeyResponse with full_key because the raw key is only shown once at creation
class ApiKeyCreatedResponse(ApiKeyResponse):
    full_key: str


class ApiKeyListResponse(BaseModel):
    keys: list[ApiKeyResponse]
    total: int
