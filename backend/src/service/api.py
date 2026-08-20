import datetime
import secrets
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exception_base import DatabaseError, NotFoundError
from src.model.api import ApiKey, ApiKeyStatus
from src.model.job import Job
from src.model.user import User
from src.utils.config import config
from src.utils.crypto import hash_str
from src.utils.log import get_logger

logger = get_logger(__name__)

WEB_SESSION_KEY_PREFIX = "web"
WEB_SESSION_DAILY_LIMIT = 5


# API key lifecycle — generate (flm_ prefix + SHA-256 hash), verify, revoke
class ApiKeyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _generate_key() -> tuple[str, str, str]:
        secret = secrets.token_urlsafe(32)
        # flm_ prefix enables secret scanning tools to detect leaked keys
        full_key = f"{config.api_key_prefix}_{secret}"
        # First 8 chars shown in UI so users can identify keys without exposing the full key
        key_prefix = f"{config.api_key_prefix}_{secret[:8]}"
        # One-way SHA-256 hash: we can verify keys but can never recover the raw value
        key_hash = hash_str(full_key)
        return full_key, key_hash, key_prefix

    async def create_key(
        self, user_id: uuid.UUID, name: str, expires_at: datetime.datetime | None = None
    ) -> tuple[ApiKey, str]:
        full_key, key_hash, key_prefix = self._generate_key()

        api_key = ApiKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            status=ApiKeyStatus.ACTIVE.value,
            expires_at=expires_at,
        )
        self.db.add(api_key)
        try:
            await self.db.flush()
            await self.db.refresh(api_key)
            await self.db.commit()
            logger.info(f"API key created for user {user_id}")
            return api_key, full_key
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating API key: {e}")
            logger.exception("Error creating API key")
            raise DatabaseError() 

    async def get_keys(self, user_id: uuid.UUID) -> list[ApiKey]:
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_key(self, key_id: uuid.UUID, user_id: uuid.UUID) -> ApiKey:
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user_id)
        )
        api_key = result.scalar_one_or_none()
        if not api_key:
            raise NotFoundError("API key not found")
        return api_key

    async def update_key(
        self, key_id: uuid.UUID, user_id: uuid.UUID, data: dict
    ) -> ApiKey:
        api_key = await self.get_key(key_id, user_id)

        for key, value in data.items():
            if hasattr(api_key, key):
                setattr(api_key, key, value)

        try:
            await self.db.flush()
            await self.db.refresh(api_key)
            await self.db.commit()
            logger.info(f"API key {key_id} updated")
            return api_key
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating API key: {e}")
            logger.exception("Error updating API key")
            raise DatabaseError()

    async def revoke_key(self, key_id: uuid.UUID, user_id: uuid.UUID) -> ApiKey:
        api_key = await self.get_key(key_id, user_id)
        api_key.status = ApiKeyStatus.REVOKED.value
        api_key.deleted_at = datetime.datetime.now(datetime.timezone.utc)

        try:
            await self.db.flush()
            await self.db.refresh(api_key)
            await self.db.commit()
            logger.info(f"API key {key_id} revoked")
            return api_key
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error revoking API key: {e}")
            logger.exception("Error revoking API key")
            raise DatabaseError()

    # Hash the raw key, look up by hash (constant-ish time), check expiry, touch last_used_at
    async def verify_key(self, raw_key: str) -> ApiKey | None:
        computed_hash = hash_str(raw_key)
        result = await self.db.execute(
            select(ApiKey).where(
                ApiKey.key_hash == computed_hash,
                ApiKey.status == ApiKeyStatus.ACTIVE.value,
            )
        )
        api_key = result.scalar_one_or_none()
        if not api_key:
            return None

        if api_key.expires_at and api_key.expires_at < datetime.datetime.now(datetime.timezone.utc):
            return None

        # Side-effect update: tracks last usage for audit/expiry; not critical if it fails
        api_key.last_used_at = datetime.datetime.now(datetime.timezone.utc)
        try:
            await self.db.flush()
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating last_used_at: {e}")
            logger.exception("Error updating last_used_at")
            raise DatabaseError()

        return api_key

    # ── Web session keys ────────────────────────────────────────────────────────

    @staticmethod
    def _generate_session_key() -> tuple[str, str, str]:
        secret = secrets.token_urlsafe(32)
        full_key = f"{WEB_SESSION_KEY_PREFIX}_{secret}"
        key_prefix = f"{WEB_SESSION_KEY_PREFIX}_{secret[:8]}"
        key_hash = hash_str(full_key)
        return full_key, key_hash, key_prefix

    async def _get_or_create_system_user(self) -> User:
        """Find or create a system user for anonymous session keys."""
        result = await self.db.execute(
            select(User).where(User.email == "system@flume.ojogulabs.xyz")
        )
        user = result.scalar_one_or_none()
        if user:
            return user

        user = User(
            email="system@flume.ojogulabs.xyz",
            email_verified=False,
            oauth_verified=False,
            onboarded=False,
            is_active=True,
            auth_provider="system",
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        await self.db.commit()
        logger.info("System user created for anonymous sessions")
        return user

    async def create_session_key(self) -> tuple[ApiKey, str]:
        """Create a short-lived web session API key (24h expiry, 5 jobs/day)."""
        system_user = await self._get_or_create_system_user()
        full_key, key_hash, key_prefix = self._generate_session_key()
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)

        api_key = ApiKey(
            user_id=system_user.id,
            name="web-session",
            key_hash=key_hash,
            key_prefix=key_prefix,
            status=ApiKeyStatus.ACTIVE.value,
            expires_at=expires_at,
        )
        self.db.add(api_key)
        try:
            await self.db.flush()
            await self.db.refresh(api_key)
            await self.db.commit()
            logger.info(f"Session key created: {key_prefix}")
            return api_key, full_key
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating session key: {e}")
            raise DatabaseError()

    async def count_jobs_last_24h(self, api_key_id: uuid.UUID) -> int:
        """Count jobs created by this API key in the last 24 hours."""
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
        result = await self.db.execute(
            select(func.count()).where(
                Job.api_key_id == api_key_id,
                Job.created_at >= cutoff,
            )
        )
        return result.scalar() or 0
