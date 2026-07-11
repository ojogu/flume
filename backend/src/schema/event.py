from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel


class CreateWebhookSubscription(BaseModel):
    url: str
    events: list[str] = ["*"]


class UpdateWebhookSubscription(BaseModel):
    url: Optional[str] = None
    events: Optional[list[str]] = None
    is_active: Optional[bool] = None


class WebhookSubscriptionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    url: str
    events: list
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WebhookSubscriptionCreatedResponse(WebhookSubscriptionResponse):
    secret: str


class WebhookDeliveryResponse(BaseModel):
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


class EventEnvelope(BaseModel):
    """The JSON body POSTed to the subscriber webhook endpoint."""

    id: uuid.UUID
    type: str
    created_at: datetime
    data: dict
