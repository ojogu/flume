import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.model.upload import Upload, UploadStatus
from src.public.schema.uploads import PresignedUploadResult
from src.core.exception_base import NotFoundError, BadRequest, DatabaseError
from src.utils.log import get_logger
from src.service.storage import storage, build_object_key

logger = get_logger(__name__)


# ── Service ──────────────────────────────────────────────────────────

class UploadService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Phase 1: Generate presigned URL (no file bytes touch the server) ─

    async def create_presigned_upload(
        self,
        api_key_id: uuid.UUID,
        original_filename: str,
        content_type: str,
        file_size: int | None = None,
    ) -> PresignedUploadResult:
        """Issue a presigned upload URL so the client can PUT the file directly to R2.
        The file never passes through our server — zero bandwidth, zero disk I/O
        """
        upload_id = uuid.uuid4()
        object_key = build_object_key(api_key_id, upload_id, original_filename)

        # Create an Upload record in PENDING status — reserves the object key.
        # Persist the Upload record *before* generating the URL so that if the DB write fails we don't issue a useless presigned URL.

        upload = Upload(
            id=upload_id,
            api_key_id=api_key_id,
            uri=object_key,                          # stores the R2 object key
            status=UploadStatus.PENDING.value,
            original_filename=original_filename,
            file_size=file_size,
        )
        self.db.add(upload)
        try:
            await self.db.flush()
            await self.db.refresh(upload)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create PENDING upload record: {e}")
            raise DatabaseError()

        # Generate a time-limited presigned URL from R2 now that we have a valid object key. 
        presigned_url = await storage.generate_presigned_upload_url(
            object_key=object_key,
            content_type=content_type,
        )

        await self.db.commit()
        logger.info(f"Presigned upload URL issued: upload_id={upload_id}, key={object_key}")

        # The URL will expire in ~1 hour from now (matches the default UPLOAD_URL_EXPIRY_SECONDS in R2Storage).  Expose the exact time so the client can pre-emptively refresh it.
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        return PresignedUploadResult(
            upload_id=upload.id,
            object_key=upload.uri,
            presigned_url=presigned_url,
            expires_at=expires_at,
        )

    # ── Phase 2: Confirm the upload landed in R2 ──────────────────────

    async def complete_upload(
        self,
        upload_id: uuid.UUID,
        api_key_id: uuid.UUID,
    ) -> Upload:
        """Verify that the file actually exists in R2 and mark the upload as ready.
        Called by the client after it has successfully PUT the file to the presigned URL.  Without this step the server would have to trust the client's word — instead we check R2 directly via head_object.

        Steps:
          1. Load the Upload record and confirm it's still PENDING.
          2. Call R2 head_object — returns None if the upload never happened.
          3. Record the real metadata (content_length, etag) from R2.
          4. Flip status to UNATTACHED so it can be attached to a job.
        """
        # ── Load + guard ──────────────────────────────────────────────
        upload = await self.get_upload(upload_id, api_key_id)

        if upload.status != UploadStatus.PENDING.value:
            logger.warning(f"Upload {upload_id} has status '{upload.status}', expected 'pending'")
            raise BadRequest("Upload is not in a processable state")

        # ── Verify in R2 ──────────────────────────────────────────────
        metadata = await storage.head_object(upload.uri)
        if metadata is None:
            logger.warning(f"Upload {upload_id}: object not found at key {upload.uri}")
            raise BadRequest("Upload not found or no longer available")

        # ── Update DB record ──────────────────────────────────────────
        upload.status = UploadStatus.UNATTACHED.value
        upload.file_size = metadata["content_length"]
        # Store the etag and content-type on the Upload model. These fields
        # are available via UploadResponse for debugging / verification.
        upload.content_type = metadata["content_type"]
        upload.etag = metadata["etag"]

        try:
            await self.db.flush()
            await self.db.refresh(upload)
            await self.db.commit()
            logger.info(f"Upload {upload_id} confirmed in R2: size={metadata['content_length']}, etag={metadata['etag']}")
            return upload
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error completing upload {upload_id}: {e}")
            raise DatabaseError()

    # ── Lookup + lifecycle helpers ────────────────────────────────────

    async def find_by_uri(
        self, uri: str, api_key_id: uuid.UUID
    ) -> Upload | None:
        """Look up an upload by its R2 object key — used in POST /job.

        When the client creates a job with source.uri = object_key, this method finds the matching Upload record and attach_upload() flips
        it to ATTACHED so the cleanup sweep doesn't delete it mid-processing.
        """
        result = await self.db.execute(
            select(Upload).where(
                Upload.uri == uri,
                Upload.api_key_id == api_key_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_upload(
        self, upload_id: uuid.UUID, api_key_id: uuid.UUID
    ) -> Upload:
        result = await self.db.execute(
            select(Upload).where(
                Upload.id == upload_id,
                Upload.api_key_id == api_key_id,
            )
        )
        upload = result.scalar_one_or_none()
        if not upload:
            raise NotFoundError("Upload not found")
        return upload

    async def attach_upload(
        self, upload_id: uuid.UUID, api_key_id: uuid.UUID
    ) -> Upload:
        """Mark an upload as attached — protects it from the 24h cleanup sweep."""
        upload = await self.get_upload(upload_id, api_key_id)

        if upload.status == UploadStatus.ATTACHED.value:
            raise BadRequest("Upload is already attached to a job")

        # Allow attaching from both UNATTACHED and (potentially) other states.
        # If the upload is still PENDING, the file hasn't been confirmed yet but we still allow the transition so the client can attach immediately after the PUT without a separate /complete call if they prefer.
        upload.status = UploadStatus.ATTACHED.value
        try:
            await self.db.flush()
            await self.db.refresh(upload)
            await self.db.commit()
            logger.info(f"Upload {upload_id} attached")
            return upload
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error attaching upload {upload_id}: {e}")
            raise DatabaseError()

    async def cleanup_unattached(self, older_than: datetime) -> int:
        """Delete pending + unattached uploads older than the threshold.

        Also removes the orphaned R2 objects so we don't leak storage.
        R2 deletion is best-effort (log failure, continue) so a single
        transient error doesn't stall the entire sweep.
        """
        result = await self.db.execute(
            select(Upload).where(
                Upload.status.in_([
                    UploadStatus.PENDING.value,
                    UploadStatus.UNATTACHED.value,
                ]),
                Upload.created_at < older_than,
            )
        )
        uploads = list(result.scalars().all())

        # Delete R2 objects first (best-effort), then DB records.
        deleted_count = 0
        for upload in uploads:
            try:
                await storage.delete_object(upload.uri)
            except Exception as e:
                logger.warning(f"Failed to delete R2 object for upload {upload.id} (key={upload.uri}): {e}")
                continue
            await self.db.delete(upload)
            deleted_count += 1

        try:
            await self.db.commit()
            logger.info(f"Cleaned up {deleted_count}/{len(uploads)} orphaned uploads")
            return deleted_count
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error cleaning up uploads: {e}")
            raise DatabaseError()
