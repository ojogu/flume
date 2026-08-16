from pydantic import BaseModel, EmailStr, Field


# ── Contact / support schemas ─────────────────────────────────────────────────
# Request body for the public contact endpoint. No auth required — submissions
# are emailed to the support inbox via the existing Celery email task.

class ContactRequest(BaseModel):
    """A support message submitted through the contact form."""
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
