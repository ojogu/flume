from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field

from src.model.job import SourceType, JobStatus


class OutputType(str, Enum):
    GENERATE_DOWNLOAD_LINK = "generate_download_link"
    UPLOAD = "upload"


class SourceObject(BaseModel):
    """Source media — type (video/audio) and URI (external URL or upload storage URI)."""
    type: SourceType
    uri: str


class PipelineOperation(BaseModel):
    """A single pipeline step — operation name and optional params."""
    operation: str
    params: dict[str, Any] = {}


class OutputBody(BaseModel):
    """A delivery target for the pipeline's final artifact."""
    type: OutputType
    params: dict[str, Any] = {}


class CreateJobRequest(BaseModel):
    """POST /job request body — source media + pipeline of operations + delivery outputs."""
    source: SourceObject
    pipeline: list[PipelineOperation] = Field(min_length=1)
    outputs: list[OutputBody] = Field(
        default_factory=lambda: [OutputBody(type=OutputType.GENERATE_DOWNLOAD_LINK)]
    )


class JobResponse(BaseModel):
    """POST /job response — created job with enriched pipeline spec."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    api_key_id: uuid.UUID
    status: JobStatus
    source_uri: str
    source_type: SourceType
    pipeline_steps: Optional[list] = None
    outputs: Optional[list] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
