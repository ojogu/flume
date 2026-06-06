from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.google import GoogleAuthService
from src.service.user import UserService
from src.utils.config import config
from src.utils.db import get_session


google_service = GoogleAuthService()


def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)
