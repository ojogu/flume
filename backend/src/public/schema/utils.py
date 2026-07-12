from datetime import datetime
from typing import Optional
import uuid

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
    key_prefix: Optional[str] = None
    name: Optional[str] = None
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    status: Optional[str] = None
