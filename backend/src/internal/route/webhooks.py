import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from fastapi import status as http_status

from src.core.dependency import get_current_user, get_event_service
from src.model.user import User
from src.service.events import EventService
from src.internal.schema.webhooks import (
    CreateInternalWebhookRequest,
    UpdateInternalWebhookRequest,
    InternalWebhookCreatedResponse,
    InternalWebhookDeliveryResponse,
)
from src.utils.response import success

# ── Internal webhook routes (JWT authenticated) ──────────────────────────────
# Dashboard-facing endpoints for managing webhook subscriptions across all of a user's API keys. The user's identity comes from the JWT.

internal_webhook_route = APIRouter(prefix="/webhooks", tags=["internal-webhooks"])


@internal_webhook_route.get("")
async def list_webhooks(
    user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
    api_key_id: uuid.UUID | None = Query(None, description="Filter by API key"),
):
    """List all webhook subscriptions across the user's API keys."""
    subs = await event_service.list_subscriptions_by_user(
        user_id=user.id, api_key_id=api_key_id,
    )
    enriched = [event_service.enrich_subscription(s) for s in subs]
    return success(data=[s.model_dump() for s in enriched])


@internal_webhook_route.post("", status_code=http_status.HTTP_201_CREATED)
async def create_webhook(
    body: CreateInternalWebhookRequest,
    user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
):
    """Create a webhook subscription on a specific API key."""
    sub, secret = await event_service.create_subscription_by_user(
        user_id=user.id,
        api_key_id=body.api_key_id,
        url=str(body.url),
        events=body.events,
    )
    enriched = event_service.enrich_subscription(sub)
    return success(
        data=InternalWebhookCreatedResponse(
            **enriched.model_dump(),
            secret=secret,
        ).model_dump(),
        message="Webhook subscription created",
        status_code=http_status.HTTP_201_CREATED,
    )


@internal_webhook_route.get("/{subscription_id}")
async def get_webhook(
    subscription_id: uuid.UUID,
    user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
):
    """Get a single webhook subscription, verifying user ownership."""
    sub = await event_service.get_subscription_by_user(user.id, subscription_id)
    enriched = event_service.enrich_subscription(sub)
    return success(data=enriched.model_dump())


@internal_webhook_route.patch("/{subscription_id}")
async def update_webhook(
    subscription_id: uuid.UUID,
    body: UpdateInternalWebhookRequest,
    user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
):
    """Update a webhook subscription, verifying user ownership."""
    data = body.model_dump(exclude_unset=True)
    if "url" in data:
        data["url"] = str(data["url"])
    sub = await event_service.update_subscription_by_user(
        user_id=user.id,
        subscription_id=subscription_id,
        **data,
    )
    enriched = event_service.enrich_subscription(sub)
    return success(
        data=enriched.model_dump(),
        message="Webhook subscription updated",
    )


@internal_webhook_route.delete("/{subscription_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    subscription_id: uuid.UUID,
    user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
):
    """Delete a webhook subscription, verifying user ownership."""
    await event_service.delete_subscription_by_user(user.id, subscription_id)
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)


@internal_webhook_route.post("/{subscription_id}/test")
async def test_webhook(
    subscription_id: uuid.UUID,
    user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
):
    """Send a synchronous test ping to the subscriber URL."""
    result = await event_service.test_subscription_by_user(user.id, subscription_id)
    return success(data=result)


@internal_webhook_route.get("/{subscription_id}/deliveries")
async def list_webhook_deliveries(
    subscription_id: uuid.UUID,
    user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
):
    """List recent delivery attempts for a subscription."""
    deliveries = await event_service.list_deliveries_by_user(user.id, subscription_id)
    return success(
        data=[InternalWebhookDeliveryResponse(**d.to_dict()).model_dump() for d in deliveries],
    )
