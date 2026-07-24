# ── Download task (op.download queue) ──────────────────────────────────────
# Responsibilities:
#   1. Execute the actual media download (yt-dlp external URL / R2 presigned GET)
#   2. Set ``source_metadata`` on the Job
#   3. Mark the download JobStep COMPLETED
#   4. Notify parent job for aggregate state computation
#
# Runs on the **op.download** queue (many workers, I/O-bound).
# ─────────────────────────────────────────────────────

import os
import uuid
from pathlib import Path

from celery_app.celery import bg_task
from celery_app.utils import run_async_in_sync
from src.model.event import EventType
from src.model.job import JobStatus, StepStatus
from src.service.downloader import download, build_artifact_from_local, assert_size_under_limit, guess_container
from src.service.storage import storage
from src.utils.config import config
from src.utils.http_client import get_http_client
from src.schema.download import FormatPreference, DownloadResult
from src.utils.log import get_logger

logger = get_logger(__name__)


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
    from src.service.events import EventService

    async with get_async_db_session() as db:
        job_service = JobService(db)
        event_service = EventService(db)
        job_uuid = uuid.UUID(job_id)
        job = await job_service.get_job(job_uuid)

        if not job:
            logger.error(f"Job {job_id} not found — aborting download")
            return

        # find the download JobStep
        step = await job_service.get_pending_job_step(job_uuid, "download")
        if not step:
            logger.error(f"No pending download step for job {job_id}")
            return

        # mark step running
        await job_service.update_job_step(step.id, StepStatus.RUNNING)

        await event_service.emit(
            event_type=EventType.STEP_STARTED,
            resource_id=job_uuid,
            data={
                "step_id": str(step.id),
                "job_id": job_id,
                "operation": step.operation,
                "step_index": step.step_index,
            },
            api_key_id=job.api_key_id,
        )

        try:
            # create isolated workspace
            workspace = _ensure_workspace(job_uuid)
            logger.info(f"Workspace ready for job {job_id}: {workspace}")

            # download — external URLs via yt-dlp, upload URIs via R2 presigned GET
            is_upload = job.source_uri.startswith("uploads/")
            if is_upload:
                result = await _download_upload_source(job, workspace)
            else:
                fmt = FormatPreference(
                    job.pipeline_steps[0].get("params", {}).get("format", "best")
                )
                result = download(
                    url=job.source_uri,
                    workspace_dir=str(workspace),
                    source_type=job.source_type,
                    fmt=fmt,
                )

            # persist source metadata on the job
            source_meta = result.artifact.model_dump(
                include={"source", "media"},
                exclude_none=True,
            )
            await job_service.set_source_metadata(job_uuid, source_meta)

            # mark download step complete
            await job_service.update_job_step(
                step.id,
                StepStatus.COMPLETE,
                output_artifact=result.artifact.model_dump(exclude_none=True),
            )

            await event_service.emit(
                event_type=EventType.STEP_COMPLETED,
                resource_id=job_uuid,
                data={
                    "step_id": str(step.id),
                    "job_id": job_id,
                    "operation": step.operation,
                    "step_index": step.step_index,
                    "output_artifact": result.artifact.model_dump(exclude_none=True),
                },
                api_key_id=job.api_key_id,
            )

            # if this job has a parent, notify for aggregate computation
            await job_service.notify_child_complete(job_uuid)

            # determine final status after parent aggregation
            updated_job = await job_service.get_job(job_uuid)
            final_status = updated_job.status if updated_job else JobStatus.SUCCEEDED.value

            await event_service.emit(
                event_type=EventType.JOB_COMPLETED,
                resource_id=job_uuid,
                data={
                    "job_id": job_id,
                    "status": final_status,
                    "source_uri": job.source_uri,
                    "source_type": job.source_type,
                    "source_metadata": source_meta,
                    "error": None,
                },
                api_key_id=job.api_key_id,
            )

            logger.info(f"Download complete for job {job_id} — {result.local_path}")

        except Exception as e:
            logger.error(f"Download failed for job {job_id}: {e}")
            await job_service.update_job_step(
                step.id, StepStatus.FAILED, error="Download failed",
            )
            await job_service.update_status(
                job_uuid, JobStatus.FAILED, error="Download failed",
            )

            await event_service.emit(
                event_type=EventType.STEP_FAILED,
                resource_id=job_uuid,
                data={
                    "step_id": str(step.id),
                    "job_id": job_id,
                    "operation": step.operation,
                    "step_index": step.step_index,
                    "error": "Download failed",
                },
                api_key_id=job.api_key_id,
            )

            await event_service.emit(
                event_type=EventType.JOB_FAILED,
                resource_id=job_uuid,
                data={
                    "job_id": job_id,
                    "status": JobStatus.FAILED.value,
                    "error": "Download failed",
                },
                api_key_id=job.api_key_id,
            )

            # still notify parent so it can compute partial_success
            await job_service.notify_child_complete(job_uuid)


def _ensure_workspace(job_uuid: uuid.UUID) -> Path:
    """Create and return the isolated workspace directory for a job.

    Pattern: ``{config.workspaces_dir}/job_{short_uuid}/``
    """
    short = str(job_uuid).split("-")[0]
    workspace = Path(config.workspaces_dir) / f"job_{short}"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


async def _download_upload_source(job, workspace: Path) -> "DownloadResult":
    """Fetch an upload-sourced file from R2 into the job workspace.

    Generates a presigned GET URL from the R2 storage layer, streams the
    file into ``workspace/input.{ext}``, verifies the size limit, and
    builds an ``Artifact`` without yt-dlp metadata (codec, resolution,
    duration — the FFmpeg pipeline fills those gaps via ffprobe).
    """
    

    presigned_url = await storage.generate_presigned_download_url(job.source_uri)

    # Determine the file extension from the object key (e.g. ``video.mp4``)
    ext = guess_container(job.source_uri)
    local_path = str(workspace / f"input.{ext}")

    async with get_http_client(timeout=300.0) as client:
        async with client.stream("GET", presigned_url) as response:
            response.raise_for_status()
            with open(local_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

    assert_size_under_limit(local_path)

    artifact = build_artifact_from_local(
        local_path, job.source_uri, job_id=str(job.id),
    )

    logger.info(f"R2 download complete for job {job.id} — {local_path} ({artifact.file.size_bytes} bytes)")

    return DownloadResult(
        local_path=local_path,
        metadata=artifact.model_dump(),
        artifact=artifact,
    )
