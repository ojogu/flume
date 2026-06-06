from .base import BaseModel
import sqlalchemy as sa
from sqlalchemy.orm import relationship


class Projects(BaseModel):
    pass 


class User(BaseModel):
    google_id = sa.Column(sa.String, nullable=True)
    refresh_token = sa.Column(sa.Text, nullable=True)
    access_token = sa.Column(sa.Text, nullable=True)
    email = sa.Column(sa.String, unique=True, nullable=False)
    email_verified = sa.Column(sa.Boolean, default=False, nullable=False)
    onboarded = sa.Column(sa.Boolean, default=False, nullable=False)
    name = sa.Column(sa.String, nullable=True)
    picture = sa.Column(sa.Text, nullable=True)
    first_name = sa.Column(sa.String, nullable=True)
    last_name = sa.Column(sa.String, nullable=True)
    is_active = sa.Column(sa.Boolean, default=False, nullable=False)
    auth_provider = sa.Column(sa.String, nullable=False)

    #relationship
    #parent:user, child:api-key
    api_keys = relationship("ApiKey", back_populates="user")

