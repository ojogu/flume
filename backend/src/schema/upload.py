from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel

from src.model.upload import UploadStatus


class UploadResponse(BaseModel):
    """Response returned after a successful file upload — includes storage URI for use in POST /job."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    api_key_id: uuid.UUID
    uri: str
    status: UploadStatus
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
