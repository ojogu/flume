from fastapi import APIRouter, Depends, status

from src.core.dependency import get_api_key_from_header, get_job_service, get_upload_service
from src.model.api import ApiKey
from src.schema.job import CreateJobRequest, JobResponse
from src.model.upload import UploadStatus
from src.service.jobs import JobService
from src.service.upload import UploadService
from src.service.validation import validate_and_build_pipeline
from src.utils.response import success

job_route = APIRouter(prefix="/job", tags=["jobs"])


@job_route.post("")
async def create_job(
    body: CreateJobRequest,
    api_key: ApiKey = Depends(get_api_key_from_header),
    job_service: JobService = Depends(get_job_service),
    upload_service: UploadService = Depends(get_upload_service),
):
    source = body.source

    # Check if the source URI is a prior upload via /upload → mark attached so cleanup sweep doesn't delete it
    upload = await upload_service.find_by_uri(source.uri, api_key.id)
    if upload and upload.status == UploadStatus.UNATTACHED.value:
        await upload_service.attach_upload(upload.id, api_key.id)

    # Run 6 validation gates (registry → params → types → terminal → build spec)
    spec = validate_and_build_pipeline(
        source=source.uri,
        source_type=source.type.value,
        pipeline=[op.model_dump() for op in body.pipeline],
    )
    # Persist the job in pending state with the enriched pipeline spec
    job = await job_service.create_job(
        api_key_id=api_key.id,
        source_uri=source.uri,
        source_type=source.type.value,
        pipeline_spec=spec,
    )
    # Wrap in standard {status, message, data} envelope with HTTP 201
    return success(
        data=JobResponse(**job.to_dict()).model_dump(),
        message="Job created",
        status_code=status.HTTP_201_CREATED,
    )
