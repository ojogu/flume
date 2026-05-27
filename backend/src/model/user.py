from .base import BaseModel
import sqlalchemy as sa
from sqlalchemy.orm import relationship


class Projects(BaseModel):
    pass 


class User(BaseModel):
    #TODO: set google oauth
    email = sa.Column(unique=True, nullable=False) 
    is_active = sa.Column(unique=True, default=False, nullable=False) 
    auth_provider = sa.Column(nullable=False)

    #relationship
    #parent:user, child:api-key
    api_keys = relationship("ApiKey", back_populates="user")

