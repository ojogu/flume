from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from src.service.user import UserService
from src.core.dependency import get_current_user, get_user_service, google_service
from src.model.user import User
from src.core.email_service import send_magic_link_email
from src.utils.response import success
from src.utils.log import get_logger

from src.auth.service import RefreshTokenBearer
from src.core.exception_base import InvalidToken
from src.utils.config import config
from src.utils.redis import key_exist, set_cache
from .service import auth_service

logger = get_logger(__name__)

auth_route = APIRouter(prefix="/auth")

#google oauth
@auth_route.get("/login")
async def oauth_login():
    url = google_service.login_with_google()
    return success(data={"url": url})


@auth_route.get("/callback")
async def oauth(request: Request, user_service: UserService = Depends(get_user_service)):
    params = dict(request.query_params)
    logger.info(f"query_params; {params}")  
    data = google_service.handle_callback(request)
    user_data = google_service.verify_id(data["id_token"])
    user_info = {
        "google_id": user_data["sub"],
        "refresh_token": data["refresh_token"],
        "access_token": data["access_token"],
        "email": user_data["email"],
        "auth_provider": "google",
        "is_active": True,
        "oauth_verified": True,
        "onboarded": True,
        "email_verified": user_data["email_verified"],
        "name": user_data["name"],
        "picture": user_data.get("picture"),
        "first_name": user_data.get("given_name"),
        "last_name": user_data.get("family_name"),
    }
    logger.info(f"user_data: {user_info}")

    existing_user = await user_service.get_user_by_email(email=user_info["email"])

    if existing_user and existing_user.email == user_info["email"]:
        user = await user_service.update_user(
            email=existing_user.email, update_data=user_info
        )
        logger.info(f"user updated: {user}")
    elif not existing_user:
        user = await user_service.create_user(**user_info)
        logger.info(f"new_user: {user}")
    else:
        logger.warning("Email mismatch for existing user.")
        return RedirectResponse(url=f"{config.frontend_url}/callback?error=email_mismatch", status_code=302)

    payload = {"user_id": str(user.id), "email": user.email}
    access = auth_service.create_access_token(user_data=payload)
    refresh = auth_service.create_access_token(
        user_data=payload, refresh=True, expiry=timedelta(days=config.refresh_token_expiry),
    )
    params = {
        "access-token": access,
        "refresh-token": refresh,
        "onboarded": str(user.onboarded).lower(),
    }
    logger.info(f"access: {access}, refresh: {refresh}")
    return RedirectResponse(
        url=f"{config.frontend_url}/callback?{urlencode(params)}",
        status_code=302,
    )


#magic link
@auth_route.get("/magic-link")
async def magic_link(email: str, user_service: UserService = Depends(get_user_service)):
    token = await user_service.create_magic_link_token(email=email)
    send_magic_link_email(to_email=email, token=token)
    return success(message="If an account with that email exists, a magic link has been sent.")

@auth_route.get("/magic-link/verify")
async def magic_link_callback(token: str, user_service: UserService = Depends(get_user_service)):
    user = await user_service.verify_magic_link_and_login(token=token)
    if not user:
        return RedirectResponse(
            url=f"{config.frontend_url}/callback?error=invalid_or_expired_token",
            status_code=302,
        )

    payload = {"user_id": str(user.id), "email": user.email}
    access = auth_service.create_access_token(user_data=payload)
    refresh = auth_service.create_access_token(
        user_data=payload, refresh=True, expiry=timedelta(days=config.refresh_token_expiry),
    )
    params = {
        "access-token": access,
        "refresh-token": refresh,
        "onboarded": str(user.onboarded).lower(),
    }
    logger.info(f"Magic link verified for user {user.email}, redirecting with tokens.")
    logger.info(f"access: {access}, refresh: {refresh}")
    return RedirectResponse(
        url=f"{config.frontend_url}/callback?{urlencode(params)}",
        status_code=302,
    )

@auth_route.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return success(data={
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "onboarded": user.onboarded,
    })

@auth_route.post("/logout", tags=["auth"])
async def logout(token_details: dict = Depends(RefreshTokenBearer())):
    """
    Logout endpoint - invalidates the refresh token by blacklisting it.
    Uses the same blacklisting logic as token refresh.
    """
    try:
        jti = token_details["jti"]
        if await key_exist(key=str(jti)):
            raise InvalidToken("Refresh token has been revoked")

        await set_cache(key=str(jti), data="", ttl=config.refresh_token_expiry)
        logger.info(f"User logged out, token {jti} has been revoked")

        return success(
            message="Logout successful",
        )
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise


@auth_route.get("/refresh-token", tags=["auth"])
async def get_new_tokens_token(token_details: dict = Depends(RefreshTokenBearer())):
    # Check if refresh token is not blacklisted (additional check)
    jti = token_details["jti"]
    if await key_exist(key=str(jti)):
        raise InvalidToken("Refresh token has been revoked")

    # Make sure it's not expired
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        access_token = auth_service.create_access_token(user_data=token_details["user"])
        refresh_token = auth_service.create_access_token(
            user_data=token_details["user"], refresh=True
        )

        # Blacklist the old refresh token
        await set_cache(key=str(jti), data="", ttl=config.refresh_token_expiry)
        logger.info(f"{jti} has been revoked")
        tokens = {"access_token": access_token, "refresh_token": refresh_token}

        return success(
            message="Refresh Token Successfully Generated",
            data=tokens,
        )