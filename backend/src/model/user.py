from datetime import datetime

import sqlalchemy as sa
import uuid
from sqlalchemy.orm import Mapped, relationship

from .base import BaseModel


# User model — profile, OAuth tokens, auth provider; MagicLinkToken for passwordless login

class Project(BaseModel):
    pass


class User(BaseModel):
    google_id: Mapped[str | None] = sa.Column(sa.String, nullable=True)
    refresh_token: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
    access_token: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
    email: Mapped[str] = sa.Column(sa.String, unique=True, nullable=False, index=True)
    email_verified: Mapped[bool] = sa.Column(sa.Boolean, default=False, nullable=False)
    oauth_verified: Mapped[bool] = sa.Column(sa.Boolean, default=False, nullable=False)
    onboarded: Mapped[bool] = sa.Column(sa.Boolean, default=False, nullable=False)
    name: Mapped[str | None] = sa.Column(sa.String, nullable=True)
    picture: Mapped[str | None] = sa.Column(sa.Text, nullable=True)
    first_name: Mapped[str | None] = sa.Column(sa.String, nullable=True)
    last_name: Mapped[str | None] = sa.Column(sa.String, nullable=True)
    is_active: Mapped[bool] = sa.Column(sa.Boolean, default=False, nullable=False)
    auth_provider: Mapped[str] = sa.Column(sa.String, nullable=False)

    # Bidirectional relationship: User.api_keys → ApiKey.user
    api_keys: Mapped[list["ApiKey"]] = relationship("ApiKey", back_populates="user")


class MagicLinkToken(BaseModel):
    token: Mapped[str] = sa.Column(sa.String, unique=True, nullable=False, index=True)
    email: Mapped[str] = sa.Column(sa.String, nullable=False, index=True)
    resend_email_id: Mapped[uuid.UUID | None] = sa.Column(sa.UUID, nullable=True)
    expires_at: Mapped[datetime] = sa.Column(sa.DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = sa.Column(sa.Boolean, default=False, nullable=False)
