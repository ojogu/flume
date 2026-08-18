# ── Download task (download_queue) ────────────────────────────────────────
# Responsibilities:
#   1. Execute the actual media download (yt-dlp external URL / R2 presigned GET)
#   2. Set ``source_metadata`` on the Job
#   3. Mark the download JobStep COMPLETED
#   4. Notify parent job for aggregate state computation
#
# Runs on the **download_queue** (many workers, I/O-bound).
# ─────────────────────────────────────────────────────

import asyncio
import json
import time
import uuid
from pathlib import Path

from celery_app.celery import bg_task
from celery_app.utils import run_async_in_sync
from src.model.event import EventType
from src.model.job import JobStatus, StepStatus
from src.schema.download import DownloadResult, _ExtractedInfo, _FormatPreference
import yt_dlp

from src.service.downloader import (
    _build_ydl_opts,
    _is_client_blocked,
    assert_size_under_limit,
    build_artifact_from_local,
    download,
    guess_container,
)
from src.service.storage import storage
from src.utils.config import config
from src.utils.http_client import get_http_client
from src.utils.log import get_logger
from src.utils.title import sanitize_title_for_filename

logger = get_logger(__name__)


@bg_task.task(
    name="jobs.download.execute",
    queue="download_queue",
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
    from src.service.events import EventService
    from src.service.jobs import JobService
    from src.utils.db import get_async_db_session

    start = time.perf_counter()
    logger.info(f"Download task started for job {job_id}")

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
            workspace = storage._ensure_workspace(job_uuid)
            logger.info(f"Workspace ready for job {job_id}: {workspace}")

            # check for clips param (used by join operation)
            clips = step.params.get("clips")
            if clips:
                result = await _download_clips(clips, workspace, job_id)
            else:
                # download — external URLs via yt-dlp, upload URIs via R2 presigned GET
                is_upload = job.source_uri.startswith("uploads/")
                if is_upload:
                    result = await _download_upload_source(job, workspace)
                else:
                    # get the format from the client, or default to best
                    fmt = _FormatPreference(
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
                output_artifact=result.artifact.model_dump(
                    mode="json", exclude_none=True
                ),
            )

            await event_service.emit(
                event_type=EventType.STEP_COMPLETED,
                resource_id=job_uuid,
                data={
                    "step_id": str(step.id),
                    "job_id": job_id,
                    "operation": step.operation,
                    "step_index": step.step_index,
                    "output_artifact": result.artifact.model_dump(
                        mode="json", exclude_none=True
                    ),
                },
                api_key_id=job.api_key_id,
            )

            pipeline_steps = job.pipeline_steps or []
            if len(pipeline_steps) > 1:
                # More steps to run: chain to the first operation step (step_index=1).
                # The job stays PROCESSING; final upload and status are set by the last operation task.
                from celery_app.operations import execute_operation_task

                next_index = 1
                next_op = pipeline_steps[next_index].get("operation", "unknown")
                logger.info(
                    f"Job {job_id} step 0 (download) complete — chaining to step {next_index} ({next_op})"
                )
                execute_operation_task.apply_async(
                    args=[job_id, next_index],
                    task_id=f"{job_id}-step-{next_index}",
                )
            else:
                # Download was the only step — upload to R2, finalize the job.
                ext = guess_container(result.local_path)
                api_key_short = str(job.api_key_id).split("-")[0]
                job_short = str(job_uuid).split("-")[0]
                sanitized = sanitize_title_for_filename(result.metadata.title)
                filename = sanitized if sanitized else "input"
                object_key = f"outputs/{api_key_short}/{job_short}/{filename}.{ext}"
                await storage.upload_file(result.local_path, object_key)
                storage._delete_workspace(job_uuid)
                result.artifact.output_url = (
                    f"{config.cdn_base_url}/job/{job_id}/download"
                )

                # Re-persist the step with the enriched artifact (output_url now set)
                await job_service.update_job_step(
                    step.id,
                    StepStatus.COMPLETE,
                    output_artifact=result.artifact.model_dump(
                        mode="json", exclude_none=True
                    ),
                )

                await job_service.update_status(job_uuid, JobStatus.SUCCEEDED)
                await job_service.notify_child_complete(job_uuid)

                updated_job = await job_service.get_job(job_uuid)
                final_status = (
                    updated_job.status if updated_job else JobStatus.SUCCEEDED.value
                )

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
                        "output_url": result.artifact.output_url,
                    },
                    api_key_id=job.api_key_id,
                )

            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(f"Download complete for job {job_id} — {result.local_path} — duration_ms={duration_ms:.2f}")

        except Exception as e:
            logger.error(f"Download failed for job {job_id}: {e}")
            logger.exception(f"Download failed for job {job_id}")
            await job_service.update_job_step(
                step.id,
                StepStatus.FAILED,
                error="Download failed",
            )
            await job_service.update_status(
                job_uuid,
                JobStatus.FAILED,
                error="Download failed",
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
        local_path,
        job.source_uri,
        job_id=str(job.id),
    )

    logger.info(
        f"R2 download complete for job {job.id!s} — {local_path} ({artifact.file.size_bytes} bytes)"
    )

    metadata = _ExtractedInfo(
        platform=artifact.source.platform,
        video_id=artifact.source.video_id,
        url=artifact.source.url,
        title=artifact.source.title or "",
    )

    return DownloadResult(
        local_path=local_path,
        metadata=metadata,
        artifact=artifact,
    )


async def _download_r2_object(object_key: str, workspace: Path, filename: str) -> str:
    """Fetch any R2 object into the workspace with a given filename.

    Generates a presigned GET URL, streams the file to disk, and verifies the size limit. Returns the local path.
    """
    presigned_url = await storage.generate_presigned_download_url(object_key)
    local_path = str(workspace / filename)

    async with get_http_client(timeout=300.0) as client:
        async with client.stream("GET", presigned_url) as response:
            response.raise_for_status()
            with open(local_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

    assert_size_under_limit(local_path)
    logger.info(f"R2 download complete — {object_key} -> {local_path}")
    return local_path


async def _download_clips(clips: list[str], workspace: Path, job_id: str) -> "DownloadResult":
    """Download multiple clips for join operation.

    Each clip URL is downloaded to the workspace. R2 URLs use presigned GET; external URLs use yt-dlp. The list of local paths is written to a JSON file whose path is returned as the result's local_path.
    """
    clip_paths: list[str] = []

    for i, clip_url in enumerate(clips):
        clip_url = clip_url.strip()
        try:
            if clip_url.startswith("uploads/"):
                ext = Path(clip_url).suffix.lstrip(".") or "mp4"
                filename = f"join_clip_{i}.{ext}"
                local_path = await _download_r2_object(clip_url, workspace, filename)
            else:
                local_path = str(workspace / f"join_clip_{i}.mp4")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, _download_clip_sync, clip_url, str(workspace), i
                )

            clip_paths.append(local_path)
        except Exception as exc:
            logger.error(f"[_download_clips] job={job_id} clip[{i}] failed: {exc}")
            raise

    json_path = str(workspace / "join_clips.json")
    with open(json_path, "w") as f:
        json.dump(clip_paths, f)

    metadata = _ExtractedInfo(
        platform="internal",
        video_id="join",
        url="internal://clips",
        title="join_clips",
    )
    artifact = build_artifact_from_local(
        json_path,
        "internal://clips",
        job_id=job_id,
    )

    return DownloadResult(
        local_path=json_path,
        metadata=metadata,
        artifact=artifact,
    )


def _download_clip_sync(url: str, workspace_dir: str, index: int):
    """Synchronous yt-dlp download with android_vr→web_safari fallback."""
    format_string = "bestvideo+bestaudio/best"

    for client in ("android_vr", "web_safari"):
        opts = _build_ydl_opts(workspace_dir, format_string, download=True, client=client)
        opts["outtmpl"] = str(Path(workspace_dir) / f"join_clip_{index}.%(ext)s")
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
                return
        except yt_dlp.utils.DownloadError as exc:
            if _is_client_blocked(exc) and client == "android_vr":
                logger.warning(
                    f"android_vr blocked for clip {index}, falling back to web_safari: {exc}"
                )
                continue
            raise
