import enum

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel


class JobStatus(str, enum.Enum):
    # non-terminal
    PENDING = "pending"
    PROCESSING = "processing"
    # terminal
    SUCCEEDED = "succeeded"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"


TERMINAL_JOB_STATUSES = {JobStatus.SUCCEEDED, JobStatus.PARTIAL_SUCCESS, JobStatus.FAILED}


class SourceType(str, enum.Enum):
    VIDEO = "video"
    AUDIO = "audio"


class StepStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class Job(BaseModel):
    """Persisted job record — created on POST /job, tracks lifecycle from pending through complete/failed."""
    api_key_id = sa.Column(
        sa.UUID,
        sa.ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = sa.Column(
        sa.String,
        nullable=False,
        default=JobStatus.PENDING.value,
    )
    source_uri = sa.Column(sa.Text, nullable=False)
    source_type = sa.Column(sa.String, nullable=False)
    pipeline_steps = sa.Column(JSONB, nullable=True)
    outputs = sa.Column(JSONB, nullable=True)
    # SourceInfo + MediaInfo stored after download; FFmpeg pipeline reads this
    # instead of running ffprobe on the downloaded file.  Null until the worker
    # completes the download/extraction phase.
    source_metadata = sa.Column(JSONB, nullable=True)
    error = sa.Column(sa.Text, nullable=True)
    completed_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    # 1-based position within a playlist (null for non-playlist jobs)
    playlist_entry_index = sa.Column(sa.Integer, nullable=True)

    # optional self-referential FK for playlist fan-out children
    parent_job_id = sa.Column(
        sa.UUID,
        sa.ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    api_key = relationship("ApiKey", back_populates="jobs")
    job_steps = relationship("JobStep", back_populates="job")
    # child jobs (playlist fan-out); parent side of the self-referential relationship
    children = relationship("Job", backref="parent", remote_side="Job.id")


class JobStep(BaseModel):
    """Per-step execution record — tracks input/output artifacts and error detail for each pipeline step."""
    job_id = sa.Column(
        sa.UUID,
        sa.ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_index = sa.Column(sa.Integer, nullable=False)
    operation = sa.Column(sa.Text, nullable=False)
    status = sa.Column(
        sa.String,
        nullable=False,
        default=StepStatus.PENDING.value,
    )
    input_artifact = sa.Column(JSONB, nullable=True)
    output_artifact = sa.Column(JSONB, nullable=True)
    error = sa.Column(sa.Text, nullable=True)
    started_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    completed_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    job = relationship("Job", back_populates="job_steps")
