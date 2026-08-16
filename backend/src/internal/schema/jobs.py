import uuid
from datetime import datetime

from pydantic import BaseModel

from src.model.job import JobStatus, SourceType


class RetryJobRequest(BaseModel):
    action: str = "retry"


class InternalJobResponse(BaseModel):
    """Job response for the internal/dashboard API — includes api_key_name."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    api_key_id: uuid.UUID
    api_key_name: str | None = None
    status: JobStatus
    source_uri: str | None
    source_type: SourceType
    pipeline_steps: list | None = None
    outputs: list | None = None
    selection: dict | None = None
    source_metadata: dict | None = None
    error: str | None = None
    parent_job_id: uuid.UUID | None = None
    playlist_entry_index: int | None = None
    retry_count: int = 0
    max_retries: int = 3
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class InternalStepResponse(BaseModel):
    """A single pipeline step embedded in job detail responses."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    job_id: uuid.UUID
    step_index: int
    operation: str
    status: str
    input_artifact: dict | None = None
    output_artifact: dict | None = None
    output_url: str | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class InternalJobDetailResponse(InternalJobResponse):
    """Single job detail — includes embedded steps."""

    steps: list[InternalStepResponse] = []


class InternalJobListResponse(BaseModel):
    """Paginated list of jobs for the internal API."""

    total: int
    page: int
    per_page: int
    jobs: list[InternalJobResponse]
