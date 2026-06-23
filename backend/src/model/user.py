from .base import BaseModel
import sqlalchemy as sa
from sqlalchemy.orm import relationship


# User model — profile, OAuth tokens, auth provider; MagicLinkToken for passwordless login

class Project(BaseModel):
    pass


class User(BaseModel):
    google_id = sa.Column(sa.String, nullable=True)
    refresh_token = sa.Column(sa.Text, nullable=True)
    access_token = sa.Column(sa.Text, nullable=True)
    email = sa.Column(sa.String, unique=True, nullable=False, index=True)
    email_verified = sa.Column(sa.Boolean, default=False, nullable=False)
    oauth_verified = sa.Column(sa.Boolean, default=False, nullable=False)
    onboarded = sa.Column(sa.Boolean, default=False, nullable=False)
    name = sa.Column(sa.String, nullable=True)
    picture = sa.Column(sa.Text, nullable=True)
    first_name = sa.Column(sa.String, nullable=True)
    last_name = sa.Column(sa.String, nullable=True)
    is_active = sa.Column(sa.Boolean, default=False, nullable=False)
    auth_provider = sa.Column(sa.String, nullable=False)

    # Bidirectional relationship: User.api_keys → ApiKey.user
    api_keys = relationship("ApiKey", back_populates="user")


class MagicLinkToken(BaseModel):
    token = sa.Column(sa.String, unique=True, nullable=False, index=True)
    email = sa.Column(sa.String, nullable=False, index=True)
    resend_email_id = sa.Column(sa.UUID, nullable=True)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    used = sa.Column(sa.Boolean, default=False, nullable=False)

