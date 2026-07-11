import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.platform import Platform
from src.core.exception_base import NotFoundError, AlreadyExistsError, DatabaseError
from src.utils.log import get_logger

logger = get_logger(__name__)


# ── Platform service ──────────────────────────────────────────────────────────
# CRUD operations for the supported platforms catalog.
# All queries exclude soft-deleted records. The slug-based lookup is used
# by the orchestrator to validate platforms before job processing.

class PlatformService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── CRUD ──────────────────────────────────────────────────────────────────

    async def create_platform(self, data: dict) -> Platform:
        """Create a new platform. Raises AlreadyExistsError if slug is taken."""
        existing = await self.get_platform_by_slug(data["slug"])
        if existing:
            raise AlreadyExistsError(f"Platform with slug '{data['slug']}' already exists")

        platform = Platform(**data)
        self.db.add(platform)
        try:
            await self.db.flush()
            await self.db.refresh(platform)
            await self.db.commit()
            logger.info(f"Platform created: {platform.slug} ({platform.name})")
            return platform
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating platform: {e}")
            raise DatabaseError()

    async def get_platforms(self, active_only: bool = False) -> list[Platform]:
        """List all platforms ordered by sort_order. Optionally filter by is_active."""
        query = select(Platform).order_by(Platform.sort_order.asc())
        if active_only:
            query = query.where(Platform.is_active.is_(True))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_platform(self, platform_id: uuid.UUID) -> Platform:
        """Fetch a platform by UUID. Raises NotFoundError if missing."""
        result = await self.db.execute(
            select(Platform).where(Platform.id == platform_id)
        )
        platform = result.scalar_one_or_none()
        if not platform:
            raise NotFoundError(f"Platform {platform_id} not found")
        return platform

    async def get_platform_by_slug(self, slug: str) -> Platform | None:
        """Fetch a platform by slug. Returns None if not found (no exception).

        Used by the orchestrator to validate platforms before job processing.
        """
        result = await self.db.execute(
            select(Platform).where(Platform.slug == slug)
        )
        return result.scalar_one_or_none()

    async def update_platform(self, platform_id: uuid.UUID, data: dict) -> Platform:
        """Partially update a platform. Raises NotFoundError if missing."""
        platform = await self.get_platform(platform_id)

        for key, value in data.items():
            if hasattr(platform, key):
                setattr(platform, key, value)

        try:
            await self.db.flush()
            await self.db.refresh(platform)
            await self.db.commit()
            logger.info(f"Platform updated: {platform.slug}")
            return platform
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating platform {platform_id}: {e}")
            raise DatabaseError() from e

    async def delete_platform(self, platform_id: uuid.UUID) -> None:
        """Soft-delete a platform by setting deleted_at. Raises NotFoundError if missing."""
        platform = await self.get_platform(platform_id)
        platform.deleted_at = datetime.datetime.now(datetime.timezone.utc)

        try:
            await self.db.flush()
            await self.db.commit()
            logger.info(f"Platform deleted: {platform.slug}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting platform {platform_id}: {e}")
            raise DatabaseError() from e
