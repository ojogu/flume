from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from src.schema.artifact import Artifact


class FormatPreference(str, Enum):
    # highest available resolution/quality — default
    BEST = "best"
    # lowest available resolution/quality
    SMALLEST = "smallest"
    # specific resolution targets — only valid for video sources
    RES_480P = "480p"
    RES_720P = "720p"
    RES_1080P = "1080p"
    RES_4K = "4k"


# Formats valid for audio sources — resolutions don't apply to audio
AUDIO_SAFE_FORMATS = {FormatPreference.BEST, FormatPreference.SMALLEST}


class PlaylistSelection(BaseModel):
    # 1-indexed positions of playlist entries to process — validated as > 0 by Pydantic's Field(gt=0)
    # Actual bounds checking (indices within playlist length) happens in the async worker
    entries: list[int] = Field(..., min_length=1)


class ExtractedInfo(BaseModel):
    """Stripped-down metadata from yt-dlp — only what FFmpeg and playlist logic need.

    No subtitles, chapters, format lists, HTTP headers, or other yt-dlp noise.
    For single videos all media fields are populated; for playlists only
    the playlist-level fields (title, count, entries) carry values.
    """
    # source identity
    platform: str
    video_id: str
    url: str
    title: str

    # playlist detection — entries is None for single videos
    is_playlist: bool = False
    playlist_title: str | None = None
    playlist_count: int | None = None
    entries: list[ExtractedInfo] | None = None

    # media properties (None for playlist-level entries)
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    video_bitrate: int | None = None
    audio_bitrate: int | None = None
    # container extension from yt-dlp — "mp4", "webm", etc.
    ext: str | None = None


class DownloadResult(BaseModel):
    # absolute path to the downloaded file in the job workspace
    local_path: str
    # stripped-down extracted info — never the full yt-dlp dict
    metadata: ExtractedInfo
    # pre-built artifact schema ready for the FFmpeg pipeline
    artifact: Artifact
