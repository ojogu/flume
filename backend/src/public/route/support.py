from fastapi import APIRouter, status

from src.core.email_service import send_contact_email
from src.public.schema.support import ContactRequest
from src.utils.response import success

# ── Public contact route ───────────────────────────────────────────────────────
# No-auth contact endpoint. Submissions are enqueued via Celery to the
# configured support inbox using the existing email infrastructure.

support_route = APIRouter(prefix="/support", tags=["support"])


@support_route.post("/contact")
async def submit_contact(body: ContactRequest):
    send_contact_email(
        name=body.name,
        email=body.email,
        subject=body.subject,
        message=body.message,
    )
    return success(
        data={"sent": True},
        message="Message received — we'll get back to you soon.",
        status_code=status.HTTP_200_OK,
    )
