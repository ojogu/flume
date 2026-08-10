import uuid
from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    """User profile returned by /auth/me and other user-facing endpoints."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    google_id: str | None = None
    refresh_token: str | None = None
    access_token: str | None = None
    email: str
    auth_provider: str
    is_active: bool
    email_verified: bool
    oauth_verified: bool
    onboarded: bool
    is_admin: bool = False
    name: str | None = None
    picture: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CreateUser(BaseModel):
    """New user creation payload — used internally after OAuth or magic link."""
    google_id: str | None = None
    refresh_token: str | None = None
    access_token: str | None = None
    email: str
    auth_provider: str
    is_active: bool = False
    email_verified: bool = False
    oauth_verified: bool = False
    onboarded: bool = False
    password_hash: str | None = None
    is_admin: bool = False
    name: str | None = None
    picture: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UpdateUser(BaseModel):
    """Partial user update — all fields optional."""
    google_id: str | None = None
    refresh_token: str | None = None
    access_token: str | None = None
    email: str | None = None
    auth_provider: str | None = None
    email_verified: bool | None = None
    oauth_verified: bool | None = None
    onboarded: bool | None = None
    password: str | None = None
    is_admin: bool | None = None
    name: str | None = None
    picture: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class MagicLinkTokenCreate(BaseModel):
    """Request to generate a magic link — just the email address."""
    email: str


class MagicLinkTokenResponse(BaseModel):
    """Magic link token record — returned for admin/debug purposes."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    token: str
    email: str
    resend_email_id: uuid.UUID | None = None
    expires_at: datetime
    used: bool
    created_at: datetime | None = None
