import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped

from .base import BaseModel


# ── Platform model ────────────────────────────────────────────────────────────
# Curated list of supported media platforms. The slug maps to yt-dlp's
# extractor_key (lowercased) and is validated during job orchestration.
# Admin CRUD manages the lifecycle; the public API exposes active platforms
# for discovery. Platforms are standalone reference data — no FK to jobs.

class Platform(BaseModel):
    """Supported media platform — curated via admin CRUD, validated during job processing."""

    slug: Mapped[str] = sa.Column(
        sa.String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    name: Mapped[str] = sa.Column(
        sa.String(128),
        nullable=False,
    )
    url: Mapped[str] = sa.Column(
        sa.String(512),
        nullable=False,
    )
    is_active: Mapped[bool] = sa.Column(
        sa.Boolean,
        nullable=False,
        default=True,
    )
    content_types: Mapped[dict] = sa.Column(
        JSONB,
        nullable=False,
        default=["single"],
    )
    requires_login: Mapped[bool] = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
    )
    supports_live: Mapped[bool] = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
    )
    description: Mapped[str | None] = sa.Column(
        sa.Text,
        nullable=True,
    )
    limitations: Mapped[str | None] = sa.Column(
        sa.Text,
        nullable=True,
    )
    logo_url: Mapped[str | None] = sa.Column(
        sa.String(512),
        nullable=True,
    )
    sort_order: Mapped[int] = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
    )
