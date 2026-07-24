import json
import secrets
from datetime import datetime, timezone
from typing import Any
import uuid

from httpx import TimeoutException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exception_base import NotFoundError
from src.model.event import DeliveryStatus, EventType, WebhookSubscription, WebhookDelivery
from src.model.api import ApiKey
from src.internal.schema.webhooks import InternalWebhookResponse
from src.schema.event import EventEnvelope, PingEnvelope
from src.utils.crypto import build_signed_headers
from src.utils.http_client import get_http_client
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

        Returns ``(subscription, plaintext_secret)`` — the secret is returned only once at creation time.
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
        await self.db.refresh(sub, ["api_key"])
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
            logger.warning(f"Webhook subscription {subscription_id} not found")
            raise NotFoundError("Webhook subscription not found")
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
        await self.db.refresh(sub, ["api_key"])
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

        Validates ownership, builds a real HMAC-signed payload, POSTs with actual delivery headers, and returns the result immediately.
        No delivery record is created.
        """
        sub = await self.get_subscription(subscription_id, api_key_id)

        envelope = PingEnvelope(
            id=f"test_{uuid.uuid4()}",
            created_at=datetime.now(timezone.utc),
            data={"message": "Webhook test from Flume dashboard"},
        )
        body_bytes = json.dumps(envelope.model_dump(mode="json"), separators=(",", ":")).encode()
        headers = build_signed_headers(body_bytes, sub.secret, envelope.id)

        try:
            async with get_http_client(timeout=10.0) as client:
                response = await client.post(sub.url, content=body_bytes, headers=headers)

            success = 200 <= response.status_code < 300
            if success:
                logger.info("Test ping to %s succeeded (status=%d)", sub.url, response.status_code)
            else:
                logger.warning("Test ping to %s failed (status=%d)", sub.url, response.status_code)

            return {
                "success": success,
                "status_code": response.status_code,
                "response_body": response.text[:4096],
            }
        except TimeoutException:
            logger.warning("Test ping to %s timed out", sub.url)
            return {
                "success": False,
                "status_code": None,
                "response_body": "Connection timeout after 10s",
            }
        except Exception as e:
            logger.warning(f"Test ping to {sub.url} failed: {e}")
            return {
                "success": False,
                "status_code": None,
                "response_body": "Request to subscriber URL failed",
            }

    # ── User-scoped queries (for internal/dashboard API) ────────────────────────

    async def _verify_subscription_ownership(
        self, user_id: uuid.UUID, subscription_id: uuid.UUID
    ) -> WebhookSubscription:
        """Verify a subscription belongs to the user; raise NotFoundError if not."""
        result = await self.db.execute(
            select(WebhookSubscription)
            .options(selectinload(WebhookSubscription.api_key))
            .join(ApiKey, WebhookSubscription.api_key_id == ApiKey.id)
            .where(WebhookSubscription.id == subscription_id)
            .where(ApiKey.user_id == user_id)
        )
        sub = result.scalar_one_or_none()
        if not sub:
            logger.warning(f"Webhook subscription {subscription_id} not found")
            raise NotFoundError("Webhook subscription not found")
        return sub

    async def list_subscriptions_by_user(
        self, user_id: uuid.UUID, api_key_id: uuid.UUID | None = None,
    ) -> list[WebhookSubscription]:
        """List all subscriptions for a user, optionally filtered by API key."""
        base = (
            select(WebhookSubscription)
            .options(selectinload(WebhookSubscription.api_key))
            .join(ApiKey, WebhookSubscription.api_key_id == ApiKey.id)
            .where(ApiKey.user_id == user_id)
        )
        if api_key_id:
            base = base.where(WebhookSubscription.api_key_id == api_key_id)

        result = await self.db.execute(
            base.order_by(WebhookSubscription.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_subscription_by_user(
        self, user_id: uuid.UUID, subscription_id: uuid.UUID,
    ) -> WebhookSubscription:
        """Fetch a single subscription, verifying user ownership."""
        return await self._verify_subscription_ownership(user_id, subscription_id)

    async def create_subscription_by_user(
        self,
        user_id: uuid.UUID,
        api_key_id: uuid.UUID,
        url: str,
        events: list[str] | None = None,
        is_active: bool = True,
    ) -> tuple[WebhookSubscription, str]:
        """Create a webhook subscription, verifying the API key belongs to the user."""
        # Verify the API key belongs to this user
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.id == api_key_id, ApiKey.user_id == user_id)
        )
        api_key = result.scalar_one_or_none()
        if not api_key:
            logger.warning(f"API key {api_key_id} not found for user")
            raise NotFoundError("API key not found")

        return await self.create_subscription(
            api_key_id=api_key_id, url=url, events=events, is_active=is_active,
        )

    async def update_subscription_by_user(
        self, user_id: uuid.UUID, subscription_id: uuid.UUID, **kwargs: Any,
    ) -> WebhookSubscription:
        """Update a subscription, verifying user ownership."""
        sub = await self._verify_subscription_ownership(user_id, subscription_id)

        for key in ("url", "events", "is_active"):
            if key in kwargs:
                setattr(sub, key, kwargs[key])

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(sub)
        logger.info(f"WebhookSubscription {subscription_id} updated (user {user_id})")
        return sub

    async def delete_subscription_by_user(
        self, user_id: uuid.UUID, subscription_id: uuid.UUID,
    ) -> None:
        """Delete a subscription, verifying user ownership."""
        sub = await self._verify_subscription_ownership(user_id, subscription_id)
        await self.db.delete(sub)
        await self.db.commit()
        logger.info(f"WebhookSubscription {subscription_id} deleted (user {user_id})")

    async def list_deliveries_by_user(
        self, user_id: uuid.UUID, subscription_id: uuid.UUID, limit: int = 50,
    ) -> list[WebhookDelivery]:
        """List recent deliveries for a subscription, verifying user ownership."""
        await self._verify_subscription_ownership(user_id, subscription_id)

        result = await self.db.execute(
            select(WebhookDelivery)
            .where(WebhookDelivery.subscription_id == subscription_id)
            .order_by(WebhookDelivery.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def test_subscription_by_user(
        self, user_id: uuid.UUID, subscription_id: uuid.UUID,
    ) -> dict:
        """Send a test ping to a subscription, verifying user ownership."""
        sub = await self._verify_subscription_ownership(user_id, subscription_id)

        envelope = PingEnvelope(
            id=f"test_{uuid.uuid4()}",
            created_at=datetime.now(timezone.utc),
            data={"message": "Webhook test from Flume dashboard"},
        )
        body_bytes = json.dumps(envelope.model_dump(mode="json"), separators=(",", ":")).encode()
        headers = build_signed_headers(body_bytes, sub.secret, envelope.id)

        try:
            async with get_http_client(timeout=10.0) as client:
                response = await client.post(sub.url, content=body_bytes, headers=headers)

            success = 200 <= response.status_code < 300
            if success:
                logger.info("Test ping to %s succeeded (status=%d)", sub.url, response.status_code)
            else:
                logger.warning("Test ping to %s failed (status=%d)", sub.url, response.status_code)

            return {
                "success": success,
                "status_code": response.status_code,
                "response_body": response.text[:4096],
            }
        except TimeoutException:
            logger.warning("Test ping to %s timed out", sub.url)
            return {
                "success": False,
                "status_code": None,
                "response_body": "Connection timeout after 10s",
            }
        except Exception as e:
            logger.warning(f"Test ping to {sub.url} failed: {e}")
            return {
                "success": False,
                "status_code": None,
                "response_body": "Request to subscriber URL failed",
            }

    # ── Response enrichment ──────────────────────────────────────────────

    def enrich_subscription(self, sub: WebhookSubscription) -> InternalWebhookResponse:
        """Build an InternalWebhookResponse with the API key name from the eager-loaded relationship."""
        return InternalWebhookResponse(
            **sub.to_dict(),
            api_key_name=sub.api_key.name if sub.api_key else None,
        )

    # ── Event emission ────────────────────────────────────────────────────

    async def emit(
        self,
        event_type: EventType,
        resource_id: uuid.UUID,
        data: dict,
        api_key_id: uuid.UUID,
    ) -> list[WebhookDelivery]:
        """Find active subscriptions matching the event type, create pending deliveries, and dispatch the Celery webhook task for each.

        Returns the list of created ``WebhookDelivery`` records.
        """
        subscriptions = await self._find_matching_subscriptions(event_type, api_key_id)
        if not subscriptions:
            return []

        deliveries: list[WebhookDelivery] = []
        for sub in subscriptions:
            envelope = EventEnvelope(
                id=str(resource_id),
                type=event_type,
                created_at=datetime.now(timezone.utc),
                data=data,
            )
            delivery = WebhookDelivery(
                subscription_id=sub.id,
                event_type=event_type,
                payload=envelope.model_dump(mode="json"),
                status=DeliveryStatus.PENDING.value,
            )
            self.db.add(delivery) #stage rows, no commit
            deliveries.append(delivery)

        await self.db.flush() #write rows to db (not committed) but python object still has stale data
        
        for d in deliveries:
            await self.db.refresh(d) # for each row, read updated data from db so python object have fresh data to work with
        await self.db.commit()#commit

        logger.info(
            "Emitted %s — %d delivery(s) created",
            event_type,
            len(deliveries),
        )

        for delivery in deliveries:
            self._dispatch_delivery(delivery.id)

        return deliveries

    async def _find_matching_subscriptions(
        self, event_type: EventType, api_key_id: uuid.UUID,
    ) -> list[WebhookSubscription]:
        """Return active subscriptions that match the event type (exact match or wildcard)."""
        result = await self.db.execute(
            select(WebhookSubscription)
            .where(WebhookSubscription.is_active.is_(True))
            .where(WebhookSubscription.api_key_id == api_key_id)
            .where(
                WebhookSubscription.events.contains("*")
                | WebhookSubscription.events.contains(event_type.value)
            )
        )
        return list(result.scalars().all())

    def _dispatch_delivery(self, delivery_id: uuid.UUID) -> None:
        """Enqueue the Celery task for this delivery."""
        from celery_app.webhook import deliver_webhook
        deliver_webhook.apply_async(args=[str(delivery_id)])
