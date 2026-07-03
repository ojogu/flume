# ── Download task (op.download queue) ──────────────────────────────────────
# Responsibilities:
#   1. Execute the actual media download (yt-dlp external URL / R2 presigned GET)
#   2. Set ``source_metadata`` on the Job
#   3. Mark the download JobStep COMPLETED
#   4. Notify parent job for aggregate state computation
#
# Runs on the **op.download** queue (many workers, I/O-bound).
# ───────────────────────────────────────────────────────────────────────────

import logging
import os
import uuid
from pathlib import Path

from celery_app.celery import bg_task
from celery_app.utils import run_async_in_sync
from src.model.job import JobStatus, StepStatus
from src.service.downloader import download
from src.utils.config import config

logger = logging.getLogger(__name__)


@bg_task.task(
    name="jobs.download.execute",
    queue="op.download",
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def download_task(job_id: str):
    """Download the source media for the given job.

    * External URL  → ``downloader.download()`` (yt-dlp)
    * Upload URI    → R2 presigned GET (future)

    The ``task_id`` matches the job UUID for monitoring.
    """
    run_async_in_sync(_download_task_async(job_id))


async def _download_task_async(job_id: str):
    from src.utils.db import get_async_db_session
    from src.service.jobs import JobService

    async with get_async_db_session() as db:
        service = JobService(db)
        job_uuid = uuid.UUID(job_id)
        job = await service.get_job(job_uuid)

        if not job:
            logger.error("Job %s not found — aborting download", job_id)
            return

        # find the download JobStep
        step = await service.get_pending_job_step(job_uuid, "download")
        if not step:
            logger.error("No pending download step for job %s", job_id)
            return

        # mark step running
        await service.update_job_step(step.id, StepStatus.RUNNING)

        try:
            # create isolated workspace
            workspace = _ensure_workspace(job_uuid)
            logger.info("Workspace ready for job %s: %s", job_id, workspace)

            # download — currently supports external URLs via yt-dlp.
            # Upload-sourced jobs will fetch via R2 presigned GET in a future pass.
            is_upload = job.source_uri.startswith("uploads/")
            if is_upload:
                # ── placeholder: R2 presigned GET → workspace ────────
                # (future when the upload flow is integrated with the worker)
                raise NotImplementedError("R2 source fetch not yet implemented")
            else:
                result = download(
                    url=job.source_uri,
                    workspace_dir=str(workspace),
                    source_type=job.source_type,
                )

            # persist source metadata on the job
            source_meta = result.artifact.model_dump(
                include={"source", "media"},
                exclude_none=True,
            )
            await service.set_source_metadata(job_uuid, source_meta)

            # mark download step complete
            await service.update_job_step(
                step.id,
                StepStatus.COMPLETE,
                output_artifact=result.artifact.model_dump(exclude_none=True),
            )

            # if this job has a parent, notify for aggregate computation
            await service.notify_child_complete(job_uuid)

            logger.info("Download complete for job %s — %s", job_id, result.local_path)

        except Exception as e:
            logger.error("Download failed for job %s: %s", job_id, e)
            await service.update_job_step(
                step.id, StepStatus.FAILED, error=str(e),
            )
            await service.update_status(
                job_uuid, JobStatus.FAILED, error=f"Download failed: {e}",
            )
            # still notify parent so it can compute partial_success
            await service.notify_child_complete(job_uuid)


def _ensure_workspace(job_uuid: uuid.UUID) -> Path:
    """Create and return the isolated workspace directory for a job.

    Pattern: ``{config.workspaces_dir}/job_{short_uuid}/``
    """
    short = str(job_uuid).split("-")[0]
    workspace = Path(config.workspaces_dir) / f"job_{short}"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace
