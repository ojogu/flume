# ── Local disk storage ────────────────────────────────────────────────────────
# Writes uploaded files to disk under config.upload_dir (default /tmp/flume/uploads).
# Returns a file:// URI. Swap to R2/S3 for production deployment.

import uuid
from pathlib import Path

from fastapi import UploadFile

from src.utils.config import config


async def store_upload(file: UploadFile) -> str:
    upload_dir = Path(config.upload_dir) / str(uuid.uuid4())
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / (file.filename or "upload")
    content = await file.read()
    file_path.write_bytes(content)

    return file_path.as_uri()
