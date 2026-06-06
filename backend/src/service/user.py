from typing import Optional
import uuid
from src.schema import UpdateUser, CreateUser
from src.model.user import User 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from src.utils.exception import (
    AlreadyExistsError,
    DatabaseError
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
        result = await self.db.execute(select(User).where(User.unique_id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_whatsapp_phone_number(self, whatsapp_phone_number: str) -> Optional[User]:
        """Fetch a user by their email address."""
        result = await self.db.execute(
            select(User).where(User.whatsapp_phone_number == whatsapp_phone_number)
        )
        logger.info(f"user_found:")
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
                raise AlreadyExistsError(
                    f"Email '{validated_data.email}' is already registered (concurrent request?)."
                )
            else:
                logger.error(f"Error creating user: {e}")
                raise DatabaseError(f"Database integrity error: {e}") from e
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            await self.db.rollback()
            raise DatabaseError(f"Could not create user: {e}") from e

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
            raise DatabaseError(f"Could not update user: {e}") from e