# ── Job cancellation flag ──────────────────────────────────────────────────
# A cancelled job's status lives in the database, but a running yt-dlp download
# can't cheaply poll Postgres from its progress hook. So cancelling also sets a
# short-lived Redis key that the worker reads with the sync client.
#
# Retry clears the flag; the TTL is a backstop for jobs that are never retried.

import time
from collections.abc import Callable

from yt_dlp.utils import DownloadCancelled

from src.utils.log import get_logger
from src.utils.redis import get_redis, get_redis_sync

logger = get_logger(__name__)

CANCEL_FLAG_TTL = 24 * 60 * 60  # seconds
_CHECK_INTERVAL = 1.0  # seconds between Redis reads inside the progress hook


def _key(job_id) -> str:
    return f"job:cancel:{job_id}"


class JobCancelled(DownloadCancelled):
    """Raised inside yt-dlp to abort a download whose job was cancelled.

    Subclasses yt-dlp's own ``DownloadCancelled`` so yt-dlp lets it propagate
    instead of treating it as a download error.
    """


async def set_cancel_flag(job_id) -> None:
    """Mark a job as cancelled for workers (async — called from request paths)."""
    try:
        redis = await get_redis()
        await redis.set(_key(job_id), "1", ex=CANCEL_FLAG_TTL)
    except Exception as e:  # the DB status is the source of truth; the flag only speeds up aborts
        logger.warning(f"Could not set cancel flag for job {job_id}: {e}")


async def clear_cancel_flag(job_id) -> None:
    """Remove the flag (used when a cancelled job is retried)."""
    try:
        redis = await get_redis()
        await redis.delete(_key(job_id))
    except Exception as e:
        logger.warning(f"Could not clear cancel flag for job {job_id}: {e}")


def is_cancel_requested(job_id) -> bool:
    """Sync check for workers. Fails open: if Redis is unreachable the job keeps running."""
    try:
        return bool(get_redis_sync().exists(_key(job_id)))
    except Exception:
        return False


def make_cancel_hook(job_id) -> Callable[[dict], None]:
    """yt-dlp progress hook that aborts the download once the job is cancelled.

    Reads Redis at most once a second so it adds no real overhead to downloads.
    """
    last_check = 0.0

    def hook(_progress: dict) -> None:
        nonlocal last_check
        now = time.monotonic()
        if now - last_check < _CHECK_INTERVAL:
            return
        last_check = now
        if is_cancel_requested(job_id):
            raise JobCancelled(f"job {job_id} cancelled")

    return hook
