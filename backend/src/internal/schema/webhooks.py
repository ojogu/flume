from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel


class CreateInternalWebhookRequest(BaseModel):
    """Request to create a webhook subscription via the internal API.

    ``api_key_id`` is required — the webhook is scoped to a specific API key.
    """

    api_key_id: uuid.UUID
    url: str
    events: list[str] = ["*"]


class UpdateInternalWebhookRequest(BaseModel):
    """Partial update for a webhook subscription."""

    url: Optional[str] = None
    events: Optional[list[str]] = None
    is_active: Optional[bool] = None


class InternalWebhookResponse(BaseModel):
    """Webhook subscription response for the internal API — includes api_key_name."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    api_key_id: uuid.UUID
    api_key_name: Optional[str] = None
    url: str
    events: list
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InternalWebhookCreatedResponse(InternalWebhookResponse):
    """Returned once at creation — includes the plaintext secret."""

    secret: str


class InternalWebhookDeliveryResponse(BaseModel):
    """Webhook delivery record for the internal API."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    subscription_id: uuid.UUID
    event_type: str
    payload: dict
    status: str
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    attempts: int
    next_retry_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
