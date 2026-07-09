from datetime import datetime
import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship

from .base import BaseModel


class JobStatus(str, enum.Enum):
    # non-terminal
    PENDING = "pending" #Job created, queued, not picked up by a worker yet
    PROCESSING = "processing" #	Worker is actively downloading/processing
    
    # terminal
    SUCCEEDED = "succeeded" #Everything completed successfully — all pipeline steps/download passed
    PARTIAL_SUCCESS = "partial_success" #Some entries in a playlist failed but at least one succeeded
    FAILED = "failed" #Job could not complete (download error, FFmpeg failure, size limit exceeded, etc.)


TERMINAL_JOB_STATUSES = {JobStatus.SUCCEEDED, JobStatus.PARTIAL_SUCCESS, JobStatus.FAILED} #once a job reaches any of these, no further processing occurs.


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
    api_key_id: Mapped[uuid.UUID] = sa.Column(
        sa.UUID,
        sa.ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = sa.Column(
        sa.String,
        nullable=False,
        default=JobStatus.PENDING.value,
    )
    source_uri: Mapped[str] = sa.Column(sa.Text, nullable=False)
    source_type: Mapped[str] = sa.Column(sa.String, nullable=False)
    pipeline_steps: Mapped[dict | None] = sa.Column(JSONB, nullable=True)
    outputs: Mapped[dict | None] = sa.Column(JSONB, nullable=True)
    # user's playlist entry selection (1-based ints); null = process all entries
    selection: Mapped[dict | None] = sa.Column(JSONB, nullable=True)
    # SourceInfo + MediaInfo stored after download; FFmpeg pipeline reads this
    # instead of running ffprobe on the downloaded file.  Null until the worker
    # completes the download/extraction phase.
    source_metadata: Mapped[dict | None] = sa.Column(JSONB, nullable=True)
    error: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
    completed_at: Mapped[datetime | None] = sa.Column(sa.DateTime(timezone=True), nullable=True)

    # 1-based position within a playlist (null for non-playlist jobs)
    playlist_entry_index: Mapped[int | None] = sa.Column(sa.Integer, nullable=True)

    # optional self-referential FK for playlist fan-out children
    parent_job_id: Mapped[uuid.UUID | None] = sa.Column(
        sa.UUID,
        sa.ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    api_key: Mapped["ApiKey"] = relationship("ApiKey", back_populates="jobs")
    job_steps: Mapped[list["JobStep"]] = relationship("JobStep", back_populates="job")
    # child jobs (playlist fan-out); parent side of the self-referential relationship
    children: Mapped[list["Job"]] = relationship("Job", backref="parent", remote_side="Job.id")


class JobStep(BaseModel):
    """Per-step execution record — tracks input/output artifacts and error detail for each pipeline step."""
    job_id: Mapped[uuid.UUID] = sa.Column(
        sa.UUID,
        sa.ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_index: Mapped[int] = sa.Column(sa.Integer, nullable=False)
    operation: Mapped[str] = sa.Column(sa.Text, nullable=False)
    status: Mapped[str] = sa.Column(
        sa.String,
        nullable=False,
        default=StepStatus.PENDING.value,
    )
    input_artifact: Mapped[dict | None] = sa.Column(JSONB, nullable=True)
    output_artifact: Mapped[dict | None] = sa.Column(JSONB, nullable=True)
    error: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
    started_at: Mapped[datetime | None] = sa.Column(sa.DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = sa.Column(sa.DateTime(timezone=True), nullable=True)

    job: Mapped["Job"] = relationship("Job", back_populates="job_steps")
