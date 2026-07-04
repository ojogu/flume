from fastapi import APIRouter, Depends, status

from src.core.dependency import get_api_key_from_header, get_job_service, get_upload_service
from src.model.api import ApiKey
from src.schema.job import CreateJobRequest, JobResponse
from src.model.upload import UploadStatus
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
    logger.info(
        f"Pipeline validation passed — "
        f"{len(spec)} steps: {[s['operation'] for s in spec]}"
    )

    # Persist the job in pending state with the enriched pipeline spec and outputs
    outputs = [o.model_dump() for o in body.outputs]
    job = await job_service.create_job(
        api_key_id=api_key.id,
        source_uri=source.uri,
        source_type=source.type.value,
        pipeline_spec=spec,
        outputs=outputs,
    )

    logger.info(f"Job {job.id} created — status={job.status}, source={job.source_uri}")

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
