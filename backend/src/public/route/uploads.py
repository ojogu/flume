from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.dependency import get_api_key_from_header, get_upload_service
from src.model.api import ApiKey
from src.public.schema.uploads import PresignUploadRequest, PresignUploadResponse, UploadResponse
from src.service.upload import UploadService
from src.utils.response import success

upload_route = APIRouter(prefix="/uploads", tags=["uploads"])


@upload_route.post("/presign", status_code=status.HTTP_201_CREATED)
# ── Phase 1: Issue a presigned upload URL ──────────────────────────
# The client requests a presigned URL, uploads the file directly
# to R2, and then confirms with /complete. The server never touches the file bytes — no bandwidth, no disk I/O.
async def presign_upload(
    body: PresignUploadRequest,
    api_key: ApiKey = Depends(get_api_key_from_header),
    upload_service: UploadService = Depends(get_upload_service),
):
    result = await upload_service.create_presigned_upload(
        api_key_id=api_key.id,
        original_filename=body.original_filename,
        content_type=body.content_type,
        file_size=body.file_size,
    )

    return success(
        data=PresignUploadResponse(
            upload_id=result.upload_id,
            presigned_url=result.presigned_url,
            object_key=result.object_key,
            expires_at=result.expires_at,
        ).model_dump(),
        message="Presigned upload URL generated",
        status_code=status.HTTP_201_CREATED,
    )


@upload_route.post("/{upload_id}/complete")
# ── Phase 2: Confirm the upload landed in R2 ───────────────────────
# The client calls this after PUTting the file to the presigned URL.
# The server verifies via R2 head_object, records the real metadata,
# and flips the upload status to UNATTACHED (ready for job creation).
async def complete_upload(
    upload_id: str,
    api_key: ApiKey = Depends(get_api_key_from_header),
    upload_service: UploadService = Depends(get_upload_service),
):
    upload = await upload_service.complete_upload(
        upload_id=UUID(upload_id),
        api_key_id=api_key.id,
    )

    return success(
        data=UploadResponse(**upload.to_dict()).model_dump(),
        message="Upload confirmed",
    )
