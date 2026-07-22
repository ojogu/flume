from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, Query, status

from src.core.dependency import (
    get_api_key_from_header,
    get_event_service,
    get_job_service,
    get_upload_service,
)
from src.model.api import ApiKey
from src.model.event import EventType
from src.model.job import JobStatus
from src.public.schema.jobs import (
    CreateJobRequest,
    JobDetailResponse,
    JobListResponse,
    JobResponse,
    StepResponse,
)
from src.model.upload import UploadStatus
from src.service.events import EventService
from src.service.jobs import JobService
from src.service.upload import UploadService
from src.service.validation import validate_and_build_pipeline
from src.utils.response import success
from src.utils.log import get_logger

logger = get_logger(__name__)

job_route = APIRouter(prefix="/job", tags=["jobs"])


@job_route.post("")
async def create_job(
    body: CreateJobRequest,
    api_key: ApiKey = Depends(get_api_key_from_header),
    job_service: JobService = Depends(get_job_service),
    upload_service: UploadService = Depends(get_upload_service),
    event_service: EventService = Depends(get_event_service),
):
    source = body.source

    logger.info(
        f"Job creation request received — "
        f"source={source.uri}, "
        f"type={source.type.value}, "
        f"operations={len(body.pipeline)}, "
        f"api_key={api_key.key_prefix}"
    )

    # Check if the source URI is a prior upload via /upload → mark attached so cleanup sweep doesn't delete it
    upload = await upload_service.find_by_uri(source.uri, api_key.id)
    if upload and upload.status == UploadStatus.UNATTACHED.value:
        await upload_service.attach_upload(upload.id, api_key.id)
        logger.info(f"Prior upload {upload.id} attached to job")

    # Run 5 validation gates (registry → params → types → build spec)
    logger.debug(f"Starting pipeline validation — {len(body.pipeline)} operations")
    spec = validate_and_build_pipeline(
        source=source.uri,
        source_type=source.type.value,
        pipeline=[op.model_dump() for op in body.pipeline],
    )
    # inject implicit download as step 0 — always runs first
    download_type = "r2" if source.uri.startswith("uploads/") else "yt-dlp"
    spec.insert(0, {
        "operation": "download",
        "params": {
            "type": download_type,
            "format": source.format.value,
        },
    })
    logger.info(
        f"Pipeline validation passed — "
        f"{len(spec)} steps: {[s['operation'] for s in spec]}"
    )

    # Persist the job in pending state with the enriched pipeline spec and outputs
    outputs = [o.model_dump() for o in body.outputs]
    selection = source.selection.model_dump() if source.selection else None
    job = await job_service.create_job(
        api_key_id=api_key.id,
        source_uri=source.uri,
        source_type=source.type.value,
        pipeline_spec=spec,
        outputs=outputs,
        selection=selection,
    )

    logger.info(f"Job {job.id} created — status={job.status}, source={job.source_uri}")

    # Emit job.created event for webhook subscribers
    await event_service.emit(
        event_type=EventType.JOB_CREATED,
        resource_id=job.id,
        data={
            "job_id": str(job.id),
            "status": job.status,
            "source_uri": job.source_uri,
            "source_type": job.source_type,
        },
        api_key_id=api_key.id,
    )

    # Dispatch job processing to the orchestrator queue.
    # Celery task_id == job UUID so monitoring tools show the application ID.
    from celery_app.orchestrator import process_job
    process_job.apply_async(args=[str(job.id)], task_id=str(job.id))
    logger.info(f"Job {job.id} dispatched to orchestrator")

    # Wrap in standard {status, message, data} envelope with HTTP 201
    return success(
        data=JobResponse(**job.to_dict()).model_dump(),
        message="Job created",
        status_code=status.HTTP_201_CREATED,
    )


@job_route.get("")
async def list_jobs(
    api_key: ApiKey = Depends(get_api_key_from_header),
    job_service: JobService = Depends(get_job_service),
    status_filter: Optional[str] = Query(None, alias="status"),
    created_after: Optional[datetime] = Query(None, alias="created_after"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """List jobs for the authenticated API key, with optional filters and pagination."""
    jobs, total = await job_service.list_jobs(
        api_key_id=api_key.id,
        status=status_filter,
        created_after=created_after,
        page=page,
        per_page=per_page,
    )
    return success(
        data=JobListResponse(
            total=total,
            page=page,
            per_page=per_page,
            jobs=[JobResponse(**j.to_dict()) for j in jobs],
        ).model_dump(),
    )


@job_route.get("/{job_id}")
async def get_job(
    job_id: uuid.UUID,
    api_key: ApiKey = Depends(get_api_key_from_header),
    job_service: JobService = Depends(get_job_service),
):
    """Get a single job with its steps, scoped to the authenticated API key."""
    job = await job_service.get_job_detail(job_id=job_id, api_key_id=api_key.id)
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")

    return success(
        data=JobDetailResponse(
            **job.to_dict(),
            steps=[StepResponse(**s.to_dict()) for s in job.job_steps],
        ).model_dump(),
    )
