from datetime import datetime
import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship

from src.utils.crypto import EncryptedText

from .base import BaseModel


class EventType(str, enum.Enum):
    """All webhook event types emitted by Flume.

    Subscriptions filter on these values (or use ``"*"`` for wildcard).
    """

    JOB_CREATED = "job.created"
    JOB_PROCESSING = "job.processing"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_CANCELLED = "job.cancelled"
    STEP_STARTED = "step.started"
    STEP_COMPLETED = "step.completed"
    STEP_FAILED = "step.failed"


ALL_EVENT_TYPES = {e.value for e in EventType}


class DeliveryStatus(str, enum.Enum):
    """Lifecycle states for a webhook delivery attempt."""

    PENDING = "pending"
    DELIVERED = "delivered"
    EXHAUSTED = "exhausted"


class WebhookSubscription(BaseModel):
    """A webhook subscription — subscriber endpoint, event filter, and HMAC secret."""

    api_key_id: Mapped[uuid.UUID] = sa.Column(
        sa.UUID,
        sa.ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = sa.Column(sa.Text, nullable=False)
    events: Mapped[dict] = sa.Column(JSONB, nullable=False, default=["*"])
    secret: Mapped[str] = sa.Column(EncryptedText, nullable=False)
    is_active: Mapped[bool] = sa.Column(sa.Boolean, default=True)

    api_key: Mapped["ApiKey"] = relationship("ApiKey", back_populates="webhook_subscriptions")
    deliveries: Mapped[list["WebhookDelivery"]] = relationship("WebhookDelivery", back_populates="subscription")


class WebhookDelivery(BaseModel):
    """Delivery attempt record for a single webhook event — tracks retries and subscriber response."""

    subscription_id: Mapped[uuid.UUID] = sa.Column(
        sa.UUID,
        sa.ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = sa.Column(sa.Text, nullable=False)
    payload: Mapped[dict] = sa.Column(JSONB, nullable=False)
    status: Mapped[str] = sa.Column(sa.String, nullable=False, default=DeliveryStatus.PENDING.value)
    response_code: Mapped[int | None] = sa.Column(sa.Integer, nullable=True)
    response_body: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
    attempts: Mapped[int] = sa.Column(sa.Integer, nullable=False, default=0)
    next_retry_at: Mapped[datetime | None] = sa.Column(sa.DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = sa.Column(sa.DateTime(timezone=True), nullable=True)

    subscription: Mapped["WebhookSubscription"] = relationship("WebhookSubscription", back_populates="deliveries")
