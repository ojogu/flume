from pathlib import Path

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.google import GoogleAuthService
from src.service.user import UserService
from src.utils.config import config
from src.utils.db import get_session


CLIENT_SECRET_PATH = (
    Path(__file__).resolve().parent.parent.parent / "client_secret.json"
)
google_service = GoogleAuthService(
    client_secret_file=str(CLIENT_SECRET_PATH),
    redirect_uri=config.redirect_url,
)


def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)
