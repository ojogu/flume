import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exception_base import BadRequest, DatabaseError, NotFoundError
from src.model.api import ApiKey
from src.model.job import (
    TERMINAL_JOB_STATUSES,
    Job,
    JobOrigin,
    JobStatus,
    JobStep,
    StepStatus,
)
from src.schema.download import _ExtractedInfo
from src.service.downloader import build_source_meta
from src.utils.log import get_logger
from src.utils.title import sanitize_title_for_filename

logger = get_logger(__name__)


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Job CRUD ───────────────────────────────────────────────────────────────

    async def get_job(self, job_id: uuid.UUID) -> Job | None:
        """Fetch a job by its UUID."""
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def list_jobs(
        self,
        api_key_id: uuid.UUID,
        status: str | None = None,
        origin: str | None = None,
        created_after: datetime | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Job], int]:
        """Paginated job listing scoped to an API key.

        Returns ``(jobs, total_count)`` ordered by creation time descending.
        """
        base = select(Job).where(Job.api_key_id == api_key_id)

        if status:
            base = base.where(Job.status == status)
        if origin:
            base = base.where(Job.origin == origin)
        if created_after:
            base = base.where(Job.created_at >= created_after)

        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))

        query = (
            base.order_by(Job.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.db.execute(query)
        jobs = list(result.scalars().all())

        return jobs, total or 0

    async def get_job_detail(
        self, job_id: uuid.UUID, api_key_id: uuid.UUID
    ) -> Job | None:
        """Fetch a single job with steps, scoped by API key ownership."""
        result = await self.db.execute(
            select(Job)
            .options(selectinload(Job.job_steps))
            .where(Job.id == job_id)
            .where(Job.api_key_id == api_key_id)
        )
        return result.scalar_one_or_none()

    # ── User-scoped queries (for internal/dashboard API) ────────────────────────

    async def list_jobs_by_user(
        self,
        user_id: uuid.UUID,
        status: str | None = None,
        api_key_id: uuid.UUID | None = None,
        origin: str | None = None,
        created_after: datetime | None = None,
        page: int = 1,
        per_page: int = 20,
        top_level: bool = False,
    ) -> tuple[list[Job], int]:
        """Paginated job listing for all API keys belonging to a user.

        Optional ``api_key_id`` filter narrows to a single key.
        ``top_level`` hides playlist children (they are listed inside their parent).
        Returns ``(jobs, total_count)`` ordered by creation time descending.
        """
        base = (
            select(Job)
            .join(ApiKey, Job.api_key_id == ApiKey.id)
            .where(ApiKey.user_id == user_id)
        )

        if api_key_id:
            base = base.where(Job.api_key_id == api_key_id)
        if origin:
            base = base.where(Job.origin == origin)
        if status:
            base = base.where(Job.status == status)
        if created_after:
            base = base.where(Job.created_at >= created_after)
        if top_level:
            base = base.where(Job.parent_job_id.is_(None))

        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))

        query = (
            base.order_by(Job.updated_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.db.execute(query)
        jobs = list(result.scalars().all())

        return jobs, total or 0

    async def get_counts_by_status(
        self,
        user_id: uuid.UUID,
        api_key_id: uuid.UUID | None = None,
        origin: str | None = None,
        top_level: bool = False,
    ) -> dict:
        """Return job counts grouped by status for all API keys belonging to a user.

        ``top_level`` excludes playlist children so counts match the top-level list.
        """
        base = (
            select(Job.status, func.count(Job.id))
            .join(ApiKey, Job.api_key_id == ApiKey.id)
            .where(ApiKey.user_id == user_id)
        )

        if api_key_id:
            base = base.where(Job.api_key_id == api_key_id)
        if origin:
            base = base.where(Job.origin == origin)
        if top_level:
            base = base.where(Job.parent_job_id.is_(None))

        result = await self.db.execute(base.group_by(Job.status))
        counts = {row[0]: row[1] for row in result.all()}

        # Ensure all statuses are present
        all_statuses = [s.value for s in JobStatus]
        for status in all_statuses:
            if status not in counts:
                counts[status] = 0

        return counts

    async def get_job_detail_by_user(
        self, user_id: uuid.UUID, job_id: uuid.UUID
    ) -> Job | None:
        """Fetch a single job with steps, verifying the job belongs to the user."""
        result = await self.db.execute(
            select(Job)
            .options(selectinload(Job.job_steps))
            .join(ApiKey, Job.api_key_id == ApiKey.id)
            .where(Job.id == job_id)
            .where(ApiKey.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_child_counts(
        self, parent_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, dict[str, int]]:
        """Child totals per parent, in one grouped query.

        Returns ``{parent_id: {"child_count", "children_done", "children_failed"}}``
        for parents that have children; parents without children are absent.
        ``DEAD`` children count as failed.
        """
        if not parent_ids:
            return {}
        result = await self.db.execute(
            select(Job.parent_job_id, Job.status, func.count(Job.id))
            .where(Job.parent_job_id.in_(parent_ids))
            .group_by(Job.parent_job_id, Job.status)
        )
        counts: dict[uuid.UUID, dict[str, int]] = {}
        for parent_id, status, n in result.all():
            c = counts.setdefault(
                parent_id, {"child_count": 0, "children_done": 0, "children_failed": 0}
            )
            c["child_count"] += n
            if status == JobStatus.SUCCEEDED.value:
                c["children_done"] += n
            elif status in (JobStatus.FAILED.value, JobStatus.DEAD.value):
                c["children_failed"] += n
        return counts

    async def list_children_by_user(
        self,
        user_id: uuid.UUID,
        parent_id: uuid.UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Job], int]:
        """Paginated children of a playlist parent, scoped to the user's API keys.

        Ordered by ``playlist_entry_index`` ascending. Returns ``(jobs, total)``.
        """
        base = (
            select(Job)
            .join(ApiKey, Job.api_key_id == ApiKey.id)
            .where(ApiKey.user_id == user_id)
            .where(Job.parent_job_id == parent_id)
        )
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        result = await self.db.execute(
            base.order_by(Job.playlist_entry_index.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return list(result.scalars().all()), total or 0

    async def create_job(
        self,
        api_key_id: uuid.UUID,
        source_uri: str | None,
        source_type: str,
        pipeline_spec: list[dict] | None = None,
        outputs: list[dict] | None = None,
        parent_job_id: uuid.UUID | None = None,
        selection: dict | None = None,
        origin: str = JobOrigin.API.value,
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
            selection=selection,
            origin=origin,
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
            logger.exception(f"Error creating job for API key {api_key_id}")
            raise DatabaseError from None

    # ── Status transitions ─────────────────────────────────────────────────────

    async def update_status(
        self,
        job_id: uuid.UUID,
        status: JobStatus,
        error: str | None = None,
    ) -> None:
        """Transition a job to a new status.

        Sets ``completed_at`` automatically when the target is a terminal state.
        A cancelled job is never moved to another status here: a worker finishing
        (or failing) after the user cancelled must not overwrite ``cancelled``.
        """
        job = await self.get_job(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found")
            raise NotFoundError("Job not found")

        values: dict = {"status": status.value}
        if status in TERMINAL_JOB_STATUSES:
            values["completed_at"] = datetime.now(timezone.utc)
        if error:
            values["error"] = error
            logger.error(f"Job {job_id} failed: {error}")

        # Single guarded UPDATE — atomic against a cancel committing at the same moment.
        stmt = update(Job).where(Job.id == job_id)
        if status != JobStatus.CANCELLED:
            stmt = stmt.where(Job.status != JobStatus.CANCELLED.value)
        result = await self.db.execute(
            stmt.values(**values).execution_options(synchronize_session="fetch")
        )
        await self.db.commit()

        if result.rowcount == 0:
            logger.info(f"Job {job_id} is cancelled — ignoring status → {status.value}")
            return
        logger.info(f"Job {job_id} status → {status.value}")

    async def get_status(self, job_id: uuid.UUID) -> str | None:
        """Current status straight from the database.

        Queries the column rather than the ORM object, so it sees a cancel that
        another process committed after this session loaded the job.
        """
        return await self.db.scalar(select(Job.status).where(Job.id == job_id))

    async def should_stop(self, job_id: uuid.UUID) -> bool:
        """True when a worker should abandon this job: it, or its playlist parent, was cancelled.

        A child that is still pending/processing under a cancelled parent is
        marked cancelled here too, which covers children created just after the
        cancel was issued.
        """
        row = (
            await self.db.execute(
                select(Job.status, Job.parent_job_id).where(Job.id == job_id)
            )
        ).first()
        if not row:
            return False
        status, parent_id = row
        if status == JobStatus.CANCELLED.value:
            return True
        if parent_id and await self.get_status(parent_id) == JobStatus.CANCELLED.value:
            await self.db.execute(
                update(Job)
                .where(
                    Job.id == job_id,
                    Job.status.in_((JobStatus.PENDING.value, JobStatus.PROCESSING.value)),
                )
                .values(
                    status=JobStatus.CANCELLED.value,
                    completed_at=datetime.now(timezone.utc),
                )
            )
            await self.db.commit()
            return True
        return False

    # ── Retry ─────────────────────────────────
    # NOTE: after every db.commit() we call db.refresh(job) to re-fetch all attributes while still in the async call stack. 
    # SQLAlchemy's expire_on_commit=True expires every attribute on commit; the next access would trigger a lazy load requiring async IO. Without refresh(), accessing job attributes (including to_dict()) after commit raises greenlet_spawn errors in async context.

    async def retry_job_and_return(
        self, job_id: uuid.UUID, user_id: uuid.UUID
    ) -> tuple[Job, list[dict], str | None]:
        """Retry a job and return fully-hydrated data in one shot.

        Returns (job, steps, api_key_name) after committing the retry.
        Steps are returned as dicts with output_url merged in.
        Handles commit internally — caller should not commit.

        All DB work (validation, mutations, commit, refresh, and subsequent queries) happen in a single async call stack, avoiding greenlet_spawn errors from SQLAlchemy's expire_on_commit=True default.
        """
        from sqlalchemy import select

        from src.model.api import ApiKey
        from src.model.job import JobStep

        job = await self.get_job_detail_by_user(user_id, job_id)
        if not job:
            raise NotFoundError("Job not found")

        # Only SUCCEEDED is truly terminal — FAILED and PARTIAL_SUCCESS are retryable
        if job.status == JobStatus.SUCCEEDED.value:
            raise BadRequest("Cannot retry a succeeded job")

        # DEAD jobs are handled by the DLQ page — not retriable here
        if job.status == JobStatus.DEAD.value:
            raise BadRequest("Cannot retry a dead job")

        job.retry_count += 1

        if job.retry_count >= job.max_retries:
            job.status = JobStatus.DEAD.value
            job.completed_at = datetime.now(timezone.utc)
            job.error = f"Exceeded max retries ({job.max_retries})"
            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(job)  # re-fetch all attributes while still in async context
            logger.warning(f"Job {job_id} reached dead state after {job.retry_count} retries")
        else:
            job.status = JobStatus.PENDING.value
            job.error = None
            job.completed_at = None

            # a retried job that was cancelled must not be aborted by its old flag
            from src.service.cancel import clear_cancel_flag
            await clear_cancel_flag(job.id)

            for step in job.job_steps or []:
                await self.db.delete(step)

            await self.db.flush()
            await self.db.commit()
            from src.service.storage import storage
            storage._delete_workspace(job.id)
            await self.db.refresh(job)  # re-fetch all attributes while still in async context
            logger.info(f"Job {job_id} retried (attempt {job.retry_count}/{job.max_retries})")

            # Emit job.retried event for webhook subscribers
            from src.model.event import EventType
            from src.service.events import EventService
            event_service = EventService(self.db)
            await event_service.emit(
                event_type=EventType.JOB_RETRIED,
                resource_id=job.id,
                data={
                    "job_id": str(job.id),
                    "status": job.status,
                    "retry_count": job.retry_count,
                    "source_uri": job.source_uri,
                    "source_type": job.source_type,
                },
                api_key_id=job.api_key_id,
            )

            # Dispatch job processing to the orchestrator queue
            from celery_app.orchestrator import process_job
            process_job.apply_async(args=[str(job.id)], task_id=str(job.id))
            logger.info(f"Job {job_id} dispatched to orchestrator after retry")

        # Fetch everything fresh — safe now that job has been refreshed post-commit
        api_key_result = await self.db.execute(
            select(ApiKey.name).where(ApiKey.id == job.api_key_id)
        )
        api_key_name = api_key_result.scalar_one_or_none()

        steps_result = await self.db.execute(
            select(JobStep).where(JobStep.job_id == job_id).order_by(JobStep.step_index)
        )
        steps = [
            {
                **s.to_dict(),
                "output_url": s.output_artifact.get("output_url") if s.output_artifact else None,
            }
            for s in steps_result.scalars().all()
        ]

        return job, steps, api_key_name

    # ── Cancel ────────────────────────────────

    async def cancel_job_and_return(
        self,
        job_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
        api_key_id: uuid.UUID | None = None,
    ) -> tuple[Job, list[dict], str | None]:
        """Cancel a job (and, for a playlist parent, its unfinished children).

        Scope by ``user_id`` (JWT / dashboard) or ``api_key_id`` (public API).
        Cancelling a job that already finished is not an error: the job is
        returned unchanged, so a late click just shows the final state.

        What this does:
          * one guarded UPDATE moves pending/processing jobs to ``cancelled`` — it
            cannot overwrite a job that finished in the meantime;
          * unfinished steps are marked cancelled;
          * a Redis flag tells any running yt-dlp download to abort (workers also
            re-check the database before and after each step);
          * a ``job.cancelled`` event is emitted per cancelled job.

        Returns ``(job, steps, api_key_name)`` like ``retry_job_and_return``.
        """
        from src.model.event import EventType
        from src.service.cancel import set_cancel_flag
        from src.service.events import EventService

        if user_id is not None:
            job = await self.get_job_detail_by_user(user_id, job_id)
        else:
            job = await self.get_job_detail(job_id, api_key_id)
        if not job:
            raise NotFoundError("Job not found")

        child_ids = list(
            (
                await self.db.execute(select(Job.id).where(Job.parent_job_id == job_id))
            ).scalars()
        )
        now = datetime.now(timezone.utc)
        cancelled_rows = (
            await self.db.execute(
                update(Job)
                .where(
                    Job.id.in_([job_id, *child_ids]),
                    Job.status.in_(
                        (JobStatus.PENDING.value, JobStatus.PROCESSING.value)
                    ),
                )
                .values(status=JobStatus.CANCELLED.value, completed_at=now)
                .returning(Job.id, Job.api_key_id)
                .execution_options(synchronize_session="fetch")
            )
        ).all()
        cancelled_ids = [r[0] for r in cancelled_rows]

        if cancelled_ids:
            await self.db.execute(
                update(JobStep)
                .where(
                    JobStep.job_id.in_(cancelled_ids),
                    JobStep.status.in_(
                        (StepStatus.PENDING.value, StepStatus.RUNNING.value)
                    ),
                )
                .values(status=StepStatus.CANCELLED.value)
            )
        await self.db.commit()
        await self.db.refresh(job)  # re-fetch while still in async context

        for cid in cancelled_ids:
            await set_cancel_flag(cid)
        logger.info(
            f"Job {job_id} cancel requested — cancelled {len(cancelled_ids)} job(s) "
            f"({len(child_ids)} children)"
        )

        event_service = EventService(self.db)
        for cid, key_id in cancelled_rows:
            await event_service.emit(
                event_type=EventType.JOB_CANCELLED,
                resource_id=cid,
                data={"job_id": str(cid), "status": JobStatus.CANCELLED.value, "error": None},
                api_key_id=key_id,
            )

        # A single playlist child was cancelled: let the parent recompute its status.
        if job.parent_job_id and job_id in cancelled_ids:
            await self.notify_child_complete(job_id)

        api_key_name = await self.db.scalar(
            select(ApiKey.name).where(ApiKey.id == job.api_key_id)
        )
        steps_result = await self.db.execute(
            select(JobStep).where(JobStep.job_id == job_id).order_by(JobStep.step_index)
        )
        steps = [
            {
                **s.to_dict(),
                "output_url": s.output_artifact.get("output_url") if s.output_artifact else None,
            }
            for s in steps_result.scalars().all()
        ]
        return job, steps, api_key_name

    async def set_source_metadata(self, job_id: uuid.UUID, metadata: dict) -> None:
        """Store the ``SourceInfo + MediaInfo`` dict after download completes."""
        job = await self.get_job(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found")
            raise NotFoundError("Job not found")

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
            logger.warning(f"Job step {step_id} not found")
            raise NotFoundError("Job step not found")

        step.status = status.value

        if status == StepStatus.RUNNING:
            step.started_at = datetime.now(timezone.utc)
        elif status in (StepStatus.COMPLETE, StepStatus.FAILED, StepStatus.CANCELLED):
            step.completed_at = datetime.now(timezone.utc)

        if output_artifact is not None:
            step.output_artifact = output_artifact
        if error is not None:
            step.error = error

        await self.db.flush()
        await self.db.commit()
        logger.debug(f"JobStep {step_id} → {status.value}")

    async def get_pending_job_step(
        self, job_id: uuid.UUID, operation: str
    ) -> JobStep | None:
        """Find the first PENDING step for a given operation on a job."""
        result = await self.db.execute(
            select(JobStep)
            .where(JobStep.job_id == job_id)
            .where(JobStep.operation == operation)
            .where(JobStep.status == StepStatus.PENDING.value)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_step(self, job_id: uuid.UUID, step_index: int) -> JobStep | None:
        """Fetch a specific JobStep by job_id and step_index."""
        result = await self.db.execute(
            select(JobStep)
            .where(JobStep.job_id == job_id)
            .where(JobStep.step_index == step_index)
        )
        return result.scalar_one_or_none()

    # ── Playlist children ──────────────────────────────────────────────────────

    async def create_child_jobs(
        self,
        parent_job: Job,
        entry_metas: list[tuple[str, _ExtractedInfo]],
        pipeline_steps: list[dict],
        outputs: list[dict],
    ) -> list[Job]:
        """Create one child Job per playlist entry.

        Each child inherits the parent's ``pipeline_steps``, ``outputs``, and ``origin``,
        but gets its own ``source_uri`` (the individual video URL from the
        playlist entry), a 1-based ``playlist_entry_index``, and
        pre-populated ``source_metadata`` from the initial extraction.
        """
        children: list[Job] = []
        try:
            for entry_index, (url, meta) in enumerate(entry_metas, start=1):
                child = Job(
                    api_key_id=parent_job.api_key_id,
                    source_uri=url,
                    source_type=parent_job.source_type,
                    status=JobStatus.PENDING.value,
                    source_metadata=build_source_meta(meta),
                    pipeline_steps=pipeline_steps,
                    outputs=outputs,
                    parent_job_id=parent_job.id,
                    playlist_entry_index=entry_index,
                    origin=parent_job.origin,
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
            logger.error(f"Failed to create child jobs for {parent_job.id!s}: {e}")
            logger.exception(f"Failed to create child jobs for {parent_job.id!s}")
            raise DatabaseError from None

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

        # A cancelled parent keeps its status; its children finishing must not reopen it.
        if await self.get_status(parent_id) == JobStatus.CANCELLED.value:
            return

        # touch the parent so an active playlist rises in history (sorted by updated_at)
        parent = await self.get_job(parent_id)
        if parent:
            parent.updated_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.commit()

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
            .where(Job.status.in_((JobStatus.FAILED.value, JobStatus.DEAD.value)))
        )

        cancelled = await self.db.scalar(
            select(func.count(Job.id))
            .where(Job.parent_job_id == parent_id)
            .where(Job.status == JobStatus.CANCELLED.value)
        )

        if succeeded == total_count:
            aggregate = JobStatus.SUCCEEDED
        elif cancelled == total_count:
            aggregate = JobStatus.CANCELLED
        elif not succeeded and failed:
            # nothing succeeded and at least one genuinely failed (the rest may be cancelled)
            aggregate = JobStatus.FAILED
        else:
            aggregate = JobStatus.PARTIAL_SUCCESS

        parent = await self.get_job(parent_id)
        if parent:
            # guarded: never overwrite a parent cancelled in the meantime
            await self.db.execute(
                update(Job)
                .where(Job.id == parent_id, Job.status != JobStatus.CANCELLED.value)
                .values(status=aggregate.value, completed_at=datetime.now(timezone.utc))
                .execution_options(synchronize_session="fetch")
            )
            await self.db.commit()
            logger.info(
                "Parent %s → %s (succeeded=%d, failed=%d / total=%d)",
                parent_id,
                aggregate.value,
                succeeded or 0,
                failed or 0,
                total_count,
            )

    async def generate_download_url(
        self, job_id: uuid.UUID, api_key_id: uuid.UUID
    ) -> str:
        """Generate a presigned R2 URL for the job's final output.

        Finds the last completed step, constructs the R2 object key from the step index and container, generates a fresh presigned URL, and returns it.

        Args:
            job_id: The job to generate a download URL for.
            api_key_id: The owning API key (used for key scoping).

        Returns:
            A presigned R2 download URL.

        Raises:
            NotFoundError: If the job or a completed step is not found.
            BadRequest: If the job has no completed steps or is not in a terminal state.
        """
        from src.model.job import JobStatus
        from src.service.storage import storage

        job = await self.get_job_detail(job_id, api_key_id)
        if not job:
            raise NotFoundError("Job not found")

        has_children = await self.db.scalar(
            select(func.count(Job.id)).where(Job.parent_job_id == job.id)
        )
        if has_children:
            raise BadRequest(
                "This job is a playlist and has no single file. "
                "Download its videos individually."
            )

        if job.status not in (
            JobStatus.SUCCEEDED.value,
            JobStatus.PARTIAL_SUCCESS.value,
        ):
            raise BadRequest(
                f"Job is not complete (status={job.status}). "
                "Download requires a terminal job state."
            )

        completed_steps = [s for s in job.job_steps if s.status == "complete"]
        if not completed_steps:
            raise NotFoundError("No completed steps found for this job")

        last_step = max(completed_steps, key=lambda s: s.step_index)
        artifact = last_step.output_artifact
        if not artifact:
            raise NotFoundError(f"Step {last_step.step_index} has no output artifact")

        container = artifact.get("file", {}).get("container", "mp4")
        api_key_short = str(job.api_key_id).split("-")[0]
        job_short = str(job.id).split("-")[0]

        title = job.source_metadata.get("source", {}).get("title") if job.source_metadata else None
        sanitized = sanitize_title_for_filename(title)

        if last_step.step_index == 0:
            filename = sanitized if sanitized else "input"
        else:
            filename = sanitized if sanitized else f"step_{last_step.step_index}_output"

        object_key = f"outputs/{api_key_short}/{job_short}/{filename}.{container}"

        return await storage.generate_presigned_download_url(object_key)
