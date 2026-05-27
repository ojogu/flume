from .base import BaseModel
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship


class ApiKey(BaseModel):
    user_id = sa.Column(
        sa.UUID,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = sa.Column(sa.Text, nullable=False)
    key_hash = sa.Column(sa.Text, nullable=False, unique=True)
    prefix = sa.Column(sa.Text, nullable=False)
    scopes = sa.Column(ARRAY(sa.Text), nullable=False)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    last_used_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    revoked_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    #relationship
    user = relationship("User", back_populates="api_keys")

