import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

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
    api_key_id: Mapped[uuid.UUID] = sa.Column(
        sa.UUID,
        sa.ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=False,
    )
    uri: Mapped[str] = sa.Column(sa.Text, nullable=False)
    status: Mapped[str] = sa.Column(
        sa.String,
        nullable=False,
        default=UploadStatus.UNATTACHED.value,
    )
    original_filename: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
    file_size: Mapped[int | None] = sa.Column(sa.BigInteger, nullable=True)
    # Populated by head_object in Phase 2 (complete_upload) — the real content-type and etag from R2, not the client's declared values.
    content_type: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
    etag: Mapped[str | None] = sa.Column(sa.Text, nullable=True)

    api_key: Mapped["ApiKey"] = relationship("ApiKey", back_populates="uploads")
