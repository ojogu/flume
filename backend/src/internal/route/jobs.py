import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from src.core.dependency import (
    get_api_key_service,
    get_current_user,
    get_event_service,
    get_job_service,
    get_upload_service,
)
from src.core.exception_base import BadRequest
from src.internal.schema.jobs import (
    InternalJobDetailResponse,
    InternalJobListResponse,
    InternalJobResponse,
    RetryJobRequest,
)
from src.model.event import EventType
from src.model.user import User
from src.public.schema.jobs import CreateJobRequest, JobResponse
from src.service.api import AUTHENTICATED_MONTHLY_LIMIT, ApiKeyService
from src.service.events import EventService
from src.service.jobs import JobService
from src.service.upload import UploadService
from src.service.validation import validate_and_build_pipeline
from src.utils.log import get_logger
from src.utils.response import success

logger = get_logger(__name__)

# ── Internal job routes (JWT authenticated) ──────────────────────────────────
# Dashboard-facing endpoints for viewing jobs across all of a user's API keys.
# The user's identity comes from the JWT, not from an API key.

internal_job_route = APIRouter(prefix="/jobs", tags=["internal-jobs"])


def _enrich_job(job, api_key_name: str | None = None) -> dict:
    """Build InternalJobResponse dict, attaching api_key_name if available."""
    data = job.to_dict()
    data["api_key_name"] = api_key_name
    return InternalJobResponse(**data).model_dump()


@internal_job_route.post("", status_code=status.HTTP_201_CREATED)
async def create_job(
    body: CreateJobRequest,
    user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    upload_service: UploadService = Depends(get_upload_service),
    event_service: EventService = Depends(get_event_service),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    """Create a job from the Flume Web page for an authenticated user (JWT).

    Jobs attach to the user's dedicated 'web' API key; enforces the
    authenticated monthly limit (20/month).
    """
    web_key = await api_key_service.get_or_create_web_key(user.id)

    count = await api_key_service.count_jobs_this_month(web_key.id)
    if count >= AUTHENTICATED_MONTHLY_LIMIT:
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Monthly job limit reached ({AUTHENTICATED_MONTHLY_LIMIT}/month).",
                "error_code": "monthly_limit_reached",
            },
            status_code=429,
            headers={"Retry-After": "3600"},
        )

    source = body.source
    logger.info(
        f"Web job creation request received — "
        f"user={user.email}, "
        f"source={source.uri}, "
        f"type={source.type.value}, "
        f"operations={len(body.pipeline)}"
    )

    # Resolve uploads/ sources. Uploads may live under an anonymous session key
    # (no JWT upload path exists yet), so resolve by ID unscoped.
    source_uri = source.uri
    if source_uri and source_uri.startswith("uploads/"):
        try:
            upload_id = uuid.UUID(source_uri.removeprefix("uploads/"))
        except ValueError:
            raise BadRequest(f"Unknown upload source: {source_uri!r}") from None
        upload = await upload_service.resolve_for_web_job(upload_id)
        source_uri = upload.uri

    # Run validation gates + build spec — same rules as public POST /v1/job.
    spec = validate_and_build_pipeline(
        source=source_uri,
        source_type=source.type.value,
        pipeline=[op.model_dump() for op in body.pipeline],
    )
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

    outputs = [o.model_dump() for o in body.outputs]
    selection = source.selection.model_dump() if source.selection else None
    job = await job_service.create_job(
        api_key_id=web_key.id,
        source_uri=source_uri,
        source_type=source.type.value,
        pipeline_spec=spec,
        outputs=outputs,
        selection=selection,
        origin="web",
    )
    logger.info(f"Web job {job.id!s} created — user={user.email}, status={job.status}")

    await event_service.emit(
        event_type=EventType.JOB_CREATED,
        resource_id=job.id,
        data={
            "job_id": str(job.id),
            "status": job.status,
            "source_uri": job.source_uri,
            "source_type": job.source_type,
        },
        api_key_id=web_key.id,
    )

    from celery_app.orchestrator import process_job

    process_job.apply_async(args=[str(job.id)], task_id=str(job.id))
    logger.info(f"Web job {job.id!s} dispatched to orchestrator")

    return success(
        data=JobResponse(**job.to_dict()).model_dump(),
        message="Job created",
        status_code=status.HTTP_201_CREATED,
    )


@internal_job_route.get("")
async def list_jobs(
    user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    api_key_id: uuid.UUID | None = Query(None, description="Filter by API key"),
    status_filter: str | None = Query(None, alias="status"),
    origin: str | None = Query(None, alias="origin"),
    created_after: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """List all jobs belonging to the authenticated user, across all API keys."""
    jobs, total = await job_service.list_jobs_by_user(
        user_id=user.id,
        status=status_filter,
        api_key_id=api_key_id,
        origin=origin,
        created_after=created_after,
        page=page,
        per_page=per_page,
    )

    # Enrich jobs with api_key_name
    from sqlalchemy import select

    from src.model.api import ApiKey

    # Batch-load API key names for the jobs in this page
    api_key_ids = list({j.api_key_id for j in jobs})
    api_key_names = {}
    if api_key_ids:
        # Use the same session from the job_service
        result = await job_service.db.execute(
            select(ApiKey.id, ApiKey.name).where(ApiKey.id.in_(api_key_ids))
        )
        api_key_names = {row[0]: row[1] for row in result.all()}

    enriched = [
        InternalJobResponse(
            **j.to_dict(),
            api_key_name=api_key_names.get(j.api_key_id),
        )
        for j in jobs
    ]

    return success(
        data=InternalJobListResponse(
            total=total,
            page=page,
            per_page=per_page,
            jobs=enriched,
        ).model_dump(),
    )


@internal_job_route.get("/counts")
async def get_job_counts(
    user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    api_key_id: uuid.UUID | None = Query(None, description="Filter by API key"),
    origin: str | None = Query(None, alias="origin"),
):
    """Return job counts grouped by status for the authenticated user."""
    counts = await job_service.get_counts_by_status(
        user_id=user.id,
        api_key_id=api_key_id,
        origin=origin,
    )
    return success(data=counts)


@internal_job_route.get("/{job_id}")
async def get_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Get a single job with steps, verifying it belongs to the user."""
    job = await job_service.get_job_detail_by_user(user_id=user.id, job_id=job_id)
    if not job:
        from src.core.exception_base import NotFoundError
        logger.warning(f"Job {job_id} not found")
        raise NotFoundError("Job not found")

    # Fetch API key name
    from sqlalchemy import select

    from src.model.api import ApiKey

    result = await job_service.db.execute(
        select(ApiKey.name).where(ApiKey.id == job.api_key_id)
    )
    api_key_name = result.scalar_one_or_none()

    # Sort steps by step_index to ensure correct ordering [0, 1, 2, ...]
    # This allows the dashboard to use steps[steps.length - 1] to reliably get the final step
    sorted_job_steps = sorted(job.job_steps or [], key=lambda s: s.step_index)
    steps = [
        {
            **s.to_dict(),
            # Extract output_url from the output_artifact JSON blob if present
            "output_url": s.output_artifact.get("output_url") if s.output_artifact else None,
        }
        for s in sorted_job_steps
    ]

    data = InternalJobDetailResponse(
        **job.to_dict(),
        api_key_name=api_key_name,
        steps=steps,
    )

    return success(data=data.model_dump())


@internal_job_route.get("/{job_id}/download")
async def download_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Redirect to a presigned R2 URL for the job's final output.

    The job is verified to belong to the authenticated user via JWT session.
    The presigned URL is scoped to the job's owning API key.
    """
    job = await job_service.get_job_detail_by_user(user_id=user.id, job_id=job_id)
    if not job:
        from src.core.exception_base import NotFoundError
        raise NotFoundError("Job not found")

    presigned_url = await job_service.generate_download_url(job_id, job.api_key_id)
    return success(data={"url": presigned_url})


@internal_job_route.patch("/{job_id}/status")
async def update_job_status(
    job_id: uuid.UUID,
    body: RetryJobRequest,
    user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Update a job's status — supports retry action.

    Retry resets the job to PENDING, increments retry_count, clears error,and deletes existing steps so the orchestrator recreates them.
    If max retries are exceeded, job goes to DEAD state.
    """
    if body.action != "retry":
        from src.core.exception_base import BadRequest
        raise BadRequest(f"Unknown action: {body.action}")

    job, steps, api_key_name = await job_service.retry_job_and_return(job_id, user.id)

    data = InternalJobDetailResponse(
        **job.to_dict(),
        api_key_name=api_key_name,
        steps=steps,
    )

    return success(data=data.model_dump())
