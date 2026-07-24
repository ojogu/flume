# ── JWT token lifecycle ───────────────────────────────────────────────────────
# Creates and decodes access/refresh JWT tokens. AccessTokenBearer and
# RefreshTokenBearer are FastAPI dependencies that enforce token type per route.

import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import bcrypt
import jwt
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from src.auth.schema import TokenPairResponse
from src.core.exception_base import InvalidEmailPassword, InvalidToken, TokenExpired
from src.model.user import User
from src.schema.user import CreateUser
from src.utils.config import config
from src.utils.log import get_logger

logger = get_logger(__name__)


class AuthService:
    """JWT token lifecycle + auth flow orchestration.

    Handles token creation/decoding, password hashing, and orchestrates
    login, OAuth, magic link, logout, and token refresh flows.
    """

    def __init__(self):
        pass

    def create_access_token(
        self, user_data: dict, expiry: timedelta | None = None, refresh: bool = False
    ):
        try:
            payload = {}
            payload["user"] = user_data
            to_expire = (
                expiry
                if expiry is not None
                else timedelta(seconds=config.access_token_expiry)
            )
            payload["exp"] = datetime.now(timezone.utc) + to_expire
            # jti (JWT ID) uniquely identifies this token — used for blacklisting in Redis on logout
            payload["jti"] = str(uuid.uuid4())
            # Refresh flag avoids needing a DB lookup to distinguish access vs refresh tokens
            payload["refresh"] = refresh

            token = jwt.encode(
                payload=payload, key=config.jwt_secret_key, algorithm=config.jwt_algo
            )
            logger.info(f"access token created for user: {user_data.get('id')}")
            return token
        except Exception as e:
            logger.error(
                f"error creating access token for user {user_data.get('id')}: {e}",
                exc_info=True,
            )
            raise

    def decode_token(self, token: str) -> dict:
        try:
            token_data = jwt.decode(
                jwt=token, key=config.jwt_secret_key, algorithms=[config.jwt_algo]
            )
            logger.info(
                f"token decoded successfully for user: {token_data.get('user').get('id')}"
            )
            return token_data
        except jwt.ExpiredSignatureError as e:
            logger.error(f"token expired for user: {e}", exc_info=True)
            raise TokenExpired("token has expired")  # noqa: B904

        except jwt.InvalidSignatureError as e:
            logger.error(f"invalid token signature: {e}", exc_info=True)
            raise TokenExpired("invalid token signature")  # noqa: B904

        except jwt.PyJWTError as e:
            logger.error(f"error decoding token: {e}", exc_info=True)
            raise TokenExpired("error decoding token")  # noqa: B904

    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def create_token_pair(self, user) -> TokenPairResponse:
        """Create access + refresh token pair for a user. Single source of truth."""
        payload = {"user_id": str(user.id), "email": user.email}
        access = self.create_access_token(user_data=payload)
        refresh = self.create_access_token(
            user_data=payload,
            refresh=True,
            expiry=timedelta(days=config.refresh_token_expiry),
        )
        return TokenPairResponse(access_token=access, refresh_token=refresh)

    async def authenticate_user(self, email: str, password: str, user_service) -> User:
        """Lookup user by email, verify password, check active status."""
        user = await user_service.get_user_by_email(email=email)
        if not user or not user.password_hash:
            raise InvalidEmailPassword("Invalid email or password")

        if not self.verify_password(password, user.password_hash):
            raise InvalidEmailPassword("Invalid email or password")

        if not user.is_active:
            raise InvalidEmailPassword("Account is not active")

        return user

    async def handle_google_callback(self, request, user_service):
        """Exchange Google auth code, upsert user, return redirect with tokens."""
        from src.core.dependency import google_service

        data = google_service.handle_callback(request)
        user_data = google_service.verify_id(data["id_token"])
        user_info = CreateUser(
            google_id=user_data["sub"],
            refresh_token=data["refresh_token"],
            access_token=data["access_token"],
            email=user_data["email"],
            auth_provider="google",
            is_active=True,
            oauth_verified=True,
            onboarded=True,
            email_verified=user_data["email_verified"],
            name=user_data["name"],
            picture=user_data.get("picture"),
            first_name=user_data.get("given_name"),
            last_name=user_data.get("family_name"),
        )
        logger.info(f"user_data: {user_info}")

        existing_user = await user_service.get_user_by_email(email=user_info.email)

        if existing_user and existing_user.email == user_info.email:
            user = await user_service.update_user(
                email=existing_user.email, update_data=user_info.model_dump()
            )
            logger.info(f"user updated: {user}")
        elif not existing_user:
            user = await user_service.create_user(**user_info.model_dump())
            logger.info(f"new_user: {user}")
        else:
            logger.warning("Email mismatch for existing user.")
            return RedirectResponse(
                url=f"{config.frontend_url}/callback?error=email_mismatch",
                status_code=302,
            )

        tokens = self.create_token_pair(user)
        params = {
            "access-token": tokens.access_token,
            "refresh-token": tokens.refresh_token,
            "onboarded": str(user.onboarded).lower(),
        }
        logger.info(f"OAuth login successful for {user.email}")
        return RedirectResponse(
            url=f"{config.frontend_url}/callback?{urlencode(params)}",
            status_code=302,
        )

    async def request_magic_link(self, email: str, user_service) -> None:
        """Create magic link token and enqueue email."""
        from src.core.email_service import send_magic_link_email

        token = await user_service.create_magic_link_token(email=email)
        send_magic_link_email(to_email=email, token=token)

    async def verify_magic_link_callback(self, token: str, user_service):
        """Verify magic link token, return redirect with tokens or error."""
        user = await user_service.verify_magic_link_and_login(token=token)
        if not user:
            return RedirectResponse(
                url=f"{config.frontend_url}/callback?error=invalid_or_expired_token",
                status_code=302,
            )

        tokens = self.create_token_pair(user)
        params = {
            "access-token": tokens.access_token,
            "refresh-token": tokens.refresh_token,
            "onboarded": str(user.onboarded).lower(),
        }
        logger.info(f"Magic link verified for user {user.email}")
        return RedirectResponse(
            url=f"{config.frontend_url}/callback?{urlencode(params)}",
            status_code=302,
        )

    async def blacklist_refresh_token(self, jti: str) -> None:
        """Blacklist a refresh token in Redis to prevent reuse."""
        from src.utils.redis import key_exist, set_cache

        if await key_exist(key=str(jti)):
            raise InvalidToken("Refresh token has been revoked")

        await set_cache(key=str(jti), data="", ttl=config.refresh_token_expiry)
        logger.info(f"Token {jti} blacklisted")

    async def rotate_refresh_tokens(self, token_details: dict) -> TokenPairResponse:
        """Validate refresh token, issue new pair, blacklist old token."""
        from src.utils.redis import key_exist, set_cache

        jti = token_details["jti"]
        if await key_exist(key=str(jti)):
            raise InvalidToken("Refresh token has been revoked")

        expiry_timestamp = token_details["exp"]
        if datetime.fromtimestamp(expiry_timestamp, tz=timezone.utc) <= datetime.now(
            timezone.utc
        ):
            raise InvalidToken("Refresh token has expired")

        payload = token_details["user"]
        access = self.create_access_token(user_data=payload)
        refresh = self.create_access_token(
            user_data=payload,
            refresh=True,
            expiry=timedelta(days=config.refresh_token_expiry),
        )

        await set_cache(key=str(jti), data="", ttl=config.refresh_token_expiry)
        logger.info(f"Token {jti} rotated and old token blacklisted")
        return TokenPairResponse(access_token=access, refresh_token=refresh)


auth_service = AuthService()


class TokenService(HTTPBearer):
    """
    Custom HTTP Bearer authentication class for validating JWT access tokens.

    This class extends FastAPI's HTTPBearer to:
    - Extract Bearer tokens from the Authorization header.
    - Decode and validate the token using an external `auth_service`.
    - Ensure the token is not a refresh token.
    - Raise a custom `InvalidToken` exception if the token is invalid or missing required data.

    Usage:
        Use as a dependency in FastAPI routes to protect endpoints and extract token data.

    Example:
        access_token_service = AccessTokenService()

        @router.get("/secure-endpoint")
        async def secure_endpoint(user_data: dict = Depends(access_token_service)):
            return {"user": user_data}

    Args:
        auto_error (bool): Whether to automatically raise an HTTPException
            if authentication fails. Defaults to True.

    Raises:
        InvalidToken: If the token is missing, invalid, expired, or is a refresh token.
    """

    # auto_error=False means we handle missing credentials ourselves (clearer error message)
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        # Extract → validate → decode → verify flow
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if credentials is None:
            raise InvalidToken("Missing authentication token")

        if not credentials or not credentials.scheme.lower() == "bearer":
            raise InvalidToken("Invalid authentication scheme")

        token = credentials.credentials

        if not self.token_valid(token):
            raise InvalidToken("Invalid or expired token")

        token_data = auth_service.decode_token(token)

        # Template Method: subclasses (AccessTokenBearer, RefreshTokenBearer) define
        # what token type they accept by overriding verify_token_data
        self.verify_token_data(token_data)

        if token_data is None:
            raise InvalidToken("No data found in access token")

        return token_data

    def token_valid(self, token: str) -> bool:
        try:
            token_data = auth_service.decode_token(token)
            return token_data is not None
        except Exception:
            return False

    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Overide in the child classes ")


class AccessTokenBearer(TokenService):
    def verify_token_data(self, token_data: dict):
        """
        Verifies that the token data is a valid access token.

        Args:
            token_data (dict): The decoded token data.

        Raises:
            InvalidToken: If the token is a refresh token.
        """
        # Rejects refresh tokens hitting access-token-protected endpoints
        if token_data and token_data.get("refresh", False):
            raise InvalidToken(
                "Please provide a valid access token, not a refresh token"
            )


class RefreshTokenBearer(TokenService):
    def verify_token_data(self, token_data: dict):
        """
        Verifies that the token data is a valid refresh token.

        Args:
            token_data (dict): The decoded token data.

        Raises:
            InvalidToken: If the token is an access token.
        """
        # Rejects access tokens hitting refresh-token-protected endpoints
        if token_data and not token_data.get("refresh", False):
            raise InvalidToken("Please provide a valid refresh token")
