from datetime import datetime

from pydantic import BaseModel

# ── Utility endpoint schemas ──────────────────────────────────────────────────
# Response bodies for /v1/utils routes — events catalog, key verification.

class PayloadField(BaseModel):
    """Describes a single field in an event's payload."""
    name: str
    type: str
    description: str


class EventInfo(BaseModel):
    """A single webhook event type with description and payload schema."""
    type: str
    description: str
    payload_fields: list[PayloadField]


class EventListResponse(BaseModel):
    events: list[EventInfo]


class VerifyKeyResponse(BaseModel):
    """API key verification result — read-only metadata about the key."""
    valid: bool
    key_prefix: str | None = None
    name: str | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    status: str | None = None
