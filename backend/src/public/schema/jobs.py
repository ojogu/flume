import uuid
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

from src.model.job import JobOrigin, JobStatus, SourceType
from src.schema.download import (
    _AUDIO_SAFE_FORMATS,
    _FormatPreference,
    _PlaylistSelection,
)


class OutputType(str, Enum):
    GENERATE_DOWNLOAD_LINK = "generate_download_link"
    UPLOAD = "upload"


class SourceObject(BaseModel):
    """Source media — type, URI, optional playlist selection, and quality format preference."""
    type: SourceType
    uri: str | None = None
    selection: _PlaylistSelection | None = None
    format: _FormatPreference = _FormatPreference.BEST

    @field_validator("uri")
    @classmethod
    def _validate_uri(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if v.startswith("uploads/"):
            return v
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError(
                f"Invalid source URI: {v!r}. Must be a valid HTTP/HTTPS URL or an uploads/ path."
            )
        return v

    @model_validator(mode="after")
    def _validate_format_for_source_type(self):
        # resolution formats (480p, 720p, etc.) only make sense for video;
        # audio sources can only use "best" or "smallest"
        if self.type == SourceType.AUDIO and self.format not in _AUDIO_SAFE_FORMATS:
            raise ValueError(
                f"Format '{self.format.value}' is not valid for audio sources. "
                f"Use 'best' or 'smallest'."
            )
        return self


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
    pipeline: list[PipelineOperation] = Field(default_factory=list)
    outputs: list[OutputBody] = Field(
        default_factory=lambda: [OutputBody(type=OutputType.GENERATE_DOWNLOAD_LINK)]
    )


class JobResponse(BaseModel):
    """POST /job response — created job with enriched pipeline spec."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    api_key_id: uuid.UUID
    status: JobStatus
    source_uri: str | None = None
    source_type: SourceType
    origin: str = JobOrigin.API.value
    pipeline_steps: list | None = None
    outputs: list | None = None
    selection: dict | None = None
    source_metadata: dict | None = None
    title: str | None = None
    error: str | None = None
    parent_job_id: uuid.UUID | None = None
    playlist_entry_index: int | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_title_from_metadata(cls, data: Any) -> Any:
        if isinstance(data, dict) and data.get("title") is None:
            source_meta = data.get("source_metadata", {})
            if isinstance(source_meta, dict):
                source = source_meta.get("source", {})
                if isinstance(source, dict):
                    data["title"] = source.get("title")
        return data


class StepResponse(BaseModel):
    """A single pipeline step embedded in job detail responses."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    job_id: uuid.UUID
    step_index: int
    operation: str
    status: str
    input_artifact: dict | None = None
    output_artifact: dict | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class JobDetailResponse(JobResponse):
    """Single job detail — includes embedded steps."""
    steps: list[StepResponse] = []


class JobListResponse(BaseModel):
    """Paginated list of jobs."""
    total: int
    page: int
    per_page: int
    jobs: list[JobResponse]
