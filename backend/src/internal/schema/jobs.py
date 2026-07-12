from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel

from src.model.job import JobStatus, SourceType


class InternalJobResponse(BaseModel):
    """Job response for the internal/dashboard API — includes api_key_name."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    api_key_id: uuid.UUID
    api_key_name: Optional[str] = None
    status: JobStatus
    source_uri: str
    source_type: SourceType
    pipeline_steps: Optional[list] = None
    outputs: Optional[list] = None
    selection: Optional[dict] = None
    source_metadata: Optional[dict] = None
    error: Optional[str] = None
    parent_job_id: Optional[uuid.UUID] = None
    playlist_entry_index: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InternalStepResponse(BaseModel):
    """A single pipeline step embedded in job detail responses."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    job_id: uuid.UUID
    step_index: int
    operation: str
    status: str
    input_artifact: Optional[dict] = None
    output_artifact: Optional[dict] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InternalJobDetailResponse(InternalJobResponse):
    """Single job detail — includes embedded steps."""

    steps: list[InternalStepResponse] = []


class InternalJobListResponse(BaseModel):
    """Paginated list of jobs for the internal API."""

    total: int
    page: int
    per_page: int
    jobs: list[InternalJobResponse]
