from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.core.dependency import get_api_key_from_header, get_upload_service
from src.model.api import ApiKey
from src.public.schema.uploads import (
    PresignUploadRequest,
    PresignUploadResponse,
    UploadResponse,
)
from src.service.api import WEB_SESSION_KEY_PREFIX
from src.service.upload import UploadService
from src.utils.response import success

upload_route = APIRouter(prefix="/uploads", tags=["uploads"])

WEB_SESSION_MAX_UPLOAD_BYTES = 100 * 1024 * 1024  # 100 MB


@upload_route.post("/presign", status_code=status.HTTP_201_CREATED)
# ── Phase 1: Issue a presigned upload URL ──────────────────────────
# The client requests a presigned URL, uploads the file directly
# to R2, and then confirms with /complete. The server never touches the file bytes — no bandwidth, no disk I/O.
async def presign_upload(
    body: PresignUploadRequest,
    api_key: ApiKey = Depends(get_api_key_from_header),
    upload_service: UploadService = Depends(get_upload_service),
):
    # Session key file size limit: 100 MB
    if api_key.key_prefix.startswith(f"{WEB_SESSION_KEY_PREFIX}_"):
        if body.file_size and body.file_size > WEB_SESSION_MAX_UPLOAD_BYTES:
            return JSONResponse(
                content={
                    "status": "error",
                    "message": f"File too large for anonymous upload. Maximum is 100 MB.",
                    "error_code": "file_too_large",
                },
                status_code=413,
            )
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
