# ── JWT token lifecycle ───────────────────────────────────────────────────────
# Creates and decodes access/refresh JWT tokens. AccessTokenBearer and
# RefreshTokenBearer are FastAPI dependencies that enforce token type per route.

from datetime import timedelta, datetime, timezone
import secrets
from fastapi import Request
import bcrypt
import jwt
import uuid
from src.utils.config import config
from src.utils.crypto import encrypt_token, decrypt_token
from src.core.exception_base import InvalidToken, TokenExpired
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from src.utils.log import get_logger


logger = get_logger(__name__)




class AuthService:
    """this class handles in-app authentication (jwt access token, refresh token)"""

    def __init__(self):
        pass

    def create_access_token(
        self, user_data: dict, expiry: timedelta = None, refresh: bool = False
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
            raise TokenExpired("token has expired")

        except jwt.InvalidSignatureError as e:
            logger.error(f"invalid token signature: {e}", exc_info=True)
            raise TokenExpired("invalid token signature")

        except jwt.PyJWTError as e:
            logger.error(f"error decoding token: {e}", exc_info=True)
            raise TokenExpired("error decoding token")

    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())




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