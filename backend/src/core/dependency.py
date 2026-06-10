from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.google import GoogleAuthService
from src.service.user import UserService
from src.utils.config import config
from src.utils.db import get_session
from src.utils.log import get_logger
from src.auth.service import AccessTokenBearer


logger = get_logger(__name__)
google_service = GoogleAuthService()


def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)

async def get_current_user(
    user_details: dict = Depends(AccessTokenBearer()),
    user_service: UserService = Depends(get_user_service),
):
    logger.info(f"user details: {user_details}")
    user_id = user_details["user"]["user_id"]
    user = await user_service.get_user_by_id(user_id)
    return user