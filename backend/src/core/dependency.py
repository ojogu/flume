from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.google import GoogleAuthService
from src.service.user import UserService
from src.service.api import ApiKeyService
from src.service.jobs import JobService
from src.model.api import ApiKey
from src.core.exception_base import Unauthorized
from src.utils.config import config
from src.utils.db import get_session
from src.utils.log import get_logger
from src.auth.service import AccessTokenBearer


logger = get_logger(__name__)
google_service = GoogleAuthService()


def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)

def get_api_key_service(db: AsyncSession = Depends(get_session)):
    return ApiKeyService(db=db)

def get_job_service(db: AsyncSession = Depends(get_session)):
    return JobService(db=db)

# Chains three dependencies: JWT extraction → DB session → user lookup by user_id from token
async def get_current_user(
    user_details: dict = Depends(AccessTokenBearer()),
    user_service: UserService = Depends(get_user_service),
):
    logger.info(f"user details: {user_details}")
    user_id = user_details["user"]["user_id"]
    user = await user_service.get_user_by_id(user_id)
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