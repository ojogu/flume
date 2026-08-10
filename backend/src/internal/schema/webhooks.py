import uuid
from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel

from src.schema.event import EventEnvelope


class CreateInternalWebhookRequest(BaseModel):
    """Request to create a webhook subscription via the internal API.

    ``api_key_id`` is required — the webhook is scoped to a specific API key.
    """

    api_key_id: uuid.UUID
    url: AnyHttpUrl
    events: list[str] = ["*"]


class UpdateInternalWebhookRequest(BaseModel):
    """Partial update for a webhook subscription."""

    url: AnyHttpUrl | None = None
    events: list[str] | None = None
    is_active: bool | None = None


class InternalWebhookResponse(BaseModel):
    """Webhook subscription response for the internal API — includes api_key_name."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    api_key_id: uuid.UUID
    api_key_name: str | None = None
    url: str
    events: list
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class InternalWebhookCreatedResponse(InternalWebhookResponse):
    """Returned once at creation — includes the plaintext secret."""

    secret: str


class InternalWebhookDeliveryResponse(BaseModel):
    """Webhook delivery record for the internal API."""

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


class PaginatedWebhookDeliveriesResponse(BaseModel):
    """Paginated list of webhook deliveries with total count."""

    data: list[InternalWebhookDeliveryResponse]
    total: int
