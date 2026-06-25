# ── R2 storage layer (boto3 S3-compatible client for Cloudflare R2) 
# This module handles:
# • Presigned upload URL generation (Phase 1 — client uploads directly)
# • head_object verification(Phase 2 — confirm upload landed)
# • Presigned download URLs (for internal pipeline workers)
#  • Object deletion       (for the cleanup sweep)
#
# boto3 is synchronous, so all public methods run the R2 call inside asyncio.to_thread() to avoid blocking the event loop.

import asyncio
import uuid
from datetime import datetime, timezone, timedelta

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from src.utils.config import config
from src.utils.log import get_logger

logger = get_logger(__name__)

UPLOAD_URL_EXPIRY_SECONDS = 3600


def build_object_key(api_key_id: uuid.UUID, upload_id: uuid.UUID, filename: str) -> str:
    """Build an R2 object key from known identifiers.

    Pattern: uploads/{api_key_8}/{upload_8}/{filename}
    Only the first 8 hex chars of each UUID are used — full UUIDs live in the DB. This keeps R2 console browsing readable while maintaining per-API-key isolation.
    """
    api_key_short = str(api_key_id).split("-")[0]
    upload_short = str(upload_id).split("-")[0]
    return f"uploads/{api_key_short}/{upload_short}/{filename}"


class R2Storage:
    """Thin wrapper around a boto3 S3 client configured for Cloudflare R2.

    Uses the S3-compatible endpoint at config.s3_url with the R2 API credentials from config.access_key_id / config.secret_access_key. The client is created once and reused (lazy singleton per process).
    """

    _client = None

    # ── Internal helpers ──────────────────────────────────────────────────

    def _get_client(self):
        """Lazy-init the boto3 S3 client for R2.

        Created once per worker process — boto3 handles its own connection
        pooling under the hood. The endpoint_url points to the R2 S3-compatible API, not the standard AWS S3 endpoint.
        """
        if self._client is not None:
            return self._client

        logger.info(f"Initialising boto3 S3 client for R2 endpoint: {config.s3_url}")

        self._client = boto3.client(
            "s3",
            endpoint_url=config.s3_url,
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
            config=BotoConfig(
                connect_timeout=10,
                read_timeout=30,
                retries={"max_attempts": 3, "mode": "adaptive"},
            ),
        )
        return self._client

    async def _run(self, method, *args, **kwargs):
        """Run a synchronous boto3 call in a thread pool.

        All boto3 methods are synchronous (they make HTTP requests via urllib3).
        Running them in asyncio.to_thread() prevents blocking the FastAPI event loop when multiple upload requests arrive concurrently.
        """
        client = self._get_client()
        fn = getattr(client, method)
        return await asyncio.to_thread(fn, *args, **kwargs)

    # ── Public API ────────────────────────────────────────────────────────

    async def generate_presigned_upload_url(
        self,
        object_key: str,
        content_type: str,
        expires_in: int = UPLOAD_URL_EXPIRY_SECONDS,
    ) -> str:
        """Issue a time-limited presigned PUT URL for direct client upload.

        The URL includes a Content-Type constraint so clients can only upload
        the declared MIME type — prevents MIME confusion attacks.
        """
        logger.info(f"Generating presigned upload URL for key={object_key} (expires={expires_in}s)")
        url = await self._run(
            "generate_presigned_url",
            ClientMethod="put_object",
            Params={
                "Bucket": config.r2_bucket_name,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )
        # Build expiry timestamp so clients can show a countdown or pre-emptively request a new URL before the old one expires.
        return url

    async def head_object(self, object_key: str) -> dict | None:
        """Check whether an object exists in R2 and return its metadata.

        Returns a dict with content_length, content_type, etag, last_modified
        if the object exists, or None if it doesn't (404). Used in Phase 2 (complete endpoint) to confirm the upload actually landed.
        """
        try:
            response = await self._run(
                "head_object",
                Bucket=config.r2_bucket_name,
                Key=object_key,
            )
            return {
                "content_length": response.get("ContentLength"),
                "content_type": response.get("ContentType"),
                "etag": response.get("ETag"),
                "last_modified": response.get("LastModified"),
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.warning(f"Object not found in R2: key={object_key}")
                return None
            logger.error(f"R2 head_object failed for key={object_key}: {e}")
            raise

    async def generate_presigned_download_url(
        self,
        object_key: str,
        expires_in: int = 3600,
    ) -> str:
        """Issue a presigned GET URL for the processing pipeline.

        Pipeline workers use this URL to download the source file for FFmpeg processing. The URL is time-limited so access is scoped
        to the processing window.
        """
        url = await self._run(
            "generate_presigned_url",
            ClientMethod="get_object",
            Params={
                "Bucket": config.r2_bucket_name,
                "Key": object_key,
            },
            ExpiresIn=expires_in,
        )
        return url

    async def delete_object(self, object_key: str) -> None:
        """Remove an object from R2 — used by the cleanup sweep for orphaned uploads.

        Silently succeeds if the object doesn't exist (R2 delete is idempotent).
        """
        logger.info(f"Deleting R2 object: key={object_key}")
        try:
            await self._run(
                "delete_object",
                Bucket=config.r2_bucket_name,
                Key=object_key,
            )
        except ClientError as e:
            logger.error(f"Failed to delete R2 object key={object_key}: {e}")
            raise


# Singleton — one R2Storage instance per worker process.
storage = R2Storage()
