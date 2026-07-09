from datetime import datetime
import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from .base import BaseModel


class ApiKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


# ApiKey model — SHA-256 hashed keys with status lifecycle (active → revoked)

class ApiKey(BaseModel):
    user_id: Mapped[uuid.UUID] = sa.Column(
        sa.UUID,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = sa.Column(sa.String, nullable=False)
    key_hash: Mapped[str] = sa.Column(sa.String(64), nullable=False, unique=True)
    key_prefix: Mapped[str] = sa.Column(sa.String(16), nullable=False)
    status: Mapped[str] = sa.Column(sa.String, nullable=False, default=ApiKeyStatus.ACTIVE.value)
    expires_at: Mapped[datetime | None] = sa.Column(sa.DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = sa.Column(sa.DateTime(timezone=True), nullable=True)

    # Bidirectional: ApiKey.user → User.api_keys
    user: Mapped["User"] = relationship("User", back_populates="api_keys")
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="api_key")
    uploads: Mapped[list["Upload"]] = relationship("Upload", back_populates="api_key")
    webhook_subscriptions: Mapped[list["WebhookSubscription"]] = relationship("WebhookSubscription", back_populates="api_key")

