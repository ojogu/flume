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
        """Create a job in pending state with the validated pipeline spec."""
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
            logger.info(
                f"Job {job.id} created for API key {api_key_id} — "
                f"source={source_uri}, "
                f"type={source_type}, "
                f"steps={len(pipeline_spec) if pipeline_spec else 0}"
            )
            return job
        except Exception as e:
            await self.db.rollback()
            logger.error(
                f"Error creating job for API key {api_key_id} — "
                f"source={source_uri}: {e}"
            )
            raise DatabaseError()
