from fastapi import APIRouter, Depends, File, UploadFile, status

from src.core.dependency import get_api_key_from_header, get_upload_service
from src.model.api import ApiKey
from src.schema.upload import UploadResponse
from src.service.upload import UploadService
from src.utils.response import success

upload_route = APIRouter(prefix="/uploads", tags=["uploads"])


@upload_route.post("")
# Stores file to disk, returns storage URI for use in POST /job
async def create_upload(
    file: UploadFile = File(...),
    api_key: ApiKey = Depends(get_api_key_from_header),
    upload_service: UploadService = Depends(get_upload_service),
):
    upload = await upload_service.create_upload(
        api_key_id=api_key.id,
        file=file,
    )
    return success(
        data=UploadResponse(**upload.to_dict()).model_dump(),
        message="Upload created",
        status_code=status.HTTP_201_CREATED,
    )
