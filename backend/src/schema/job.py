from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field, model_validator

from src.model.job import SourceType, JobStatus
from src.schema.download import FormatPreference, PlaylistSelection, AUDIO_SAFE_FORMATS


class OutputType(str, Enum):
    GENERATE_DOWNLOAD_LINK = "generate_download_link"
    UPLOAD = "upload"


class SourceObject(BaseModel):
    """Source media — type, URI, optional playlist selection, and quality format preference."""
    type: SourceType
    uri: str
    # optional playlist entry filter — surface-level validation only (entries are positive ints);
    # actual playlist detection and index-bounds checking happen in the async worker
    selection: PlaylistSelection | None = None
    # download quality preference — "best" by default; resolutions are rejected for audio sources
    format: FormatPreference = FormatPreference.BEST

    @model_validator(mode="after")
    def _validate_format_for_source_type(self):
        # resolution formats (480p, 720p, etc.) only make sense for video;
        # audio sources can only use "best" or "smallest"
        if self.type == SourceType.AUDIO and self.format not in AUDIO_SAFE_FORMATS:
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
