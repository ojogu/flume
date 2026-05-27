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

    async def create_user(self, **user_data: CreateUser) -> User:
        """Create a new user."""
        # Check if phone_number already exists
        validated_data = CreateUser(**user_data)
        logger.info(f"validated data:{validated_data.whatsapp_phone_number}")
        existing_user = await self.get_user_by_whatsapp_phone_number(validated_data.whatsapp_phone_number)
        if existing_user:
            logger.warning(F"user already exists: {existing_user}")
            return existing_user
    
        new_user = User(
            **validated_data.model_dump()
        )
        logger.info(f"Creating new user with WhatsApp phone number: {new_user.whatsapp_phone_number}, ID: {new_user.id}")
        self.db.add(new_user)
        try:
            await (
                self.db.flush()
            )  # Use flush to get potential errors before commit
            await self.db.refresh(
                new_user
            )  # Refresh to get DB defaults like ID, created_at
            await self.db.commit()
            
            return new_user
        
        except IntegrityError as e:
            await self.db.rollback()
            # Check if it's a unique constraint violation (though checked above, good practice)
            if "unique constraint" in str(e).lower():
                logger.error(f"an error exist: {e}")
                raise AlreadyExistsError(
                    f"Email '{user_data.whatsapp_phone_number}' is already registered (concurrent request?)."
                )
            else:
                # Handle other potential integrity errors
                logger.error(f"Error creating user: {e}")
                raise DatabaseError(f"Database integrity error: {e}") from e
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            await self.db.rollback()
            raise DatabaseError(f"Could not create user: {e}") from e