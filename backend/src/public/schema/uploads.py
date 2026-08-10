import uuid
from datetime import datetime

from pydantic import BaseModel

from src.model.upload import UploadStatus


class PresignedUploadResult(BaseModel):
    """Flat result from create_presigned_upload — no ORM refs, just what the route needs."""
    upload_id: uuid.UUID
    object_key: str
    presigned_url: str
    expires_at: datetime


# ── Phase 1: Request a presigned upload URL ──────────────────────────
# Client tells us the filename and type; server generates a time-limited
# presigned PUT URL. The file goes directly from client to R2 — the server
# never touches the bytes (see ADR-005).

class PresignUploadRequest(BaseModel):
    original_filename: str
    content_type: str
    file_size: int | None = None


class PresignUploadResponse(BaseModel):
    upload_id: uuid.UUID
    presigned_url: str
    object_key: str
    expires_at: datetime


# ── Phase 2: Confirm the upload landed in R2 ─────────────────────────
# Client calls this after the PUT succeeds. Server verifies via head_object,
# records real metadata, flips status to UNATTACHED.

class UploadResponse(BaseModel):
    """Returned after Phase 2 (complete) — the upload is now ready for job creation."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    api_key_id: uuid.UUID
    uri: str
    status: UploadStatus
    original_filename: str | None = None
    file_size: int | None = None
    content_type: str | None = None
    etag: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
