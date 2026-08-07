# ── Operation execution task (media_queue) ──────────────────────────────────
# Responsibilities:
#   1. Pick a step (step_index >= 1) for a job and execute it via FFmpeg
#   2. Resolve the input file from the previous step's output_artifact
#   3. Mark the step RUNNING → COMPLETE/FAILED and emit STEP_* events
#   4. Chain to the next step (pipeline_steps[step_index+1]) or mark the job SUCCEEDED when this was the final step.

# Step 0 (download) is executed by the download task and dispatches the first operation task via this module when the pipeline has user steps.

# Runs on the **media_queue** (CPU-bound, FFmpeg). Task name is ``jobs.media.execute``.
# ────────────────────────────────────────

import uuid
from pathlib import Path

from celery_app.celery import bg_task
from celery_app.utils import run_async_in_sync
from src.model.event import EventType
from src.model.job import Job, JobStatus, JobStep, StepStatus
from src.schema.processor import ProcessResult
from src.service.events import EventService
from src.service.jobs import JobService
from src.utils.config import config
from src.utils.log import get_logger

logger = get_logger(__name__)


@bg_task.task(
    name="jobs.media.execute",
    queue="media_queue",
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def execute_operation_task(job_id: str, step_index: int):
    """Execute the pipeline step at ``step_index`` for ``job_id``.

    Generic across every operation in the registry — the operation name and params are read from ``job.pipeline_steps[step_index]``.

    The ``task_id`` includes the step index so monitoring tools (Flower) can distinguish concurrent step executions for the same job.
    """
    run_async_in_sync(_execute_operation_async(job_id, step_index))


async def _execute_operation_async(job_id: str, step_index: int):
    from src.service.events import EventService
    from src.service.jobs import JobService
    from src.service.processor import ProcessorService
    from src.utils.db import get_async_db_session

    async with get_async_db_session() as db:
        job_service = JobService(db)
        event_service = EventService(db)
        processor = ProcessorService(db)

        job_uuid = uuid.UUID(job_id)
        job = await job_service.get_job(job_uuid)

        if not job:
            logger.error(f"Job {job_id} not found — aborting operation")
            return

        step = await job_service.get_step(job_uuid, step_index)
        if not step:
            logger.error(f"No JobStep at index {step_index} for job {job_id}")
            return

        # Idempotency guard: skip if this step already reached a terminal state.
        if step.status in (StepStatus.COMPLETE.value, StepStatus.FAILED.value):
            logger.warning(
                f"Step {step_index} ({step.operation}) already {step.status} "
                f"— skipping execution"
            )
            return

        if step_index < len(job.pipeline_steps or []):
            step_spec = job.pipeline_steps[step_index]
        else:
            step_spec = None
        if not step_spec:
            logger.error(
                f"No pipeline_steps entry at index {step_index} for job {job_id}"
            )
            return

        operation = step_spec["operation"]
        params = step_spec.get("params", {})

        # mark step RUNNING and emit STEP_STARTED
        await job_service.update_job_step(step.id, StepStatus.RUNNING)
        await event_service.emit(
            event_type=EventType.STEP_STARTED,
            resource_id=job_uuid,
            data={
                "step_id": str(step.id),
                "job_id": job_id,
                "operation": operation,
                "step_index": step_index,
            },
            api_key_id=job.api_key_id,
        )

        try:
            # Resolve input from the previous step's output_artifact.
            input_path = await _resolve_input_path(job_service, job_uuid, step_index)
            if input_path is None:
                raise RuntimeError(
                    f"Could not resolve input path for step {step_index}"
                )

            workspace = _ensure_workspace(job_uuid)

            result = await processor.execute_operation(
                job_id=job_uuid,
                step_index=step_index,
                operation=operation,
                params=params,
                input_path=input_path,
                workspace=workspace,
            )

            if result.success:
                if result.artifact is None:
                    # Processor returned success without an artifact — treat as a contract violation and route through the failure path.
                    raise RuntimeError(
                        f"[{operation}] Processor returned success but no artifact"
                    )
                await _handle_success(
                    job_service, event_service,
                    job, step, step_index, operation, result,
                )
            else:
                # Operation failed with a structured ProcessResult.error.
                error_summary = (
                    result.error.summary if result.error
                    else f"[{operation}] FFmpeg failed (no error details)"
                )
                await _handle_failure(
                    job_service, event_service,
                    job, step, step_index, operation, error_summary,
                )

        except Exception as e:
            # Catches input-resolution failures, unexpected exceptions from the processor, and the contract-violation case above. 
            # Operation-level failures (ProcessResult.success=False) are handled above and do not re-enter this branch.
            await _handle_failure(
                job_service, event_service,
                job, step, step_index, operation, str(e),
            )


async def _handle_success(
    job_service: JobService,
    event_service: EventService,
    job: Job,
    step: JobStep,
    step_index: int,
    operation: str,
    result: ProcessResult,
) -> None:
    """Persist step COMPLETED, emit STEP_COMPLETED, chain to next or finish job."""
    job_uuid = job.id
    job_id = str(job_uuid)

    # Emit STEP_COMPLETED — output_artifact without output_url for intermediate steps.
    # output_url is only set and attached when this is the final step.
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
            "operation": operation,
            "step_index": step_index,
            "output_artifact": result.artifact.model_dump(exclude_none=True),
        },
        api_key_id=job.api_key_id,
    )

    # Chain to the next step if one exists, otherwise finalize the job.
    pipeline_len = len(job.pipeline_steps or [])
    next_index = step_index + 1
    if next_index < pipeline_len:
        next_op = job.pipeline_steps[next_index].get("operation", "unknown")
        logger.info(
            f"Job {job_id} step {step_index} complete — chaining to step {next_index} ({next_op})"
        )
        execute_operation_task.apply_async(
            args=[job_id, next_index],
            task_id=f"{job_id}-step-{next_index}",
        )
    else:
        # Last step — upload to R2 and attach CDN URL to artifact.
        from src.service.storage import storage
        from src.utils.config import config
        ext = Path(result.output_path).suffix.lstrip(".") or "mp4"
        api_key_short = str(job.api_key_id).split("-")[0]
        job_short = str(job_uuid).split("-")[0]
        object_key = (
            f"outputs/{api_key_short}/{job_short}/"
            f"step_{step_index}_output.{ext}"
        )
        await storage.upload_file(result.output_path, object_key)
        result.artifact.output_url = (
            f"{config.cdn_base_url}/job/{job_id}/step/{step_index}/download"
        )

        # Re-persist the step with the enriched artifact (output_url now set)
        await job_service.update_job_step(
            step.id,
            StepStatus.COMPLETE,
            output_artifact=result.artifact.model_dump(exclude_none=True),
        )

        logger.info(
            f"Job {job_id} — final step {step_index} complete, marking SUCCEEDED"
        )
        await job_service.update_status(job_uuid, JobStatus.SUCCEEDED)
        await event_service.emit(
            event_type=EventType.JOB_COMPLETED,
            resource_id=job_uuid,
            data={
                "job_id": job_id,
                "status": JobStatus.SUCCEEDED.value,
                "source_uri": job.source_uri,
                "source_type": job.source_type,
                "error": None,
                "output_url": result.artifact.output_url,
            },
            api_key_id=job.api_key_id,
        )
        # Playlist aggregation: a child completing may finalize the parent.
        await job_service.notify_child_complete(job_uuid)


async def _handle_failure(
    job_service: JobService,
    event_service: EventService,
    job: Job,
    step: JobStep,
    step_index: int,
    operation: str,
    error_summary: str,
) -> None:
    """Persist step FAILED, emit STEP_FAILED + JOB_FAILED, notify parent."""
    job_uuid = job.id
    job_id = str(job_uuid)

    await job_service.update_job_step(
        step.id, StepStatus.FAILED, error=error_summary,
    )
    await job_service.update_status(
        job_uuid, JobStatus.FAILED, error=error_summary,
    )

    await event_service.emit(
        event_type=EventType.STEP_FAILED,
        resource_id=job_uuid,
        data={
            "step_id": str(step.id),
            "job_id": job_id,
            "operation": operation,
            "step_index": step_index,
            "error": error_summary,
        },
        api_key_id=job.api_key_id,
    )
    await event_service.emit(
        event_type=EventType.JOB_FAILED,
        resource_id=job_uuid,
        data={
            "job_id": job_id,
            "status": JobStatus.FAILED.value,
            "error": error_summary,
        },
        api_key_id=job.api_key_id,
    )

    # Even on failure the parent must be notified so it can compute partial_success when all siblings have terminated.
    await job_service.notify_child_complete(job_uuid)


async def _resolve_input_path(job_service: JobService, job_uuid: uuid.UUID, step_index: int) -> str | None:
    """Resolve the input file for ``step_index`` from the previous step's output artifact.

    Each step N (>= 1) reads its input from step N-1's output_artifact.file.path.
    Step 0 has no predecessor and is not handled by this function.

    Returns None if the previous step is not COMPLETE or has no output artifact.
    """
    # step_index 0 has no predecessor — input is the original download artifact
    if step_index <= 0:
        return None

    # Fetch the completed predecessor step
    prev_step = await job_service.get_step(job_uuid, step_index - 1)
    if not prev_step:
        logger.error(
            f"Previous step {step_index - 1} not found for job {job_uuid}"
        )
        return None

    # Previous step must have completed successfully — a failed step breaks the chain
    if prev_step.status != StepStatus.COMPLETE.value:
        logger.error(
            f"Previous step {step_index - 1} is {prev_step.status} (not complete) "
            f"— cannot chain"
        )
        return None

    # Unpack the output artifact from the previous step
    artifact = prev_step.output_artifact
    if not artifact:
        logger.error(
            f"Previous step {step_index - 1} has no output_artifact"
        )
        return None

    # Extract the file path from the artifact's file object
    file_path = artifact.get("file", {}).get("path")
    if not file_path:
        logger.error(
            f"Previous step {step_index - 1} output_artifact has no file.path"
        )
        return None

    return file_path


def _ensure_workspace(job_uuid: uuid.UUID) -> Path:
    """Return the job's isolated workspace directory, creating it if missing."""
    short = str(job_uuid).split("-")[0]
    workspace = Path(config.workspaces_dir) / f"job_{short}"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace