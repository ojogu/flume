import uuid
from datetime import datetime, timezone

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.model.upload import Upload, UploadStatus
from src.core.exception_base import NotFoundError, BadRequest, DatabaseError
from src.utils.log import get_logger
from src.service.storage import store_upload
from src.utils.log import get_logger

logger = get_logger(__name__)


class UploadService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_upload(
        self, api_key_id: uuid.UUID, file: UploadFile
    ) -> Upload:
        uri = await store_upload(file)

        upload = Upload(
            api_key_id=api_key_id,
            uri=uri,
            status=UploadStatus.UNATTACHED.value,
            original_filename=file.filename,
            file_size=file.size,
        )
        self.db.add(upload)
        try:
            await self.db.flush()
            await self.db.refresh(upload)
            await self.db.commit()
            logger.info(
                "Upload %s created for API key %s (file: %s)",
                upload.id, api_key_id, file.filename,
            )
            return upload
        except Exception as e:
            await self.db.rollback()
            logger.error("Error creating upload: %s", e)
            raise DatabaseError()

    async def find_by_uri(
        self, uri: str, api_key_id: uuid.UUID
    ) -> Upload | None:
        """Look up an upload by storage URI — used in POST /job to check if the URI is a prior upload."""
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
        # Verify upload exists and belongs to this API key before mutating
        upload = await self.get_upload(upload_id, api_key_id)

        # Reject if already attached (idempotency guard)
        if upload.status == UploadStatus.ATTACHED.value:
            raise BadRequest("Upload is already attached to a job")

        # Flip to ATTACHED so the 24h cleanup sweep skips it
        upload.status = UploadStatus.ATTACHED.value
        try:
            await self.db.flush()
            await self.db.refresh(upload)
            await self.db.commit()
            logger.info("Upload %s attached", upload.id)
            return upload
        except Exception as e:
            await self.db.rollback()
            logger.error("Error attaching upload %s: %s", upload.id, e)
            raise DatabaseError()

    async def cleanup_unattached(self, older_than: datetime) -> int:
        """Delete unattached uploads older than the given timestamp — runs on a scheduled job."""
        result = await self.db.execute(
            select(Upload).where(
                Upload.status == UploadStatus.UNATTACHED.value,
                Upload.created_at < older_than,
            )
        )
        uploads = list(result.scalars().all())
        for upload in uploads:
            await self.db.delete(upload)
        try:
            await self.db.commit()
            logger.info("Cleaned up %d unattached uploads", len(uploads))
            return len(uploads)
        except Exception as e:
            await self.db.rollback()
            logger.error("Error cleaning up uploads: %s", e)
            raise DatabaseError()
