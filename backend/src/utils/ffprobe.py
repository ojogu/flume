import json
import subprocess

from src.schema.artifact import _MediaInfo
from src.utils.log import get_logger

logger = get_logger(__name__)


def probe_media(file_path: str) -> _MediaInfo:
    """Probe a local media file with ffprobe and return its media metadata.

    Call this when you need to inspect a media file on disk and retrieve its codec, resolution, duration, or bitrate — for example, to build an accurate Artifact after a file lands in a workspace.

    Raises RuntimeError if ffprobe is missing, the file is not found,  or ffprobe fails for any reason.
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(file_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        raise RuntimeError(
            f"ffprobe binary not found on PATH — cannot inspect media file: {file_path}"
        ) from None

    if result.returncode != 0:
        raise RuntimeError(
            f"ffprobe failed for '{file_path}' (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"ffprobe returned invalid JSON for '{file_path}': {e}"
        ) from None

    return _parse_probe(data)


def _parse_probe(data: dict) -> _MediaInfo:
    """Map raw ffprobe JSON output to a _MediaInfo object.

    Handles both audio-only and video files by detecting the presence of a video stream. Called internally by probe_media() after ffprobe returns.
    """
    format_info = data.get("format") or {}
    streams = data.get("streams") or []

    duration_seconds = _parse_duration(format_info.get("duration"))

    video_stream = next(
        (s for s in streams if s.get("codec_type") == "video"),
        None,
    )
    audio_stream = next(
        (s for s in streams if s.get("codec_type") == "audio"),
        None,
    )

    if video_stream is None or video_stream.get("codec_name") == "none":
        return _MediaInfo(
            duration_seconds=duration_seconds,
            width=None,
            height=None,
            fps=None,
            video_codec=None,
            audio_codec=_audio_codec(audio_stream),
            video_bitrate=None,
            audio_bitrate=_audio_bitrate(audio_stream),
        )

    fps = _parse_fps(video_stream.get("r_frame_rate", "0/0"))

    return _MediaInfo(
        duration_seconds=duration_seconds,
        width=video_stream.get("width"),
        height=video_stream.get("height"),
        fps=fps,
        video_codec=video_stream.get("codec_name"),
        audio_codec=_audio_codec(audio_stream),
        video_bitrate=_video_bitrate(video_stream),
        audio_bitrate=_audio_bitrate(audio_stream),
    )


def _parse_duration(value: str | None) -> float:
    """Parse an ffprobe duration string to a float number of seconds.

    Returns 0.0 for None or unparseable values. Call this when extracting the duration field from an ffprobe format dict.
    """
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _parse_fps(rate_str: str | None) -> float | None:
    """Parse an ffprobe rational frame rate string to a float (e.g. "30000/1001" → 29.97).

    Returns None for None or unparseable values. Call this when extracting the r_frame_rate field from an ffprobe video stream dict.
    """
    if rate_str is None:
        return None
    try:
        num, denom = rate_str.split("/")
        return float(num) / float(denom)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def _video_bitrate(stream: dict | None) -> int | None:
    """Extract the bit_rate from a video stream dict, in bits per second.

    Returns None if the stream is None, has no bit_rate, or the value is unparseable. Call this when building _MediaInfo for a video file.
    """
    if stream is None:
        return None
    raw = stream.get("bit_rate")
    if raw is None:
        return None
    try:
        return int(raw)
    except (ValueError, TypeError):
        return None


def _audio_bitrate(stream: dict | None) -> int | None:
    """Extract the bit_rate from an audio stream dict, in bits per second.

    Returns None if the stream is None, has no bit_rate, or the value is unparseable. Call this when building _MediaInfo for any file with audio.
    """
    if stream is None:
        return None
    raw = stream.get("bit_rate")
    if raw is None:
        return None
    try:
        return int(raw)
    except (ValueError, TypeError):
        return None


def _audio_codec(stream: dict | None) -> str | None:
    """Return the codec_name from an audio stream dict, or None if no audio stream.

    Call this when populating the audio_codec field of _MediaInfo.
    """
    if stream is None:
        return None
    return stream.get("codec_name")
