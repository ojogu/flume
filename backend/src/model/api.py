import enum

from .base import BaseModel
import sqlalchemy as sa
from sqlalchemy.orm import relationship


class ApiKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


class ApiKey(BaseModel):
    user_id = sa.Column(
        sa.UUID,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = sa.Column(sa.String, nullable=False)
    key_hash = sa.Column(sa.String(64), nullable=False, unique=True)
    key_prefix = sa.Column(sa.String(16), nullable=False)
    status = sa.Column(sa.String, nullable=False, default=ApiKeyStatus.ACTIVE.value)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    last_used_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    # Bidirectional: ApiKey.user → User.api_keys
    user = relationship("User", back_populates="api_keys")
    jobs = relationship("Job", back_populates="api_key")

