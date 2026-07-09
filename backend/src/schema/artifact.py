from datetime import datetime


from pydantic import BaseModel


class SourceInfo(BaseModel):
    platform: str  # platform identifier from yt-dlp extractor key — "youtube", "instagram", etc.
    video_id: str # unique video/media ID from the platform
    url: str # original URL the user submitted



class FileInfo(BaseModel):
    path: str # absolute path to the file on disk in the job workspace
    size_bytes: int # file size in bytes
    container: str # container format — "mp4", "webm", "m4a", etc.


class MediaInfo(BaseModel):
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
    source: SourceInfo # source metadata from the download/extraction phase
    file: FileInfo # physical file properties
    media: MediaInfo # media stream properties — FFmpeg reads this, never runs ffprobe
    status: str = "completed" # processing status — "pending", "downloading", "completed", "failed"
    created_at: datetime #when the artifact was created
    
