import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from typing import Any
import uuid

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exception_base import NotFoundError
from src.model.event import WebhookSubscription, WebhookDelivery
from src.utils.log import get_logger

logger = get_logger(__name__)


class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Subscription CRUD ─────────────────────────────────────────────────

    async def create_subscription(
        self,
        api_key_id: uuid.UUID,
        url: str,
        events: list[str] | None = None,
        is_active: bool = True,
    ) -> tuple[WebhookSubscription, str]:
        """Create a webhook subscription with an auto-generated HMAC secret.

        Returns ``(subscription, plaintext_secret)`` — the secret is returned
        only once at creation time.
        """
        secret = secrets.token_hex(32)
        sub = WebhookSubscription(
            api_key_id=api_key_id,
            url=url,
            events=events or ["*"],
            secret=secret,
            is_active=is_active,
        )
        self.db.add(sub)
        await self.db.flush()
        await self.db.refresh(sub)
        await self.db.commit()
        logger.info(f"WebhookSubscription {sub.id} created for API key {api_key_id}")
        return sub, secret

    async def list_subscriptions(
        self, api_key_id: uuid.UUID,
    ) -> list[WebhookSubscription]:
        """List all subscriptions owned by the given API key."""
        result = await self.db.execute(
            select(WebhookSubscription)
            .where(WebhookSubscription.api_key_id == api_key_id)
            .order_by(WebhookSubscription.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_subscription(
        self, subscription_id: uuid.UUID, api_key_id: uuid.UUID,
    ) -> WebhookSubscription:
        """Fetch a single subscription, scoped by API key ownership."""
        result = await self.db.execute(
            select(WebhookSubscription)
            .where(WebhookSubscription.id == subscription_id)
            .where(WebhookSubscription.api_key_id == api_key_id)
        )
        sub = result.scalar_one_or_none()
        if not sub:
            raise NotFoundError(f"WebhookSubscription {subscription_id} not found")
        return sub

    async def update_subscription(
        self,
        subscription_id: uuid.UUID,
        api_key_id: uuid.UUID,
        **kwargs: Any,
    ) -> WebhookSubscription:
        """Partially update a subscription. Accepted keys: ``url``, ``events``, ``is_active``."""
        sub = await self.get_subscription(subscription_id, api_key_id)

        for key in ("url", "events", "is_active"):
            if key in kwargs:
                setattr(sub, key, kwargs[key])

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(sub)
        logger.info(f"WebhookSubscription {subscription_id} updated")
        return sub

    async def delete_subscription(
        self, subscription_id: uuid.UUID, api_key_id: uuid.UUID,
    ) -> None:
        """Delete a subscription, scoped by API key ownership."""
        sub = await self.get_subscription(subscription_id, api_key_id)
        await self.db.delete(sub)
        await self.db.commit()
        logger.info(f"WebhookSubscription {subscription_id} deleted")

    async def list_deliveries(
        self, subscription_id: uuid.UUID, api_key_id: uuid.UUID, limit: int = 50,
    ) -> list[WebhookDelivery]:
        """List recent deliveries for a subscription, validating ownership first."""
        # Verify ownership before querying deliveries
        await self.get_subscription(subscription_id, api_key_id)

        result = await self.db.execute(
            select(WebhookDelivery)
            .where(WebhookDelivery.subscription_id == subscription_id)
            .order_by(WebhookDelivery.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # ── Test endpoint ─────────────────────────────────────────────────────

    async def test_subscription(
        self, subscription_id: uuid.UUID, api_key_id: uuid.UUID,
    ) -> dict:
        """Send a synchronous test ping to the subscriber URL.

        Validates ownership, builds a real HMAC-signed payload, POSTs with
        actual delivery headers, and returns the result immediately.
        No delivery record is created.
        """
        sub = await self.get_subscription(subscription_id, api_key_id)

        payload = {
            "id": f"test_{uuid.uuid4()}",
            "type": "ping",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": {"message": "Webhook test from Flume dashboard"},
        }
        body_bytes = json.dumps(payload, separators=(",", ":")).encode()
        signature = hmac.new(
            sub.secret.encode(), body_bytes, hashlib.sha256,
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Signature-256": f"sha256={signature}",
            "X-Event-ID": payload["id"],
            "User-Agent": "Flume-Webhook/1.0",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(sub.url, content=body_bytes, headers=headers)

            return {
                "success": 200 <= response.status_code < 300,
                "status_code": response.status_code,
                "response_body": response.text[:4096],
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "status_code": None,
                "response_body": "Connection timeout after 10s",
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "response_body": str(e)[:4096],
            }

    # ── Event emission ────────────────────────────────────────────────────

    async def emit(
        self,
        event_type: str,
        resource_id: uuid.UUID,
        data: dict,
    ) -> list[WebhookDelivery]:
        """Find active subscriptions matching the event type, create pending deliveries,
        and dispatch the Celery webhook task for each.

        Returns the list of created ``WebhookDelivery`` records.
        """
        subscriptions = await self._find_matching_subscriptions(event_type)
        if not subscriptions:
            return []

        deliveries: list[WebhookDelivery] = []
        for sub in subscriptions:
            delivery = WebhookDelivery(
                subscription_id=sub.id,
                event_type=event_type,
                payload={
                    "id": str(resource_id),
                    "type": event_type,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "data": data,
                },
                status="pending",
            )
            self.db.add(delivery)
            deliveries.append(delivery)

        await self.db.flush()
        for d in deliveries:
            await self.db.refresh(d)
        await self.db.commit()

        logger.info(
            "Emitted %s — %d delivery(s) created",
            event_type,
            len(deliveries),
        )

        for delivery in deliveries:
            self._dispatch_delivery(delivery.id)

        return deliveries

    async def _find_matching_subscriptions(
        self, event_type: str,
    ) -> list[WebhookSubscription]:
        """Return active subscriptions that match the event type (exact match or wildcard)."""
        result = await self.db.execute(
            select(WebhookSubscription)
            .where(WebhookSubscription.is_active.is_(True))
        )
        subs = list(result.scalars().all())

        matching = []
        for sub in subs:
            events = sub.events or []
            if "*" in events or event_type in events:
                matching.append(sub)

        return matching

    def _dispatch_delivery(self, delivery_id: uuid.UUID) -> None:
        """Enqueue the Celery task for this delivery."""
        from celery_app.webhook import deliver_webhook
        deliver_webhook.apply_async(args=[str(delivery_id)])
