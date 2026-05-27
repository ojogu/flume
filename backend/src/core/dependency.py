from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.utils.db import get_session
from src.service.user import UserService


def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)
