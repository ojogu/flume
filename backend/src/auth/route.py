# ── Authentication routes ─────────────────────────────────────────────────────
# Google OAuth (/login → /callback), magic link passwordless login, token refresh, logout (token blacklisting), and /me profile endpoint.
# Thin controller: all business logic delegated to AuthService.

from fastapi import APIRouter, Depends, Query, Request

from src.auth.schema import (
    LoginRequest,
    LoginResponse,
    UserProfileResponse,
)
from src.auth.service import RefreshTokenBearer, auth_service
from src.core.dependency import get_current_user, get_user_service
from src.model.user import User
from src.service.user import UserService
from src.utils.log import get_logger
from src.utils.response import success

logger = get_logger(__name__)

auth_route = APIRouter(prefix="/auth", tags=["auth"])


@auth_route.post("/login")
async def login(
    body: LoginRequest,
    user_service: UserService = Depends(get_user_service),
):
    user = await auth_service.authenticate_user(
        email=body.email,
        password=body.password,
        user_service=user_service,
    )
    tokens = auth_service.create_token_pair(user)
    return success(
        data=LoginResponse(
            **tokens.model_dump(),
            user=UserProfileResponse(
                id=str(user.id),
                email=user.email,
                name=user.name,
                picture=user.picture,
                onboarded=user.onboarded,
                is_admin=user.is_admin,
            ),
        ).model_dump()
    )


@auth_route.get("/login")
async def oauth_login():
    from src.core.dependency import google_service

    url = google_service.login_with_google()
    return success(data={"url": url})


@auth_route.get("/callback")
async def oauth(
    request: Request,
    test: bool | None = Query(None),
    user_service: UserService = Depends(get_user_service),
):
    if test:
        logger.info("webhook is ready")
        return {"status": "ready"}

    logger.info(f"query_params; {dict(request.query_params)}")
    return await auth_service.handle_google_callback(
        request=request,
        user_service=user_service,
    )


@auth_route.get("/magic-link")
async def magic_link(
    email: str,
    user_service: UserService = Depends(get_user_service),
):
    await auth_service.request_magic_link(email=email, user_service=user_service)
    return success(
        message="If an account with that email exists, a magic link has been sent."
    )


@auth_route.get("/magic-link/verify")
async def magic_link_callback(
    token: str,
    user_service: UserService = Depends(get_user_service),
):
    return await auth_service.verify_magic_link_callback(
        token=token,
        user_service=user_service,
    )


@auth_route.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return success(
        data=UserProfileResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            picture=user.picture,
            onboarded=user.onboarded,
            is_admin=user.is_admin,
        ).model_dump()
    )


@auth_route.post("/logout", tags=["auth"])
async def logout(token_details: dict = Depends(RefreshTokenBearer())):
    """Logout endpoint - invalidates the refresh token by blacklisting it."""
    await auth_service.blacklist_refresh_token(jti=token_details["jti"])
    return success(message="Logout successful")


@auth_route.get("/refresh-token", tags=["auth"])
async def get_new_tokens(token_details: dict = Depends(RefreshTokenBearer())):
    tokens = await auth_service.rotate_refresh_tokens(token_details)
    return success(
        message="Refresh Token Successfully Generated",
        data=tokens.model_dump(),
    )
