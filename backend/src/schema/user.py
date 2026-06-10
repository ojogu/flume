from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    google_id: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    email: str
    auth_provider: str
    is_active: bool
    email_verified: bool
    oauth_verified: bool
    onboarded: bool
    name: Optional[str] = None
    picture: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CreateUser(BaseModel):
    google_id: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    email: str
    auth_provider: str
    is_active: bool = False
    email_verified: bool = False
    oauth_verified: bool = False
    onboarded: bool = False
    name: Optional[str] = None
    picture: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UpdateUser(BaseModel):
    google_id: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    email: Optional[str] = None
    auth_provider: Optional[str] = None
    email_verified: Optional[bool] = None
    oauth_verified: Optional[bool] = None
    onboarded: Optional[bool] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class MagicLinkTokenCreate(BaseModel):
    email: str


class MagicLinkTokenResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    token: str
    email: str
    resend_email_id: Optional[uuid.UUID] = None
    expires_at: datetime
    used: bool
    created_at: Optional[datetime] = None