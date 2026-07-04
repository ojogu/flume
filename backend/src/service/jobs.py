import uuid
from datetime import datetime, timezone


from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.job import Job, JobStatus, TERMINAL_JOB_STATUSES, JobStep, StepStatus
from src.core.exception_base import DatabaseError, NotFoundError
from src.utils.log import get_logger

logger = get_logger(__name__)


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Job CRUD ───────────────────────────────────────────────────────────────

    async def get_job(self, job_id: uuid.UUID) -> Job | None:
        """Fetch a job by its UUID."""
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def create_job(
        self,
        api_key_id: uuid.UUID,
        source_uri: str,
        source_type: str,
        pipeline_spec: list[dict] | None = None,
        outputs: list[dict] | None = None,
        parent_job_id: uuid.UUID | None = None,
    ) -> Job:
        """Create a job in pending state with the validated pipeline spec."""
        job = Job(
            api_key_id=api_key_id,
            source_uri=source_uri,
            source_type=source_type,
            status=JobStatus.PENDING.value,
            pipeline_steps=pipeline_spec,
            outputs=outputs,
            parent_job_id=parent_job_id,
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
                f"steps={len(pipeline_spec) if pipeline_spec else 0}, "
                f"outputs={len(outputs) if outputs else 0}"
            )
            return job
        except Exception as e:
            await self.db.rollback()
            logger.error(
                f"Error creating job for API key {api_key_id} — "
                f"source={source_uri}: {e}"
            )
            raise DatabaseError()

    # ── Status transitions ─────────────────────────────────────────────────────

    async def update_status(
        self,
        job_id: uuid.UUID,
        status: JobStatus,
        error: str | None = None,
    ) -> None:
        """Transition a job to a new status.

        Sets ``completed_at`` automatically when the target is a terminal state.
        """
        job = await self.get_job(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} not found")

        job.status = status.value

        if status in TERMINAL_JOB_STATUSES:
            job.completed_at = datetime.now(timezone.utc)

        if error:
            job.error = error
            logger.error(f"Job {job_id} failed: {error}")

        await self.db.flush()
        await self.db.commit()
        logger.info(f"Job {job_id} status → {status.value}")

    async def set_source_metadata(self, job_id: uuid.UUID, metadata: dict) -> None:
        """Store the ``SourceInfo + MediaInfo`` dict after download completes."""
        job = await self.get_job(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} not found")

        job.source_metadata = metadata
        await self.db.flush()
        await self.db.commit()
        logger.info(f"Job {job_id} source_metadata set")

    # ── JobStep lifecycle ──────────────────────────────────────────────────────

    async def create_job_step(
        self,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        input_artifact: dict | None = None,
    ) -> JobStep:
        """Create a JobStep record in PENDING state."""
        step = JobStep(
            job_id=job_id,
            step_index=step_index,
            operation=operation,
            status=StepStatus.PENDING.value,
            input_artifact=input_artifact,
        )
        self.db.add(step)
        await self.db.flush()
        await self.db.commit()
        return step

    async def update_job_step(
        self,
        step_id: uuid.UUID,
        status: StepStatus,
        output_artifact: dict | None = None,
        error: str | None = None,
    ) -> None:
        """Transition a JobStep and set timestamps."""
        result = await self.db.execute(select(JobStep).where(JobStep.id == step_id))
        step = result.scalar_one_or_none()
        if not step:
            raise NotFoundError(f"JobStep {step_id} not found")

        step.status = status.value

        if status == StepStatus.RUNNING:
            step.started_at = datetime.now(timezone.utc)
        elif status in (StepStatus.COMPLETE, StepStatus.FAILED):
            step.completed_at = datetime.now(timezone.utc)

        if output_artifact is not None:
            step.output_artifact = output_artifact
        if error is not None:
            step.error = error

        await self.db.flush()
        await self.db.commit()
        logger.info(f"JobStep {step_id} → {status.value}")

    async def get_pending_job_step(self, job_id: uuid.UUID, operation: str) -> JobStep | None:
        """Find the first PENDING step for a given operation on a job."""
        result = await self.db.execute(
            select(JobStep)
            .where(JobStep.job_id == job_id)
            .where(JobStep.operation == operation)
            .where(JobStep.status == StepStatus.PENDING.value)
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ── Playlist children ──────────────────────────────────────────────────────

    async def create_child_jobs(
        self,
        parent_job: Job,
        entry_urls: list[str],
        pipeline_steps: list[dict],
        outputs: list[dict],
    ) -> list[Job]:
        """Create one child Job per playlist entry URL.

        Each child inherits the parent's ``pipeline_steps`` and ``outputs``,
        but gets its own ``source_uri`` (the individual video URL from the
        playlist entry) and a 1-based ``playlist_entry_index``.
        """
        children: list[Job] = []
        try:
            for entry_index, url in enumerate(entry_urls, start=1):
                child = Job(
                    api_key_id=parent_job.api_key_id,
                    source_uri=url,
                    source_type=parent_job.source_type,
                    status=JobStatus.PENDING.value,
                    pipeline_steps=pipeline_steps,
                    outputs=outputs,
                    parent_job_id=parent_job.id,
                    playlist_entry_index=entry_index,
                )
                self.db.add(child)
                children.append(child)

            await self.db.flush()
            for c in children:
                await self.db.refresh(c)
            await self.db.commit()
            logger.info(
                "Created %d child jobs for parent %s", len(children), parent_job.id
            )
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create child jobs for {parent_job.id}: {e}")
            raise DatabaseError()

        return children

    async def count_terminal_children(self, parent_id: uuid.UUID) -> tuple[int, int]:
        """Return ``(terminal_count, total_count)`` for children of the given parent.

        Used by ``notify_child_complete`` to decide the aggregate parent state.
        """
        total = await self.db.scalar(
            select(func.count(Job.id)).where(Job.parent_job_id == parent_id)
        )
        terminal = await self.db.scalar(
            select(func.count(Job.id))
            .where(Job.parent_job_id == parent_id)
            .where(Job.status.in_(s.value for s in TERMINAL_JOB_STATUSES))
        )
        return terminal or 0, total or 0

    async def notify_child_complete(self, child_id: uuid.UUID) -> None:
        """Called when a child job reaches a terminal state.

        Checks whether all siblings are also terminal and, if so, computes the
        aggregate ``PARTIAL_SUCCESS`` / ``SUCCEEDED`` / ``FAILED`` on the parent.
        """
        child = await self.get_job(child_id)
        if not child or not child.parent_job_id:
            return  # no parent to notify

        parent_id = child.parent_job_id
        terminal_count, total_count = await self.count_terminal_children(parent_id)

        if terminal_count < total_count:
            return  # not all children have finished yet

        # all children are terminal — compute aggregate
        succeeded = await self.db.scalar(
            select(func.count(Job.id))
            .where(Job.parent_job_id == parent_id)
            .where(Job.status == JobStatus.SUCCEEDED.value)
        )
        failed = await self.db.scalar(
            select(func.count(Job.id))
            .where(Job.parent_job_id == parent_id)
            .where(Job.status == JobStatus.FAILED.value)
        )

        if succeeded == total_count:
            aggregate = JobStatus.SUCCEEDED
        elif failed == total_count:
            aggregate = JobStatus.FAILED
        else:
            aggregate = JobStatus.PARTIAL_SUCCESS

        parent = await self.get_job(parent_id)
        if parent:
            parent.status = aggregate.value
            parent.completed_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.commit()
            logger.info(
                "Parent %s → %s (succeeded=%d, failed=%d / total=%d)",
                parent_id, aggregate.value, succeeded or 0, failed or 0, total_count,
            )
