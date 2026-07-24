from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import AccessTokenBearer
from src.auth.service import auth_service as auth_service_instance
from src.core.exception_base import Unauthorized
from src.model.api import ApiKey
from src.model.user import User
from src.service.api import ApiKeyService
from src.service.events import EventService
from src.service.google import GoogleAuthService
from src.service.jobs import JobService
from src.service.platform import PlatformService
from src.service.upload import UploadService
from src.service.user import UserService
from src.service.util import UtilService
from src.utils.db import get_session
from src.utils.log import get_logger

logger = get_logger(__name__)
google_service = GoogleAuthService()


def get_auth_service():
    """Return the singleton AuthService instance."""
    return auth_service_instance


def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)


def get_api_key_service(db: AsyncSession = Depends(get_session)):
    return ApiKeyService(db=db)


# Wires JobService per request — one DB session, one service instance
def get_job_service(db: AsyncSession = Depends(get_session)):
    return JobService(db=db)


# Wires UploadService per request — same pattern as get_job_service
def get_upload_service(db: AsyncSession = Depends(get_session)):
    return UploadService(db=db)


def get_event_service(db: AsyncSession = Depends(get_session)):
    return EventService(db=db)


def get_platform_service(db: AsyncSession = Depends(get_session)):
    return PlatformService(db=db)


def get_util_service(db: AsyncSession = Depends(get_session)):
    return UtilService(db=db)


# Chains three dependencies: JWT extraction → DB session → user lookup by user_id from token
async def get_current_user(
    user_details: dict = Depends(AccessTokenBearer()),
    user_service: UserService = Depends(get_user_service),
):
    logger.info(f"user details: {user_details}")
    user_id = user_details["user"]["user_id"]
    user = await user_service.get_user_by_id(user_id)
    return user


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_admin:
        raise Unauthorized("Admin access required")
    return user


# Alternative auth path for programmatic API access (no JWT, uses X-API-Key header)
async def get_api_key_from_header(
    request: Request,
    api_key_service: ApiKeyService = Depends(get_api_key_service),
) -> ApiKey:
    raw_key = request.headers.get("X-API-Key")
    if not raw_key:
        raise Unauthorized("Missing X-API-Key header")

    api_key = await api_key_service.verify_key(raw_key)
    if not api_key:
        raise Unauthorized("Invalid or expired API key")

    logger.info(f"API key authenticated: {api_key.key_prefix}")
    return api_key
