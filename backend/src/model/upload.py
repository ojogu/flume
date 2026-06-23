import enum

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import BaseModel


class UploadStatus(str, enum.Enum):
    UNATTACHED = "unattached"
    ATTACHED = "attached"


class Upload(BaseModel):
    """Uploaded file — tracks lifecycle (unattached → attached). Cleanup sweep deletes unattached older than 24h."""
    api_key_id = sa.Column(
        sa.UUID,
        sa.ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=False,
    )
    uri = sa.Column(sa.Text, nullable=False)
    status = sa.Column(
        sa.String,
        nullable=False,
        default=UploadStatus.UNATTACHED.value,
    )
    original_filename = sa.Column(sa.Text, nullable=True)
    file_size = sa.Column(sa.BigInteger, nullable=True)

    api_key = relationship("ApiKey", back_populates="uploads")
