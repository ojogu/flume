from datetime import datetime
from typing import Optional
import uuid
import enum

from pydantic import BaseModel


class ApiKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


class CreateApiKeyRequest(BaseModel):
    name: str
    expires_at: Optional[datetime] = None


class UpdateApiKeyRequest(BaseModel):
    name: Optional[str] = None
    expires_at: Optional[datetime] = None


class ApiKeyResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    key_prefix: str
    status: ApiKeyStatus
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class ApiKeyCreatedResponse(ApiKeyResponse):
    full_key: str


class ApiKeyListResponse(BaseModel):
    keys: list[ApiKeyResponse]
    total: int
