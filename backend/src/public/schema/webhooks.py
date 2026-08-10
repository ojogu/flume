import uuid
from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel

from src.schema.event import EventEnvelope


class CreateWebhookSubscription(BaseModel):
    url: AnyHttpUrl
    events: list[str] = ["*"]


class UpdateWebhookSubscription(BaseModel):
    url: AnyHttpUrl | None = None
    events: list[str] | None = None
    is_active: bool | None = None


class WebhookSubscriptionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    url: str
    events: list
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WebhookSubscriptionCreatedResponse(WebhookSubscriptionResponse):
    secret: str


class WebhookDeliveryResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    subscription_id: uuid.UUID
    event_type: str
    payload: EventEnvelope
    status: str
    response_code: int | None = None
    response_body: str | None = None
    attempts: int
    next_retry_at: datetime | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None
