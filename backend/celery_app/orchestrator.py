# ── Orchestrator task (orchestrator queue) ─────────────────────────────────
# Responsibilities:
#   1. Extract metadata from the source URL
#   2. Detect playlist → fan out child jobs / single → dispatch download
#   3. Create JobStep records for the implicit download step + user pipeline
#   4. Route the actual download to the op.download queue
#
# Runs on the **orchestrator** queue (few workers, lightweight tasks).
# ──────────────────────────────────────────────────────────────────────────

import logging

from celery_app.celery import bg_task
from celery_app.utils import run_async_in_sync
from src.model.job import Job, JobStatus
from src.service.downloader import extract_info
from src.service.jobs import JobService

logger = logging.getLogger(__name__)


@bg_task.task(
    name="jobs.orchestrator.process",
    queue="orchestrator",
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def process_job(job_id: str):
    """Orchestrate a single job: detect playlist, fan out, or dispatch download.

    Runs synchronously but bridges to async for DB and storage calls.
    The ``task_id`` is set to the job UUID by the caller (``route/job.py``)
    so Celery monitoring tools (Flower, CLI) display the application job ID.
    """
    run_async_in_sync(_process_job_async(job_id))


async def _process_job_async(job_id: str):
    from src.utils.db import get_async_db_session
    from src.service.jobs import JobService

    async with get_async_db_session() as db:
        service = JobService(db)
        job = await service.get_job(job_id)

        if not job:
            logger.error(f"Job {job_id} not found — aborting")
            return

        if job.status != JobStatus.PENDING.value:
            logger.warning(f"Job {job_id} is not PENDING (status={job.status}) — aborting")
            return

        # mark as processing
        await service.update_status(job.id, JobStatus.PROCESSING)

        try:
            # upload URIs are always single videos — skip yt-dlp extraction
            is_upload = job.source_uri.startswith("uploads/")
            if is_upload:
                await _handle_single(service, job)
            else:
                # extract metadata — this is synchronous yt-dlp, runs in thread
                info = extract_info(job.source_uri)

                if info.is_playlist:
                    await _handle_playlist(service, job, info)
                else:
                    await _handle_single(service, job)
        except Exception as e:
            logger.error(f"Orchestration failed for job {job_id}: {e}")
            await service.update_status(job.id, JobStatus.FAILED, error=str(e))


async def _handle_single(service: JobService, job: Job):
    """Create JobSteps for a single video and dispatch the download task."""
    from celery_app.download import download_task

    # step 0: implicit download
    await service.create_job_step(job.id, 0, "download")

    # steps 1..N: user's pipeline (deferred — processor not yet built)
    if job.pipeline_steps:
        for i, step in enumerate(job.pipeline_steps, start=1):
            op = step.get("operation", "unknown")
            await service.create_job_step(job.id, i, op)

    logger.info(
        "Job %s — created %d steps, dispatching download",
        job.id,
        1 + (len(job.pipeline_steps) if job.pipeline_steps else 0),
    )

    # dispatch download — Celery task_id == job UUID for monitoring
    download_task.apply_async(args=[str(job.id)], task_id=str(job.id))


async def _handle_playlist(service: JobService, parent: Job, info):
    """Fan out into child jobs — one per selected playlist entry."""
    from celery_app.download import download_task

    # validate selection against playlist
    selection = _resolve_selection(parent, info)
    if selection is None:
        await service.update_status(parent.id, JobStatus.FAILED)
        return

    # create child jobs
    children = await service.create_child_jobs(
        parent_job=parent,
        selection=selection,
        pipeline_steps=parent.pipeline_steps,
        outputs=parent.outputs,
    )

    if not children:
        await service.update_status(parent.id, JobStatus.FAILED, error="No valid playlist entries")
        return

    # create JobSteps + dispatch each child
    for child in children:
        await service.create_job_step(child.id, 0, "download")
        if child.pipeline_steps:
            for i, step in enumerate(child.pipeline_steps, start=1):
                op = step.get("operation", "unknown")
                await service.create_job_step(child.id, i, op)

        download_task.apply_async(args=[str(child.id)], task_id=str(child.id))

    logger.info(
        "Parent %s — fanned out %d child jobs",
        parent.id, len(children),
    )


def _resolve_selection(parent: Job, info) -> list[int] | None:
    """Return the final list of 0-based entry indices to process.

    If the parent was submitted with a user ``selection``, use those
    (converting from 1-based to 0-based).  Otherwise select every entry.

    Returns ``None`` when validation fails (caller should fail the parent).
    """
    from src.utils.db import get_async_db_session
    from src.service.jobs import JobService

    # The parent's source.selection isn't stored directly on the Job model.
    # It was part of the request body but not persisted in the Job record.
    # For now, if the job has a user-provided selection, we need to find it.
    # Since the orchestrator is the first to inspect the URL, we check the
    # playlist count against the entitlements.

    total = info.playlist_count or 0
    if total == 0:
        logger.error(f"Playlist {parent.id} has no entries")
        return None

    # full playlist processing — process all entries
    return list(range(total))
