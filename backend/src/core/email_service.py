# Email dispatch via Resend — renders Jinja2 templates, enqueues via Celery to avoid blocking HTTP responses

from pathlib import Path

import resend
from jinja2 import Environment, FileSystemLoader

from src.utils.config import config
from src.utils.log import get_logger

logger = get_logger(__name__)

resend.api_key = config.resend_key

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_jinja_env: Environment | None = None



def send_email_notification(to_email: str, subject: str, html_content: str) -> dict:
    try:
        params: resend.Emails.SendParams = {
            "from": config.resend_mail,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        email = resend.Emails.send(params)
        logger.info(f"Email sent to {to_email}: {email}")
        return email
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        return {"error": str(e)}



def _get_jinja_env() -> Environment:
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    return _jinja_env

def render_email_template(template_name: str, **kwargs) -> str:
    env = _get_jinja_env()
    template = env.get_template(template_name)
    return template.render(**kwargs)


# Enqueues email via Celery to avoid blocking the HTTP response with SMTP latency
def send_magic_link_email(to_email: str, token: str) -> dict | None:
    magic_link_url = f"{config.api_url}/internal/auth/magic-link/verify?token={token}" 
    html_content = render_email_template(
        "magic_link.html",
        magic_link_url=magic_link_url,
        year=2026,
    )
    subject = "Sign in to Flume"
    try:
        from celery_app.celery import bg_task

        bg_task.send_task(
            "celery_app.task.send_email_task",
            args=[to_email, subject, html_content],
        )
        logger.info(f"Magic link email enqueued for {to_email}")
        return None
    except Exception as e:
        logger.error(f"Failed to enqueue magic link email for {to_email}: {e}", exc_info=True)
        # TODO: route to dead letter queue in production to alert the team on enqueue failures
        # fallback: send_email_notification(to_email, subject, html_content)
