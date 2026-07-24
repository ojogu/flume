from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel

from src.schema.event import EventEnvelope


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
    payload: EventEnvelope
    status: str
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    attempts: int
    next_retry_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
