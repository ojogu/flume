import enum

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import BaseModel


class UploadStatus(str, enum.Enum):
    # ── Lifecycle ──────────────────────────────────────────────────────
    # PENDING     — Presigned URL issued, waiting for client to upload to R2
    # UNATTACHED  — File confirmed in R2 via head_object, ready for job attach
    # ATTACHED    — Linked to a job, protected from cleanup sweep
    PENDING = "pending"
    UNATTACHED = "unattached"
    ATTACHED = "attached"


class Upload(BaseModel):
    """Uploaded file — tracks lifecycle (pending → unattached → attached).
    Cleanup sweep deletes pending + unattached older than 24h, and removes
    the orphaned R2 object too."""
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
    # Populated by head_object in Phase 2 (complete_upload) — the real content-type and etag from R2, not the client's declared values.
    content_type = sa.Column(sa.Text, nullable=True)
    etag = sa.Column(sa.Text, nullable=True)

    api_key = relationship("ApiKey", back_populates="uploads")
