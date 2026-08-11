import os
import shutil
import time
from pathlib import Path

from celery_app.celery import bg_task
from src.utils.config import config
from src.utils.log import get_logger

logger = get_logger(__name__)


@bg_task.task(
    name="celery_app.cleanup_stale_workspaces",
    ignore_result=True,
)
def cleanup_stale_workspaces() -> dict:
    cutoff = time.time() - (config.cleanup_max_age_hours * 3600)
    deleted = []
    errors = []

    for job_dir in os.listdir(config.workspaces_dir):
        path = Path(config.workspaces_dir) / job_dir
        if not path.is_dir():
            continue
        if path.stat().st_mtime < cutoff:
            try:
                logger.info(f"Deleting stale workspace {path}")
                shutil.rmtree(path)
                deleted.append(str(path))
            except Exception as e:
                logger.warning(f"Failed to delete {path}: {e}")
                errors.append(str(path))

    logger.info(f"Cleanup done — deleted {len(deleted)}, errors {len(errors)}")
    return {"deleted": deleted, "errors": errors}
