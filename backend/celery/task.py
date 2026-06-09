import asyncio
import concurrent
import logging

from celery.celery import bg_task
from src.core.email_service import send_email_notification

logger = logging.getLogger(__name__)


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


@bg_task.task(name="celery.task.send_email_task", max_retries=3, default_retry_delay=60)
def send_email_task(to_email, subject, html_content):
    """Send an email via the notification service."""
    try:
        result = send_email_notification(to_email, subject, html_content)
        logger.info(f"Email sent to {to_email}: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise send_email_task.retry(exc=e)

        