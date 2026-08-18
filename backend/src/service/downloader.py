# ── yt-dlp download layer  (dumb media adapter) ──────────────────────────────
# Three responsibilities:
#   extract_info   — pull metadata from a URL without downloading
#   download       — fetch media to an isolated job workspace
#   build_artifact — transform extracted info into the Artifact schema that the FFmpeg pipeline consumes

# This module is synchronous — it calls yt-dlp's Python API directly.
# Celery tasks invoke it from worker processes; it is never called from the FastAPI event loop.


import os
from datetime import datetime, timezone
from pathlib import Path

import yt_dlp

from src.schema.artifact import (
    Artifact,
    _ArtifactStatus,
    _FileInfo,
    _MediaInfo,
    _SourceInfo,
)
from src.schema.download import DownloadResult, _ExtractedInfo, _FormatPreference
from src.utils.config import config
from src.utils.ffprobe import probe_media
from src.utils.log import get_logger

logger = get_logger(__name__)

# format preference → yt-dlp format string lookup for video sources
_VIDEO_FORMAT_MAP: dict[_FormatPreference, str] = {
    _FormatPreference.BEST:      "bestvideo+bestaudio/best",
    _FormatPreference.SMALLEST:  "worstvideo+worstaudio/worst",
    _FormatPreference.RES_480P:  "bestvideo[height<=480]+bestaudio/best[height<=480]",
    _FormatPreference.RES_720P:  "bestvideo[height<=720]+bestaudio/best[height<=720]",
    _FormatPreference.RES_1080P: "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    _FormatPreference.RES_4K:    "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
}

# format preference → yt-dlp format string lookup for audio sources
_AUDIO_FORMAT_MAP: dict[_FormatPreference, str] = {
    _FormatPreference.BEST:     "bestaudio/best",
    _FormatPreference.SMALLEST: "worstaudio/worst",
}

# ── YouTube client configs ────────────────────────────────────────────────────
# android_vr: high-quality DASH formats, no PO token needed, but blocked by
#   datacenter IPs (403 on download).  Tried first.
# web_safari: HLS manifests (max 480p), requires PO token via bgutil, works
#   through datacenter proxies.  Used as fallback.

_POT_PROVIDER_BASE_URL = os.environ.get("POT_PROVIDER_BASE_URL", "")

_ANDROID_VR_EXTRACTOR_ARGS: dict = {
    "youtube": {"player_client": ["android_vr"]},
}

_WEB_SAFARI_EXTRACTOR_ARGS: dict = {
    "youtube": {
        "player_client": ["web_safari"],
        "fetch_pot": ["always"],
    },
}
if _POT_PROVIDER_BASE_URL:
    _WEB_SAFARI_EXTRACTOR_ARGS["youtubepot-bgutilhttp"] = {
        "base_url": [_POT_PROVIDER_BASE_URL],
    }


# ── Private helpers───────────────


def _resolve_format_string(fmt: _FormatPreference, source_type: str) -> str:
    """Translate a FormatPreference + source_type into a yt-dlp format string."""
    if source_type == "audio":
        return _AUDIO_FORMAT_MAP[fmt]
    return _VIDEO_FORMAT_MAP[fmt]


def _build_ydl_opts(
    workspace_dir: str,
    format_string: str,
    download: bool = True,
    client: str = "android_vr",
) -> dict:
    """Construct the options dict passed to yt-dlp's YoutubeDL.

    *client* selects the YouTube player client.  ``"android_vr"`` offers
    high-quality DASH formats but is blocked by datacenter IPs;``"web_safari"`` offers HLS (max 480p) with PO token and works through proxies.
    """
    extractor_args = (
        _WEB_SAFARI_EXTRACTOR_ARGS if client == "web_safari"
        else _ANDROID_VR_EXTRACTOR_ARGS
    )

    opts: dict = {
        "outtmpl": str(Path(workspace_dir) / "input.%(ext)s"),
        "format": format_string,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
        "js_runtimes": {"deno": {}},
        "remote_components": ["ejs:github"],
        "extractor_args": extractor_args,
    }

    if not download:
        opts["skip_download"] = True

    cookie_file = config.ytdlp_cookie_file
    if cookie_file:
        opts["cookiefile"] = cookie_file

    if config.yt_proxy_url:
        opts["proxy"] = config.yt_proxy_url

    return opts


def _is_client_blocked(exc: Exception) -> bool:
    """True when the error looks like a YouTube client/IP block (403, bot gate)."""
    msg = str(exc).lower()
    return "403" in msg or "forbidden" in msg or "sign in to confirm" in msg


def _get_file_size(path: str) -> int:
    """Return file size in bytes, following symlinks if needed."""
    return os.stat(path, follow_symlinks=True).st_size


def assert_size_under_limit(path: str) -> None:
    """Raise ValueError if file exceeds the configured max download size."""
    size = _get_file_size(path)
    if size > config.max_download_size_bytes:
        limit_mb = config.max_download_size_bytes / (1024 * 1024)
        actual_mb = size / (1024 * 1024)
        logger.warning(f"File size {actual_mb:.1f} MB exceeds limit {limit_mb:.1f} MB")
        raise ValueError("Downloaded file exceeds size limit")


def guess_container(path: str) -> str:
    """Extract the file extension (without dot) as the container name."""
    return Path(path).suffix.lstrip(".") or "unknown"


def _safe_float(value: object) -> float | None:
    """Coerce *value* to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _raw_to_extracted_info(raw: dict) -> _ExtractedInfo:
    """Pull just the fields we need from yt-dlp's response.

    yt-dlp returns ~100+ fields; we only keep the ~15 that the pipeline actually uses.
    """
    is_playlist = raw.get("_type") == "playlist"

    if is_playlist:
        raw_entries: list[dict] = raw.get("entries") or []
        entries = [_raw_to_extracted_info(e) for e in raw_entries if e is not None]

        return _ExtractedInfo(
            platform=(raw.get("extractor_key") or "unknown").lower(),
            video_id=raw.get("id") or "playlist",
            url=raw.get("webpage_url") or "",
            title=raw.get("title") or "",
            description=raw.get("description"),
            is_playlist=True,
            playlist_title=raw.get("title"),
            playlist_count=raw.get("playlist_count") or len(entries),
            entries=entries or None,
        )

    return _ExtractedInfo(
        platform=(raw.get("extractor_key") or "unknown").lower(),
        video_id=raw.get("id") or "unknown",
        url=raw.get("webpage_url") or "",
        title=raw.get("title") or "",
        description=raw.get("description"),
        duration_seconds=_safe_float(raw.get("duration")),
        width=raw.get("width"),
        height=raw.get("height"),
        fps=raw.get("fps"),
        video_codec=raw.get("vcodec"),
        audio_codec=raw.get("acodec"),
        video_bitrate=int(round(raw["vbr"])) if raw.get("vbr") else None,
        audio_bitrate=int(round(raw["abr"])) if raw.get("abr") else None,
        ext=raw.get("ext"),
    )


def build_source_meta(info: _ExtractedInfo) -> dict:
    """Pre-populate Job.source_metadata before download starts.

    Allows the API to return media metadata without waiting for download to complete.
    """
    return {
        "source": {
            "platform": info.platform,
            "video_id": info.video_id,
            "url": info.url,
            "title": info.title,
            "description": info.description,
        },
        "media": {
            "duration_seconds": info.duration_seconds,
            "width": info.width,
            "height": info.height,
            "fps": info.fps,
            "video_codec": info.video_codec,
            "audio_codec": info.audio_codec,
            "video_bitrate": info.video_bitrate,
            "audio_bitrate": info.audio_bitrate,
        },
    }


# ── Public API ───────────────────────────────────────────────────────────────


def extract_info(url: str) -> _ExtractedInfo:
    """Pull metadata from *url* without downloading any media.

    Returns a clean ``ExtractedInfo`` — no raw yt-dlp dicts, no subtitles, no format lists, no HTTP metadata.  Use ``.is_playlist`` and ``.entries`` for playlist detection.

    Raises ``yt_dlp.utils.DownloadError`` (or subclasses) on failure.
    """
    opts = _build_ydl_opts(
        workspace_dir="/tmp",
        format_string="best",
        download=False,
    )
    with yt_dlp.YoutubeDL(opts) as ydl:
        logger.info(f"Extracting metadata from {url}")
        raw = ydl.extract_info(url, download=False)
        logger.info(f"Metadata extracted — type={raw.get('_type', 'video')}, title={raw.get('title', 'unknown')}")
        return _raw_to_extracted_info(raw)
    #TODO: error handling


def download(
    url: str,
    workspace_dir: str,
    *,
    fmt: _FormatPreference = _FormatPreference.BEST,
    source_type: str = "video",
) -> DownloadResult:
    """Download media from *url* into *workspace_dir*.

    Args:
        url: The media URL to download.
        workspace_dir: Absolute path to the job's isolated workspace directory. Must already exist (caller creates it).
        fmt: Quality preference — default BEST.
        source_type: ``"video"`` or ``"audio"`` — affects format-string selection.

    Returns:
        A ``DownloadResult`` with the local file path, stripped-down metadata, and pre-built ``Artifact`` schema ready for the FFmpeg pipeline.

    Raises:
        yt_dlp.utils.DownloadError:  Download or extraction failure.
        ValueError: File exceeds ``max_download_size_bytes``.
    """
    format_string = _resolve_format_string(fmt, source_type)

    # Try android_vr first (high-quality DASH), fall back to web_safari + PO
    # token (HLS, max 480p) when the client is blocked by the network.
    raw: dict = {}
    for client in ("android_vr", "web_safari"):
        opts = _build_ydl_opts(workspace_dir, format_string, download=True, client=client)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                logger.info(f"Downloading {url} (format={fmt.value}, client={client})")
                raw = ydl.extract_info(url, download=True)
                logger.info(f"Download complete — title={raw.get('title', 'unknown')} (client={client})")
                break
        except yt_dlp.utils.DownloadError as exc:
            if _is_client_blocked(exc) and client == "android_vr":
                logger.warning(f"android_vr blocked for {url}, falling back to web_safari: {exc}")
                continue
            raise

    ext = raw.get("ext", "mp4")
    local_path = str(Path(workspace_dir) / f"input.{ext}")

    if not os.path.exists(local_path):
        files = sorted(Path(workspace_dir).iterdir())
        if files:
            local_path = str(files[0])
        else:
            logger.error(f"No file found in workspace: {workspace_dir}")
            raise FileNotFoundError("Downloaded file not found")

    assert_size_under_limit(local_path)

    extracted = _raw_to_extracted_info(raw)
    artifact = build_artifact(extracted, local_path, job_id="unknown")

    return DownloadResult(
        local_path=local_path,
        metadata=extracted,
        artifact=artifact,
    )


def build_artifact(info: _ExtractedInfo, local_path: str, job_id: str = "unknown") -> Artifact:
    """Transform extracted info into a canonical ``Artifact`` schema.

    This is a pure data transformation — no I/O, no side effects.
    The returned ``Artifact`` is the contract between the yt-dlp layer and the FFmpeg layer; FFmpeg workers read from it and never call ffprobe.

    *job_id* is bound after the artifact is created (the Celery task knows the job ID; the downloader itself doesn't).
    """
    source = _SourceInfo(
        platform=info.platform,
        video_id=info.video_id,
        url=info.url,
        title=info.title,
        description=info.description,
    )

    try:
        size_bytes = _get_file_size(local_path)
    except OSError:
        size_bytes = 0

    container = guess_container(local_path)

    file_info = _FileInfo(
        path=local_path,
        size_bytes=size_bytes,
        container=container,
    )

    media = _MediaInfo(
        duration_seconds=info.duration_seconds or 0.0,
        width=info.width,
        height=info.height,
        fps=info.fps,
        video_codec=info.video_codec,
        audio_codec=info.audio_codec,
        video_bitrate=info.video_bitrate,
        audio_bitrate=info.audio_bitrate,
    )

    return Artifact(
        id=f"art_{info.video_id}",
        job_id=job_id,
        source=source,
        file=file_info,
        media=media,
        status=_ArtifactStatus.COMPLETED,
        created_at=datetime.now(timezone.utc),
    )


def build_artifact_from_local(
    local_path: str,
    source_uri: str,
    job_id: str = "unknown",
) -> Artifact:
    """Build an artifact from a local file without yt-dlp metadata.

    Used for upload-sourced jobs (R2 → workspace). MediaInfo fields are populated by probing the file with ffprobe so the Artifact accurately reflects the media on disk.
    """
    try:
        size_bytes = _get_file_size(local_path)
    except OSError:
        size_bytes = 0

    container = guess_container(local_path)

    source = _SourceInfo(
        platform="upload",
        video_id=Path(source_uri).stem,
        url=source_uri,
        title=Path(source_uri).stem or "video",
    )
    file_info = _FileInfo(
        path=local_path,
        size_bytes=size_bytes,
        container=container,
    )
    media = probe_media(local_path)

    return Artifact(
        id=f"art_{Path(source_uri).stem}",
        job_id=job_id,
        source=source,
        file=file_info,
        media=media,
        status=_ArtifactStatus.COMPLETED,
        created_at=datetime.now(timezone.utc),
    )
