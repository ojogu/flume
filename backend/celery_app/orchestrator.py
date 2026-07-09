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
from src.service.downloader import extract_info, build_source_meta
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
    from src.service.events import EventService

    async with get_async_db_session() as db:
        job_service = JobService(db)
        event_service = EventService(db)
        job = await job_service.get_job(job_id)

        if not job:
            logger.error(f"Job {job_id} not found — aborting")
            return

        if job.status != JobStatus.PENDING.value:
            logger.warning(f"Job {job_id} is not PENDING (status={job.status}) — aborting")
            return

        # mark as processing
        await job_service.update_status(job.id, JobStatus.PROCESSING)

        await event_service.emit(
            event_type="job.processing",
            resource_id=job.id,
            data={
                "job_id": str(job.id),
                "status": JobStatus.PROCESSING.value,
                "source_uri": job.source_uri,
                "source_type": job.source_type,
            },
        )

        try:
            # upload URIs are always single videos — skip yt-dlp extraction
            is_upload = job.source_uri.startswith("uploads/")
            if is_upload:
                await _handle_single(job_service, job)
            else:
                # extract metadata, check if playlist — this is synchronous yt-dlp, runs in thread
                info = extract_info(job.source_uri)

                if info.is_playlist:
                    await _handle_playlist(job_service, job, info)
                else:
                    meta = build_source_meta(info)
                    await job_service.set_source_metadata(job.id, meta)
                    await _handle_single(job_service, job)
        except Exception as e:
            logger.error(f"Orchestration failed for job {job_id}: {e}")
            await job_service.update_status(job.id, JobStatus.FAILED, error=str(e))
            await event_service.emit(
                event_type="job.failed",
                resource_id=job.id,
                data={
                    "job_id": str(job.id),
                    "status": JobStatus.FAILED.value,
                    "error": str(e),
                },
            )


async def _handle_single(job_service: JobService, job: Job):
    """Create JobSteps for a single video and dispatch the download task."""
    from celery_app.download import download_task

    # full pipeline is already on the job (download injected as step 0 at route level)
    for i, step in enumerate(job.pipeline_steps):
        await job_service.create_job_step(job.id, i, step.get("operation", "unknown"))

    logger.info(
        f"Job {job.id} — created {len(job.pipeline_steps)} steps, dispatching download",
    )

    # dispatch download — Celery task_id == job UUID for monitoring
    download_task.apply_async(args=[str(job.id)], task_id=str(job.id))


async def _handle_playlist(job_service: JobService, parent: Job, info):
    """Fan out into child jobs — one per selected playlist entry."""
    from celery_app.download import download_task

    # validate selection against playlist
    selection = _resolve_selection(parent, info)
    if selection is None:
        await job_service.update_status(parent.id, JobStatus.FAILED)
        return

    # resolve per-entry URLs + metadata from extracted info
    entry_metas = [(info.entries[i].url, info.entries[i]) for i in selection]

    children = await job_service.create_child_jobs(
        parent_job=parent,
        entry_metas=entry_metas,
        pipeline_steps=parent.pipeline_steps,
        outputs=parent.outputs,
    )

    if not children:
        await job_service.update_status(parent.id, JobStatus.FAILED, error="No valid playlist entries")
        return

    # create JobSteps + dispatch each child
    for child in children:
        for i, step in enumerate(child.pipeline_steps):
            await job_service.create_job_step(child.id, i, step.get("operation", "unknown"))

        download_task.apply_async(args=[str(child.id)], task_id=str(child.id))

    logger.info(f"Parent {parent.id} — fanned out {len(children)} child jobs")


def _resolve_selection(parent: Job, info) -> list[int] | None:
    """Return 0-based entry indices to process.

    If the parent has a stored ``selection`` (1-based ints from the request),
    convert them to 0-based and filter out-of-bounds.  Otherwise select every
    entry.  Returns ``None`` when the playlist is empty.
    """
    total = info.playlist_count or 0
    if total == 0:
        logger.error(f"Playlist {parent.id} has no entries")
        return None

    if parent.selection:
        entries = parent.selection.get("entries", [])
        return [i - 1 for i in entries if 1 <= i <= total]

    return list(range(total))
