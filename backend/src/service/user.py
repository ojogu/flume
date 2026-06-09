import datetime
import secrets
from typing import Optional
import uuid
from src.schema import UpdateUser, CreateUser
from src.model import User, MagicLinkToken
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from src.utils.exception import (
    AlreadyExistsError,
    DatabaseError,
    ServerError,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


from src.utils.log import get_logger

logger = get_logger(__name__)


class UserService:
    """Service layer for user-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a user by their UUID."""
        if not isinstance(user_id, uuid.UUID):
            user_id = uuid.UUID(user_id, version=4)
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, **user_data) -> User:
        """Create a new user."""
        validated_data = CreateUser(**user_data)
        logger.info(f"validated data: {validated_data}")

        new_user = User(**validated_data.model_dump())
        logger.info(f"Creating new user: {new_user.email}, ID: {new_user.id}")
        self.db.add(new_user)
        try:
            await self.db.flush()
            await self.db.refresh(new_user)
            await self.db.commit()
            return new_user
        except IntegrityError as e:
            await self.db.rollback()
            if "unique constraint" in str(e).lower():
                logger.error(f"an error exist: {e}")
                raise AlreadyExistsError()
            else:
                logger.error(f"Error creating user: {e}")
                raise DatabaseError() from e
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            await self.db.rollback()
            raise DatabaseError() from e

    async def update_user(self, email: str, update_data: dict) -> Optional[User]:
        """Update a user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()
        if not user:
            return None

        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        try:
            await self.db.flush()
            await self.db.refresh(user)
            await self.db.commit()
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error updating user: {e}")
            raise DatabaseError() from e
    

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(48)

    async def create_magic_link_token(self, email):
        token = self.generate_token()
        expired_time = datetime.utcnow() + datetime.timedelta(minutes=15)
        #check if email exist and log
        email_exists = await self.get_user_by_email(email=email)
        if not email_exists:
            logger.warning(f"Magic link requested for non-existent email: {email}")
        #store tokens and metadata
        new_token = MagicLinkToken(
            email=email, 
            token=token,
            expires_at=expired_time
            )
        self.db.add(new_token)
        try:
            await self.db.flush()
            await self.db.refresh(new_token)
            await self.db.commit()
            logger.info(f"Magic link token created for email: {email}")
            return token
        except Exception as e:
            logger.error(f"Error creating magic link token: {e}")
            raise ServerError()


    async def verify_magic_link_token(self, token: str) -> Optional[str]:
        result = await self.db.execute(
            select(MagicLinkToken).where(
                and_(
                    MagicLinkToken.token == token,
                    MagicLinkToken.used == False,
                    MagicLinkToken.expires_at > datetime.utcnow()
                )
            )
        )
        token_record = result.scalar_one_or_none()
        if not token_record:
            logger.warning(f"Invalid or expired magic link token: {token}")
            return None

        # Mark the token as used
        token_record.used = True
        try:
            await self.db.flush()
            await self.db.refresh(token_record)
            await self.db.commit()
            logger.info(f"Magic link token verified for email: {token_record.email}")
            return token_record.email
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error verifying magic link token: {e}")
            raise ServerError()

    async def verify_magic_link_and_login(self, token: str) -> Optional[User]:
        email = await self.verify_magic_link_token(token)
        if not email:
            return None

        user = await self.get_user_by_email(email)
        if user:
            user = await self.update_user(
                email=email,
                update_data={"email_verified": True, "is_active": True},
            )
            logger.info(f"Existing user logged in via magic link: {email}")
        else:
            user = await self.create_user(
                email=email,
                auth_provider="magic_link",
                email_verified=True,
                is_active=True,
            )
            logger.info(f"New user created via magic link: {email}")

        return user

    