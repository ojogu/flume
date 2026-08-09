import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse

from src.core.dependency import get_current_user, get_job_service
from src.utils.log import get_logger

logger = get_logger(__name__)
from src.internal.schema.jobs import (
    InternalJobDetailResponse,
    InternalJobListResponse,
    InternalJobResponse,
)
from src.model.user import User
from src.service.jobs import JobService
from src.utils.response import success

# ── Internal job routes (JWT authenticated) ──────────────────────────────────
# Dashboard-facing endpoints for viewing jobs across all of a user's API keys.
# The user's identity comes from the JWT, not from an API key.

internal_job_route = APIRouter(prefix="/jobs", tags=["internal-jobs"])


def _enrich_job(job, api_key_name: str | None = None) -> dict:
    """Build InternalJobResponse dict, attaching api_key_name if available."""
    data = job.to_dict()
    data["api_key_name"] = api_key_name
    return InternalJobResponse(**data).model_dump()


@internal_job_route.get("")
async def list_jobs(
    user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    api_key_id: uuid.UUID | None = Query(None, description="Filter by API key"),
    status_filter: str | None = Query(None, alias="status"),
    created_after: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """List all jobs belonging to the authenticated user, across all API keys."""
    jobs, total = await job_service.list_jobs_by_user(
        user_id=user.id,
        status=status_filter,
        api_key_id=api_key_id,
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

    steps = [
        {
            **s.to_dict(),
            "output_url": s.output_artifact.get("output_url") if s.output_artifact else None,
        }
        for s in (job.job_steps or [])
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
