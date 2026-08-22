import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse, RedirectResponse

from src.core.dependency import (
    get_api_key_from_header,
    get_api_key_service,
    get_event_service,
    get_job_service,
    get_upload_service,
)
from src.core.exception_base import BadRequest, NotFoundError
from src.model.api import ApiKey
from src.model.event import EventType
from src.model.upload import UploadStatus
from src.public.schema.jobs import (
    CreateJobRequest,
    JobDetailResponse,
    JobListResponse,
    JobResponse,
    StepResponse,
)
from src.service.api import (
    WEB_SESSION_DAILY_LIMIT,
    WEB_SESSION_KEY_PREFIX,
    ApiKeyService,
)
from src.service.events import EventService
from src.service.jobs import JobService
from src.service.upload import UploadService
from src.service.validation import validate_and_build_pipeline
from src.utils.log import get_logger
from src.utils.response import success

logger = get_logger(__name__)

job_route = APIRouter(prefix="/job", tags=["jobs"])


@job_route.post("")
async def create_job(
    body: CreateJobRequest,
    api_key: ApiKey = Depends(get_api_key_from_header),
    job_service: JobService = Depends(get_job_service),
    upload_service: UploadService = Depends(get_upload_service),
    event_service: EventService = Depends(get_event_service),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    source = body.source

    # Session key rate limit: 5 jobs/day
    if api_key.key_prefix.startswith(f"{WEB_SESSION_KEY_PREFIX}_"):
        count = await api_key_service.count_jobs_last_24h(api_key.id)
        if count >= WEB_SESSION_DAILY_LIMIT:
            return JSONResponse(
                content={
                    "status": "error",
                    "message": f"Daily job limit reached ({WEB_SESSION_DAILY_LIMIT}/day). Try again tomorrow.",
                    "error_code": "daily_limit_reached",
                },
                status_code=429,
                headers={"Retry-After": "3600"},
            )

    logger.info(
        f"Job creation request received — "
        f"source={source.uri}, "
        f"type={source.type.value}, "
        f"operations={len(body.pipeline)}, "
        f"api_key={api_key.key_prefix}"
    )

    # Resolve uploads/ sources to their real R2 object key before anything else.
    # Clients may reference an upload either by its object key (API surface) or by
    # upload ID (web flow sends uploads/{uuid}). Fail fast on unknown/unconfirmed
    # uploads instead of letting the worker crash with a 404 later.
    source_uri = source.uri
    if source_uri.startswith("uploads/"):
        upload = await upload_service.find_by_uri(source_uri, api_key.id)
        if not upload:
            try:
                upload_id = uuid.UUID(source_uri.removeprefix("uploads/"))
            except ValueError:
                raise BadRequest(f"Unknown upload source: {source_uri!r}") from None
            try:
                upload = await upload_service.get_upload(upload_id, api_key.id)
            except NotFoundError:
                raise BadRequest(f"Unknown upload source: {source_uri!r}") from None
            source_uri = upload.uri

        if upload.status == UploadStatus.PENDING.value:
            raise BadRequest(
                "Upload not confirmed yet — complete the upload before creating a job"
            )
        if upload.status == UploadStatus.UNATTACHED.value:
            await upload_service.attach_upload(upload.id, api_key.id)
            logger.info(f"Prior upload {upload.id!s} attached to job")

    # Run 5 validation gates (registry → params → types → build spec)
    logger.debug(f"Starting pipeline validation — {len(body.pipeline)} operations")
    spec = validate_and_build_pipeline(
        source=source_uri,
        source_type=source.type.value,
        pipeline=[op.model_dump() for op in body.pipeline],
    )
    # inject implicit download as step 0 — always runs first
    if body.pipeline and body.pipeline[0].operation == "join":
        spec.insert(
            0,
            {
                "operation": "download",
                "params": {
                    "clips": body.pipeline[0].params.get("clips", []),
                },
            },
        )
    else:
        download_type = "r2" if source_uri.startswith("uploads/") else "yt-dlp"
        spec.insert(
            0,
            {
                "operation": "download",
                "params": {
                    "type": download_type,
                    "format": source.format.value,
                },
            },
        )
    logger.info(
        f"Pipeline validation passed — "
        f"{len(spec)} steps: {[s['operation'] for s in spec]}"
    )

    # Persist the job in pending state with the enriched pipeline spec and outputs
    outputs = [o.model_dump() for o in body.outputs]
    selection = source.selection.model_dump() if source.selection else None
    job = await job_service.create_job(
        api_key_id=api_key.id,
        source_uri=source_uri,
        source_type=source.type.value,
        pipeline_spec=spec,
        outputs=outputs,
        selection=selection,
    )

    logger.info(
        f"Job {job.id!s} created — status={job.status}, source={job.source_uri}"
    )

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
    logger.info(f"Job {job.id!s} dispatched to orchestrator")

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
    status_filter: str | None = Query(None, alias="status"),
    created_after: datetime | None = Query(None, alias="created_after"),
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


@job_route.get("/{job_id}/download")
async def download_job(
    job_id: uuid.UUID,
    redirect: bool = Query(default=True),
    api_key: ApiKey = Depends(get_api_key_from_header),
    job_service: JobService = Depends(get_job_service),
):
    """Redirect to a presigned R2 URL for the job's final output.

    Use ?redirect=false to get the presigned URL as JSON instead.
    """
    presigned_url = await job_service.generate_download_url(job_id, api_key.id)
    if redirect:
        return RedirectResponse(presigned_url, status_code=302)
    return success(data={"url": presigned_url})


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
