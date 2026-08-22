"""Analytics models for page visit tracking."""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from .base import BaseModel


class PageView(BaseModel):
    """Tracks page visits for analytics — pseudonymous via visitor_hash (SHA-256 of IP + UA + salt)."""

    path: Mapped[str] = sa.Column(sa.Text, nullable=False, index=True)
    visitor_hash: Mapped[str] = sa.Column(sa.String(64), nullable=False, index=True)
    referrer: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
    user_agent: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
