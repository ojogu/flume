from datetime import datetime


from pydantic import BaseModel


class SourceInfo(BaseModel):
    # platform identifier from yt-dlp extractor key — "youtube", "instagram", etc.
    platform: str
    # unique video/media ID from the platform
    video_id: str
    # original URL the user submitted
    url: str


class FileInfo(BaseModel):
    # absolute path to the file on disk in the job workspace
    path: str
    # file size in bytes
    size_bytes: int
    # container format — "mp4", "webm", "m4a", etc.
    container: str


class MediaInfo(BaseModel):
    # duration in seconds (float for sub-second precision)
    duration_seconds: float
    # video resolution — None for audio-only sources
    width: int | None = None
    height: int | None = None
    # frames per second — None for audio
    fps: float | None = None
    # codec strings — "none" when the stream is absent (e.g. video-only has acodec="none")
    video_codec: str | None = None
    audio_codec: str | None = None
    # bitrates in bits per second, None when unknown
    video_bitrate: int | None = None
    audio_bitrate: int | None = None


class Artifact(BaseModel):
    # unique artifact identifier, e.g. "art_<uuid short>"
    id: str
    # owning job identifier
    job_id: str
    # source metadata from the download/extraction phase
    source: SourceInfo
    # physical file properties
    file: FileInfo
    # media stream properties — FFmpeg reads this, never runs ffprobe
    media: MediaInfo
    # processing status — "pending", "downloading", "completed", "failed"
    status: str = "completed"
    # when the artifact was created
    created_at: datetime
