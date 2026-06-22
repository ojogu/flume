import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.model.job import Job, JobStatus
from src.core.exception_base import DatabaseError
from src.utils.log import get_logger

logger = get_logger(__name__)


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(
        self,
        api_key_id: uuid.UUID,
        source_uri: str,
        source_type: str,
        pipeline_spec: list[dict] | None = None,
    ) -> Job:
        job = Job(
            api_key_id=api_key_id,
            source_uri=source_uri,
            source_type=source_type,
            status=JobStatus.PENDING.value,
            pipeline_steps=pipeline_spec,
        )
        self.db.add(job)
        try:
            await self.db.flush()
            await self.db.refresh(job)
            await self.db.commit()
            logger.info(f"Job {job.id} created for API key {api_key_id}")
            return job
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating job: {e}")
            raise DatabaseError()
