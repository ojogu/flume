import uuid
from datetime import datetime

from pydantic import BaseModel

from src.model.api import ApiKeyStatus


class CreateApiKeyRequest(BaseModel):
    """Request to create a new API key — name, optional expiry."""
    name: str
    expires_at: datetime | None = None


class UpdateApiKeyRequest(BaseModel):
    """Request to update an API key — name and/or expiry."""
    name: str | None = None
    expires_at: datetime | None = None


class ApiKeyResponse(BaseModel):
    """API key response (full_key excluded — only returned once at creation)."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    key_prefix: str
    status: ApiKeyStatus
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    created_at: datetime | None = None


# Extends ApiKeyResponse with full_key because the raw key is only shown once at creation
class ApiKeyCreatedResponse(ApiKeyResponse):
    full_key: str


class ApiKeyListResponse(BaseModel):
    keys: list[ApiKeyResponse]
    total: int
