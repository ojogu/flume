# ── Webhook delivery task (webhook queue) ─────────────────────────────────
# Responsibilities:
#   1. Read pending WebhookDelivery + subscription
#   2. Sign body with HMAC-SHA256 using the subscription's secret
#   3. POST to subscriber URL with signature and idempotency headers
#   4. Mark delivered on 2xx, retry with exponential backoff on failure
#
# Runs on the **webhook** queue (dedicated workers).
# ──────────────────────────────────────────────────────────────────────────

import hashlib
import hmac
import json
from datetime import datetime, timezone, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.model.event import DeliveryStatus, WebhookDelivery

from celery_app.celery import bg_task
from celery_app.utils import run_async_in_sync
from src.utils.log import get_logger

logger = get_logger(__name__)

# Exponential backoff schedule: attempts → delay in seconds
BACKOFF_SCHEDULE = [10, 60, 600, 3600]  # 10s, 1m, 10m, 1h
MAX_ATTEMPTS = 5


@bg_task.task(
    name="jobs.webhook.deliver",
    queue="webhook",
    max_retries=0,
    acks_late=True,
)
def deliver_webhook(delivery_id: str):
    """Deliver a pending webhook event to the subscriber.

    Performs the HTTP POST, handles response, and manages retry lifecycle
    through the database (not Celery's built-in retry mechanism).
    """
    run_async_in_sync(_deliver_webhook_async(delivery_id))


async def _deliver_webhook_async(delivery_id: str):
    from src.model.event import WebhookSubscription
    from src.utils.db import get_async_db_session

    async with get_async_db_session() as db:
        result = await db.execute(
            select(WebhookDelivery)
            .options(selectinload(WebhookDelivery.subscription))
            .where(WebhookDelivery.id == delivery_id)
        )
        delivery = result.scalar_one_or_none()
        if not delivery:
            logger.error(f"WebhookDelivery {delivery_id} not found")
            return

        if delivery.status != DeliveryStatus.PENDING.value:
            logger.warning(
                f"WebhookDelivery {delivery_id} already {delivery.status} — skipping"
            )
            return

        subscription = delivery.subscription
        if not subscription or not subscription.is_active:
            logger.warning(
                f"Subscription {delivery.subscription_id} is inactive — skipping delivery {delivery_id}"
            )
            return

        body_bytes = json.dumps(delivery.payload, separators=(",", ":")).encode()
        signature = hmac.new(
            subscription.secret.encode(), body_bytes, hashlib.sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Signature-256": f"sha256={signature}",
            "X-Event-ID": str(delivery.id),
            "User-Agent": "Flume-Webhook/1.0",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    subscription.url,
                    content=body_bytes,
                    headers=headers,
                )

            delivery.response_code = response.status_code
            delivery.response_body = response.text[:4096]

            if 200 <= response.status_code < 300:
                delivery.status = DeliveryStatus.DELIVERED.value
                delivery.completed_at = datetime.now(timezone.utc)
                logger.info(
                    "Webhook %s delivered to %s (status=%d)",
                    delivery_id, subscription.url, response.status_code,
                )
            else:
                await _handle_failure(delivery, subscription.url)

        except Exception as e:
            delivery.response_body = str(e)[:4096]
            await _handle_failure(delivery, subscription.url)

        await db.flush()
        await db.commit()


async def _handle_failure(delivery: WebhookDelivery, url: str) -> None:
    """Increment attempt counter, schedule retry, or mark exhausted."""
    delivery.attempts += 1

    if delivery.attempts >= MAX_ATTEMPTS:
        delivery.status = DeliveryStatus.EXHAUSTED.value
        delivery.completed_at = datetime.now(timezone.utc)
        logger.error(
            "Webhook %s exhausted after %d attempts — %s",
            delivery.id, delivery.attempts, url,
        )
        return

    delay = BACKOFF_SCHEDULE[delivery.attempts - 1] if delivery.attempts <= len(BACKOFF_SCHEDULE) else BACKOFF_SCHEDULE[-1]
    delivery.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)

    logger.warning(
        "Webhook %s failed (attempt %d/%d) — retrying in %ds — %s",
        delivery.id, delivery.attempts, MAX_ATTEMPTS, delay, url,
    )

    # Re-enqueue via Celery for the next attempt
    deliver_webhook.apply_async(
        args=[str(delivery.id)],
        countdown=delay,
    )
