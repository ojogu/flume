from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field

from src.model.event import EventType


# ── Event data models ───────────────────────────────────────────────────


class JobCreatedData(BaseModel):
    """Payload for ``job.created`` events."""

    job_id: str
    status: str
    source_uri: str
    source_type: str


class JobProcessingData(BaseModel):
    """Payload for ``job.processing`` events."""

    job_id: str
    status: str
    source_uri: str
    source_type: str


class JobCompletedData(BaseModel):
    """Payload for ``job.completed`` events."""

    job_id: str
    status: str
    source_uri: str
    source_type: str
    source_metadata: dict[str, Any] | None = None
    error: str | None = None


class JobFailedData(BaseModel):
    """Payload for ``job.failed`` events."""

    job_id: str
    status: str
    error: str


class JobCancelledData(BaseModel):
    """Payload for ``job.cancelled`` events."""

    job_id: str
    status: str
    error: str | None = None


class StepStartedData(BaseModel):
    """Payload for ``step.started`` events."""

    step_id: str
    job_id: str
    operation: str
    step_index: int


class StepCompletedData(BaseModel):
    """Payload for ``step.completed`` events."""

    step_id: str
    job_id: str
    operation: str
    step_index: int
    output_artifact: dict[str, Any]


class StepFailedData(BaseModel):
    """Payload for ``step.failed`` events."""

    step_id: str
    job_id: str
    operation: str
    step_index: int
    error: str


class PingData(BaseModel):
    """Payload for ``ping`` test events."""

    message: str


# ── Envelope (discriminated union on type) ──────────────────────────────


class _BaseEnvelope(BaseModel):
    """Base for all event envelopes — shared fields only."""

    id: str
    created_at: datetime


class JobCreatedEnvelope(_BaseEnvelope):
    type: Literal[EventType.JOB_CREATED] = EventType.JOB_CREATED
    data: JobCreatedData


class JobProcessingEnvelope(_BaseEnvelope):
    type: Literal[EventType.JOB_PROCESSING] = EventType.JOB_PROCESSING
    data: JobProcessingData


class JobCompletedEnvelope(_BaseEnvelope):
    type: Literal[EventType.JOB_COMPLETED] = EventType.JOB_COMPLETED
    data: JobCompletedData


class JobFailedEnvelope(_BaseEnvelope):
    type: Literal[EventType.JOB_FAILED] = EventType.JOB_FAILED
    data: JobFailedData


class JobCancelledEnvelope(_BaseEnvelope):
    type: Literal[EventType.JOB_CANCELLED] = EventType.JOB_CANCELLED
    data: JobCancelledData


class StepStartedEnvelope(_BaseEnvelope):
    type: Literal[EventType.STEP_STARTED] = EventType.STEP_STARTED
    data: StepStartedData


class StepCompletedEnvelope(_BaseEnvelope):
    type: Literal[EventType.STEP_COMPLETED] = EventType.STEP_COMPLETED
    data: StepCompletedData


class StepFailedEnvelope(_BaseEnvelope):
    type: Literal[EventType.STEP_FAILED] = EventType.STEP_FAILED
    data: StepFailedData


class PingEnvelope(_BaseEnvelope):
    type: Literal[EventType.PING] = EventType.PING
    data: PingData


EventEnvelope = Annotated[
    Union[
        JobCreatedEnvelope,
        JobProcessingEnvelope,
        JobCompletedEnvelope,
        JobFailedEnvelope,
        JobCancelledEnvelope,
        StepStartedEnvelope,
        StepCompletedEnvelope,
        StepFailedEnvelope,
        PingEnvelope,
    ],
    Field(discriminator="type"),
]
