# ── Celery task definitions ────────────────────────────────────────────────────
# Email dispatch task with retry. Async-to-sync bridge for calling async
# service methods from Celery's synchronous execution context.

import asyncio
import concurrent
import logging

from celery_app.celery import bg_task
from src.core.email_service import send_email_notification

logger = logging.getLogger(__name__)


# Celery tasks run synchronously, but our service layer uses async SQLAlchemy.
# This helper runs an async coroutine in a dedicated thread with its own event loop,
# preventing event-loop conflicts with FastAPI's async context.
def run_async_in_sync(coro):
    """
    Helper function to run async code in sync Celery tasks
    Creates a fresh event loop in a separate thread to avoid conflicts.
    """

    def _run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_in_thread)
        return future.result()


# max_retries=3 with 60s backoff between attempts; raises to Celery for DLQ routing
@bg_task.task(name="celery_app.task.send_email_task", max_retries=3, default_retry_delay=60)
def send_email_task(to_email, subject, html_content):
    """Send an email via the notification service."""
    try:
        result = send_email_notification(to_email, subject, html_content)
        logger.info(f"Email sent to {to_email}: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise send_email_task.retry(exc=e)

        