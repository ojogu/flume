from datetime import datetime
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field, HttpUrl

from src.model.job import SourceType, JobStatus


class PipelineOperation(BaseModel):
    operation: str
    params: dict[str, Any] = {}


class CreateJobRequest(BaseModel):
    source: HttpUrl
    source_type: SourceType
    pipeline: list[PipelineOperation] = Field(min_length=1)


class JobResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    api_key_id: uuid.UUID
    status: JobStatus
    source_uri: str
    source_type: SourceType
    pipeline_steps: Optional[list] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
