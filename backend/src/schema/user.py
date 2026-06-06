from typing import Optional
from pydantic import BaseModel


class CreateUser(BaseModel):
    google_id: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    email: str
    email_verified: bool = False
    oauth_verified: bool = False
    onboarded: bool = False
    name: Optional[str] = None
    picture: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UpdateUser(BaseModel):
    google_id: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    oauth_verified: Optional[bool] = None
    onboarded: Optional[bool] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None