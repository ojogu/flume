# ── Celery task definitions ────────────────────────────────────────────────────
# Email dispatch task with retry. Async-to-sync bridge for calling async
# service methods from Celery's synchronous execution context.

from celery_app.celery import bg_task
from src.core.email_service import send_email_notification
from src.utils.log import get_logger

logger = get_logger(__name__)




# max_retries=3 with 60s backoff between attempts; raises to Celery for DLQ routing
@bg_task.task(name="jobs.email.send", max_retries=3, default_retry_delay=60)
def send_email_task(to_email, subject, html_content):
    """Send an email via the notification service."""
    try:
        result = send_email_notification(to_email, subject, html_content)
        logger.info(f"Email sent to {to_email}: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise send_email_task.retry(exc=e)

        