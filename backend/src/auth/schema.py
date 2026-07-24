from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Email + password login payload."""

    email: EmailStr
    password: str


class MagicLinkRequest(BaseModel):
    """Magic link email request — used for query param validation."""

    email: EmailStr


class UserProfileResponse(BaseModel):
    """Thin user profile for auth responses (login, /me, OAuth callback)."""

    id: str
    email: str
    name: str | None = None
    picture: str | None = None
    onboarded: bool = False
    is_admin: bool = False


class TokenPairResponse(BaseModel):
    """JWT access + refresh token pair."""

    access_token: str
    refresh_token: str


class LoginResponse(TokenPairResponse):
    """Login response — tokens plus user profile."""

    user: UserProfileResponse


class OAuthCallbackParams(BaseModel):
    """Params passed to frontend via redirect after OAuth callback."""

    access_token: str
    refresh_token: str
    onboarded: str
