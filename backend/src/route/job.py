from fastapi import APIRouter, Depends, status

from src.core.dependency import get_api_key_from_header, get_job_service
from src.model.api import ApiKey
from src.schema.job import CreateJobRequest, JobResponse
from src.service.jobs import JobService
from src.service.validation import validate_and_build_pipeline
from src.utils.response import success

job_route = APIRouter(prefix="/job", tags=["jobs"])


@job_route.post("")
async def create_job(
    body: CreateJobRequest,
    api_key: ApiKey = Depends(get_api_key_from_header),
    job_service: JobService = Depends(get_job_service),
):
    spec = validate_and_build_pipeline(
        source=str(body.source),
        source_type=body.source_type.value,
        pipeline=[op.model_dump() for op in body.pipeline],
    )
    job = await job_service.create_job(
        api_key_id=api_key.id,
        source_uri=str(body.source),
        source_type=body.source_type.value,
        pipeline_spec=spec,
    )
    return success(
        data=JobResponse(**job.to_dict()).model_dump(),
        message="Job created",
        status_code=status.HTTP_201_CREATED,
    )
