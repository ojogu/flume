import enum

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


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
    completed_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    api_key = relationship("ApiKey", back_populates="jobs")
    job_steps = relationship("JobStep", back_populates="job")


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
