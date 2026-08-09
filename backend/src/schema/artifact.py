import enum
from datetime import datetime

from pydantic import BaseModel


class _ArtifactStatus(str, enum.Enum):
    """Processing status of an artifact through the pipeline."""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


class _SourceInfo(BaseModel):
    platform: str  # platform identifier from yt-dlp extractor key — "youtube", "instagram", etc.
    video_id: str # unique video/media ID from the platform
    url: str # original URL the user submitted
    title: str | None = None # human-readable title from the platform



class _FileInfo(BaseModel):
    path: str # absolute path to the file on disk in the job workspace
    size_bytes: int # file size in bytes
    container: str # container format — "mp4", "webm", "m4a", etc.


class _MediaInfo(BaseModel):
    duration_seconds: float # duration in seconds (float for sub-second precision)
    width: int | None = None # video resolution — None for audio-only sources
    height: int | None = None # frames per second — None for audio

    fps: float | None = None # codec strings — "none" when the stream is absent (e.g. video-only has acodec="none")

    video_codec: str | None = None
    audio_codec: str | None = None
    video_bitrate: int | None = None
    audio_bitrate: int | None = None
    # bitrates in bits per second, None when unknown


class Artifact(BaseModel):

    id: str #unique artifact identifier, e.g. "art_<uuid short>"
    job_id: str #owning job identifier
    source: _SourceInfo # source metadata from the download/extraction phase
    file: _FileInfo # physical file properties
    media: _MediaInfo # media stream properties — populated by ffprobe for local files
    status: _ArtifactStatus = _ArtifactStatus.COMPLETED
    created_at: datetime #when the artifact was created
    output_url: str | None = None # CDN/R2 URL set after step output is uploaded to R2
    
