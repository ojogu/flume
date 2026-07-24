from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel


class UserResponse(BaseModel):
    """User profile returned by /auth/me and other user-facing endpoints."""
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
    is_admin: bool = False
    name: Optional[str] = None
    picture: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CreateUser(BaseModel):
    """New user creation payload — used internally after OAuth or magic link."""
    google_id: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    email: str
    auth_provider: str
    is_active: bool = False
    email_verified: bool = False
    oauth_verified: bool = False
    onboarded: bool = False
    password_hash: Optional[str] = None
    is_admin: bool = False
    name: Optional[str] = None
    picture: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UpdateUser(BaseModel):
    """Partial user update — all fields optional."""
    google_id: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    email: Optional[str] = None
    auth_provider: Optional[str] = None
    email_verified: Optional[bool] = None
    oauth_verified: Optional[bool] = None
    onboarded: Optional[bool] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class MagicLinkTokenCreate(BaseModel):
    """Request to generate a magic link — just the email address."""
    email: str


class MagicLinkTokenResponse(BaseModel):
    """Magic link token record — returned for admin/debug purposes."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    token: str
    email: str
    resend_email_id: Optional[uuid.UUID] = None
    expires_at: datetime
    used: bool
    created_at: Optional[datetime] = None
