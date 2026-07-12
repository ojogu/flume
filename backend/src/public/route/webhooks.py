import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from src.core.dependency import get_api_key_from_header, get_event_service
from src.model.api import ApiKey
from src.public.schema.webhooks import (
    CreateWebhookSubscription,
    UpdateWebhookSubscription,
    WebhookSubscriptionCreatedResponse,
    WebhookSubscriptionResponse,
    WebhookDeliveryResponse,
)
from src.service.events import EventService
from src.utils.response import success

# ── Webhook subscription CRUD ──────────────────────────────────────────────────
# Authenticated endpoints for managing webhook subscriptions and viewing delivery history. All scoped by the API key from the ``X-API-Key`` header.

webhook_route = APIRouter(prefix="/webhooks", tags=["webhooks"])


@webhook_route.post("")
async def create_webhook(
    body: CreateWebhookSubscription,
    api_key: ApiKey = Depends(get_api_key_from_header),
    event_service: EventService = Depends(get_event_service),
):
    sub, secret = await event_service.create_subscription(
        api_key_id=api_key.id,
        url=body.url,
        events=body.events,
    )
    return success(
        data=WebhookSubscriptionCreatedResponse(
            **sub.to_dict(),
            secret=secret,
        ).model_dump(),
        message="Webhook subscription created",
        status_code=status.HTTP_201_CREATED,
    )


@webhook_route.get("")
async def list_webhooks(
    api_key: ApiKey = Depends(get_api_key_from_header),
    event_service: EventService = Depends(get_event_service),
):
    subs = await event_service.list_subscriptions(api_key_id=api_key.id)
    return success(
        data=[WebhookSubscriptionResponse(**s.to_dict()) for s in subs],
    )


@webhook_route.get("/{subscription_id}")
async def get_webhook(
    subscription_id: uuid.UUID,
    api_key: ApiKey = Depends(get_api_key_from_header),
    event_service: EventService = Depends(get_event_service),
):
    sub = await event_service.get_subscription(
        subscription_id=subscription_id,
        api_key_id=api_key.id,
    )
    return success(
        data=WebhookSubscriptionResponse(**sub.to_dict()).model_dump(),
    )


@webhook_route.patch("/{subscription_id}")
async def update_webhook(
    subscription_id: uuid.UUID,
    body: UpdateWebhookSubscription,
    api_key: ApiKey = Depends(get_api_key_from_header),
    event_service: EventService = Depends(get_event_service),
):
    sub = await event_service.update_subscription(
        subscription_id=subscription_id,
        api_key_id=api_key.id,
        **body.model_dump(exclude_unset=True),
    )
    return success(
        data=WebhookSubscriptionResponse(**sub.to_dict()).model_dump(),
        message="Webhook subscription updated",
    )


@webhook_route.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    subscription_id: uuid.UUID,
    api_key: ApiKey = Depends(get_api_key_from_header),
    event_service: EventService = Depends(get_event_service),
):
    await event_service.delete_subscription(
        subscription_id=subscription_id,
        api_key_id=api_key.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@webhook_route.post("/{subscription_id}/test")
async def test_webhook(
    subscription_id: uuid.UUID,
    api_key: ApiKey = Depends(get_api_key_from_header),
    event_service: EventService = Depends(get_event_service),
):
    """Send a synchronous test ping to the subscriber URL.

    Returns the HTTP status and response body so the dashboard can show
    green (2xx) or red (non-2xx / error).
    """
    result = await event_service.test_subscription(
        subscription_id=subscription_id,
        api_key_id=api_key.id,
    )
    return success(data=result)


@webhook_route.get("/{subscription_id}/deliveries")
async def list_webhook_deliveries(
    subscription_id: uuid.UUID,
    api_key: ApiKey = Depends(get_api_key_from_header),
    event_service: EventService = Depends(get_event_service),
):
    deliveries = await event_service.list_deliveries(
        subscription_id=subscription_id,
        api_key_id=api_key.id,
    )
    return success(
        data=[WebhookDeliveryResponse(**d.to_dict()) for d in deliveries],
    )
