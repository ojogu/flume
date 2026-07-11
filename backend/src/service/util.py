import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.model.api import ApiKey
from src.utils.log import get_logger

logger = get_logger(__name__)


# ── Utility service ───────────────────────────────────────────────────────────
# Powers the discovery and verification endpoints under /v1/utils.
# Platform listing is delegated to PlatformService (DB-backed).
# Events are a static catalog — no DB access.

EVENT_CATALOG = [
    {
        "type": "job.created",
        "description": "Job was created and queued for processing",
        "payload_fields": [
            {"name": "job_id", "type": "UUID", "description": "Unique job identifier"},
            {"name": "status", "type": "string", "description": "Job status (always 'pending')"},
            {"name": "source_uri", "type": "string", "description": "Original source URL or upload URI"},
            {"name": "source_type", "type": "string", "description": "Source media type ('video' or 'audio')"},
        ],
    },
    {
        "type": "job.processing",
        "description": "Worker picked up the job for execution",
        "payload_fields": [
            {"name": "job_id", "type": "UUID", "description": "Unique job identifier"},
            {"name": "status", "type": "string", "description": "Job status (always 'processing')"},
            {"name": "source_uri", "type": "string", "description": "Original source URL or upload URI"},
            {"name": "source_type", "type": "string", "description": "Source media type ('video' or 'audio')"},
        ],
    },
    {
        "type": "job.completed",
        "description": "Job finished successfully — all pipeline steps passed",
        "payload_fields": [
            {"name": "job_id", "type": "UUID", "description": "Unique job identifier"},
            {"name": "status", "type": "string", "description": "Final job status ('succeeded' or 'partial_success')"},
            {"name": "source_uri", "type": "string", "description": "Original source URL or upload URI"},
            {"name": "source_type", "type": "string", "description": "Source media type ('video' or 'audio')"},
            {"name": "source_metadata", "type": "dict", "description": "Extracted source and media metadata"},
            {"name": "error", "type": "string|null", "description": "Error message (null on success)"},
        ],
    },
    {
        "type": "job.failed",
        "description": "Job could not complete",
        "payload_fields": [
            {"name": "job_id", "type": "UUID", "description": "Unique job identifier"},
            {"name": "status", "type": "string", "description": "Job status (always 'failed')"},
            {"name": "error", "type": "string", "description": "Error description"},
        ],
    },
    {
        "type": "step.started",
        "description": "Pipeline step began execution",
        "payload_fields": [
            {"name": "step_id", "type": "UUID", "description": "Unique step identifier"},
            {"name": "job_id", "type": "UUID", "description": "Parent job identifier"},
            {"name": "operation", "type": "string", "description": "Operation name (e.g. 'download', 'trim', 'compress')"},
            {"name": "step_index", "type": "int", "description": "Zero-based position in the pipeline"},
        ],
    },
    {
        "type": "step.completed",
        "description": "Pipeline step finished successfully",
        "payload_fields": [
            {"name": "step_id", "type": "UUID", "description": "Unique step identifier"},
            {"name": "job_id", "type": "UUID", "description": "Parent job identifier"},
            {"name": "operation", "type": "string", "description": "Operation name"},
            {"name": "step_index", "type": "int", "description": "Zero-based position in the pipeline"},
            {"name": "output_artifact", "type": "dict", "description": "Output artifact metadata"},
        ],
    },
    {
        "type": "step.failed",
        "description": "Pipeline step failed",
        "payload_fields": [
            {"name": "step_id", "type": "UUID", "description": "Unique step identifier"},
            {"name": "job_id", "type": "UUID", "description": "Parent job identifier"},
            {"name": "operation", "type": "string", "description": "Operation name"},
            {"name": "step_index", "type": "int", "description": "Zero-based position in the pipeline"},
            {"name": "error", "type": "string", "description": "Error description"},
        ],
    },
]


class UtilService:
    """Service for utility/discovery endpoints.

    Combines the static event catalog with read-only API key verification.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def get_events() -> list[dict]:
        """Return the curated webhook event catalog.

        Each entry includes the event type string, a human-readable
        description, and the payload fields emitted with that event.
        """
        return EVENT_CATALOG

    async def verify_api_key(self, api_key: ApiKey) -> dict:
        """Return metadata about an already-resolved API key.

        Takes the ApiKey ORM object from get_api_key_from_header.
        Read-only — does NOT update last_used_at (that happens on
        actual API calls, not on verification).
        """
        return {
            "valid": True,
            "key_prefix": api_key.key_prefix,
            "name": api_key.name,
            "expires_at": api_key.expires_at,
            "last_used_at": api_key.last_used_at,
            "status": api_key.status,
        }
