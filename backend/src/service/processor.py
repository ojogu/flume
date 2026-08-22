# ── FFmpeg operation execution layer ─────────────────────────────────────────
# Executes media operations (trim, mute, compress, cut, watermark, subtitle, etc.) by building FFmpeg command lists, running them via subprocess, and returning a ProcessResult. On failure, stderr is routed to the LLM error summarizer.

from __future__ import annotations

import os
import re
import subprocess
import textwrap
import uuid
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar

import requests
from sqlalchemy.ext.asyncio import AsyncSession

from src.schema.artifact import (
    Artifact,
    _ArtifactStatus,
    _FileInfo,
    _SourceInfo,
)
from src.schema.processor import ProcessError, ProcessResult
from src.service.llm_error_summarizer import summarize_ffmpeg_error
from src.utils.ffprobe import probe_media
from src.utils.log import get_logger
from src.utils.resolution import (
    DEFAULT_PRESET,
    derive_aspect_ratio,
    derive_orientation,
    ensure_even,
    get_dimensions,
)

logger = get_logger(__name__)

# ── Meme caption font ────────────────────────────────────────────────────────────
_MEME_FONT_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def _get_meme_font_path() -> str:
    for path in _MEME_FONT_PATHS:
        if os.path.exists(path):
            return path
    return _MEME_FONT_PATHS[0]

_MEME_BAND_RATIO = 10
_MEME_MAX_FONT_SIZE = 40
_MEME_MIN_FONT_SIZE = 18
_MEME_FONT_COLOR = "black"
_MEME_BACKGROUND_COLOR = "white"

# GIF output is capped at this width (larger sources are downscaled; small ones never upscaled).
_GIF_MAX_WIDTH = 576


class ProcessorService:
    """FFmpeg execution service. Each operation is a private method that builds an FFmpeg command, runs it via ``_run_ffmpeg``, and on success attaches an ``Artifact`` built from the output file. ``execute_operation`` is the single public entry point used by the ``jobs.media.execute`` Celery task."""

    # ── Handler registry ──────────────────────────────────
    # Maps operation name → bound method name. Method names are strings (not direct references) because the class body can't forward-reference methods defined below — resolution happens at call time via getattr.
    _HANDLERS: ClassVar[dict[str, str]] = {
        "trim": "_trim",
        "mute": "_mute",
        "thumbnail": "_thumbnail",
        "extract_audio": "_extract_audio",
        "gif": "_gif",
        "compress": "_compress",
        "resize": "_resize",
        "transcode": "_transcode",
        "cut": "_cut",
        "watermark": "_watermark",
        "subtitle": "_subtitle",
        "join": "_join",
        "meme": "_meme",
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Public dispatch ──────────────────────────────

    async def execute_operation(
        self,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
        input_path: str,
        workspace: Path,
    ) -> ProcessResult:
        """Dispatch to the registered handler for *operation*."""
        job_id_str = str(job_id)
        handler_name = self._HANDLERS.get(operation)
        if handler_name is None:
            logger.error(f"No handler registered for operation '{operation}' — job={job_id_str}, step={step_index}")
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="unimplemented_operation",
                    summary=f"[{operation}] Operation not implemented",
                    cause=f"No handler registered for operation '{operation}'",
                    fix=None,
                    raw_stderr="",
                ),
            )

        handler = getattr(self, handler_name)

        logger.info(
            f"Executing operation '{operation}' for job {job_id_str} step {step_index} "
            f"— input={input_path}, workspace={workspace}"
        )
        return await handler(input_path, workspace, job_id, step_index, operation, params)

    # ── Operations ──────────────────────────────────

    async def _trim(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Clip a segment from the input between ``start`` and ``end``. Re-encodes to H.264 + AAC for frame-accurate cutting."""
        job_id_str = str(job_id)
        start = params["start"]
        end = params.get("end")  # optional — None means "till end of video"

        if end is not None and end <= start:
            logger.warning(
                f"[{operation}] job={job_id_str} step={step_index} — "
                f"end ({end}) must be > start ({start})"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="invalid_params",
                    summary=f"[trim] 'end' ({end}) must be greater than 'start' ({start})",
                    cause="'end' param was not greater than 'start'",
                    fix="Provide start < end with both values >= 0.",
                    raw_stderr="",
                ),
            )

        if end is None:
            media = probe_media(input_path)
            end = media.duration_seconds or 0

        output_path = str(workspace / f"step_{step_index}_output.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ss", str(start),
            "-to", str(end),
            "-c:v", "libx264",
            "-c:a", "aac",
            output_path,
        ]
        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="trim",
        )
        return ProcessResult(
            success=True,
            output_path=output_path,
            artifact=artifact,
        )

    async def _mute(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Remove the audio stream from the input video."""
        output_path = str(workspace / f"step_{step_index}_output.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-c:v", "copy",
            "-an",
            output_path,
        ]
        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="mute",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    async def _thumbnail(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Extract a single frame from the video as a JPEG."""
        timestamp = params["timestamp"]
        output_path = str(workspace / f"step_{step_index}_output.jpg")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ss", str(timestamp),
            "-vframes", "1",
            "-q:v", "2",  # JPEG quality: 2=high, 31=low
            output_path,
        ]
        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="thumbnail",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    async def _extract_audio(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Strip video and encode audio to mp3 or aac."""
        fmt = params["format"]  # required=true, validated by Gate 3
        output_path = str(workspace / f"step_{step_index}_output.{fmt}")
        if fmt == "mp3":
            cmd = ["ffmpeg", "-y", "-i", input_path, "-vn", "-c:a", "libmp3lame", "-q:a", "2", output_path]
        else:  # aac
            cmd = ["ffmpeg", "-y", "-i", input_path, "-vn", "-c:a", "aac", "-strict", "experimental", output_path]

        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="extract_audio",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    async def _gif(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Convert a video segment to a GIF using two-pass palette generation for better quality."""
        job_id_str = str(job_id)
        start = params["start"]
        end = params.get("end")  # optional — None means "till end of video"
        fps = params.get("fps", 15)

        if end is not None and end <= start:
            logger.warning(
                f"[{operation}] job={job_id_str} step={step_index} — "
                f"end ({end}) must be > start ({start})"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="invalid_params",
                    summary=f"[gif] 'end' ({end}) must be greater than 'start' ({start})",
                    cause="'end' param was not greater than 'start'",
                    fix="Provide start < end with both values >= 0.",
                    raw_stderr="",
                ),
            )

        media = probe_media(input_path)
        duration = media.duration_seconds or 0
        if start >= duration:
            logger.warning(
                f"[{operation}] job={job_id_str} step={step_index} — "
                f"start ({start}) is beyond video duration ({duration}s)"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="invalid_params",
                    summary=f"[gif] 'start' ({start}) is beyond video duration ({duration}s)",
                    cause="Requested segment begins at or after the end of the input video.",
                    fix=f"Provide 'start' < {duration}.",
                    raw_stderr="",
                ),
            )

        if end is None:
            end = duration
        elif end > duration:
            logger.info(
                f"[{operation}] job={job_id_str} step={step_index} — "
                f"clamping end ({end}) to duration ({duration}s)"
            )
            end = duration

        if end - start < 0.1:
            logger.warning(
                f"[{operation}] job={job_id_str} step={step_index} — "
                f"segment too short ({end - start:.3f}s between start={start} and end={end})"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="invalid_params",
                    summary=f"[gif] Segment too short ({end - start:.2f}s). Need at least 0.1s.",
                    cause="'end' and 'start' are (nearly) identical after duration clamping.",
                    fix="Provide a wider start/end range.",
                    raw_stderr="",
                ),
            )

        palette_path = str(workspace / f"step_{step_index}_palette.png")  # intermediate; cleaned up after
        output_path = str(workspace / f"step_{step_index}_output.gif")

        # Scale caps output width without upscaling small sources; identical chain in both passes so paletteuse sees matching dimensions.
        gif_scale = f"scale='min({_GIF_MAX_WIDTH},iw)':-2:flags=lanczos"

        # Pass 1: generate palette. Seek options go BEFORE -i (input seeking) — placing them after -i with palettegen produces an empty image2 output while ffmpeg still exits 0.
        cmd_palette = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-to", str(end),
            "-i", input_path,
            "-vf", f"{gif_scale},fps={fps},palettegen",
            "-update", "1",
            palette_path,
        ]
        result = await self._run_ffmpeg(cmd_palette, operation, params, input_path, palette_path, job_id, step_index)
        if not result.success:
            with suppress(OSError):
                os.remove(palette_path)
            return result

        # Pass 2: apply palette to produce GIF — explicit stream mapping, no auto-selection.
        cmd_gif = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-to", str(end),
            "-i", input_path,
            "-i", palette_path,
            "-filter_complex", f"[0:v]{gif_scale},fps={fps}[v];[v][1:v]paletteuse",
            output_path,
        ]
        result = await self._run_ffmpeg(cmd_gif, operation, params, input_path, output_path, job_id, step_index)
        if not result.success:
            return result

        # Clean up palette file
        with suppress(OSError):
            os.remove(palette_path)

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="gif",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    # CRF: lower = better quality, larger file. 28=web quality, 23=default, 18=visually lossless.
    _CRF_MAP: ClassVar[dict[str, int]] = {"low": 28, "medium": 23, "high": 18}

    async def _compress(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Re-encode video at a lower CRF to reduce file size. Audio is re-encoded to AAC.

        If params.resolution is set, the video is scaled to the target resolution before
        CRF compression is applied.
        """
        quality = params.get("quality", "medium")
        crf = self._CRF_MAP[quality]
        resolution = params.get("resolution")

        output_path = str(workspace / f"step_{step_index}_output.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
        ]

        # If resolution is specified, scale to target dimensions first.
        if resolution:
            media = probe_media(input_path)
            if media.width is None or media.height is None:
                return ProcessResult(
                    success=False,
                    error=ProcessError(
                        code="invalid_input",
                        summary="[compress] Cannot determine source resolution",
                        cause="Input video has no video stream.",
                        fix="Provide a valid video file.",
                        raw_stderr="",
                    ),
                )
            ar = derive_aspect_ratio(media.width, media.height)
            dims = ensure_even(get_dimensions(ar, resolution))
            width, height = dims["width"], dims["height"]
            cmd.extend([
                "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            ])

        cmd.extend([
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", "medium",
            "-c:a", "aac",
            output_path,
        ])

        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="compress",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    async def _resize(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Scale video to a target resolution.

        Resolution is determined by the following priority:
        1. Explicit width/height — use directly (escape hatch for arbitrary dimensions)
        2. orientation + resolution — lookup in table for exact dimensions
        3. Only orientation — lookup with DEFAULT_PRESET (1080p)
        4. Only resolution — probe source for aspect ratio, then lookup
        5. Neither specified — keep source as-is
        """
        width = params.get("width")
        height = params.get("height")
        orientation = params.get("orientation")
        resolution = params.get("resolution")

        # Case 1: explicit width/height (escape hatch)
        if width is not None or height is not None:
            width = width or -1
            height = height or -1
        # Case 2: orientation + resolution — lookup directly
        elif orientation and resolution:
            dims = ensure_even(get_dimensions(orientation, resolution))
            width, height = dims["width"], dims["height"]
        # Case 3: only orientation — lookup with DEFAULT_PRESET
        elif orientation:
            dims = ensure_even(get_dimensions(orientation, DEFAULT_PRESET))
            width, height = dims["width"], dims["height"]
        # Case 4: only resolution — probe source for aspect ratio
        elif resolution:
            media = probe_media(input_path)
            if media.width is None or media.height is None:
                return ProcessResult(
                    success=False,
                    error=ProcessError(
                        code="invalid_input",
                        summary="[resize] Cannot determine source resolution",
                        cause="Input video has no video stream.",
                        fix="Provide explicit width/height instead.",
                        raw_stderr="",
                    ),
                )
            ar = derive_aspect_ratio(media.width, media.height)
            dims = ensure_even(get_dimensions(ar, resolution))
            width, height = dims["width"], dims["height"]
        # Case 5: neither specified — keep source as-is
        else:
            # No-op: source dimensions preserved
            return ProcessResult(
                success=True,
                output_path=input_path,
                artifact=self._build_output_artifact(
                    output_path=input_path,
                    job_id=job_id,
                    step_index=step_index,
                    operation="resize",
                ),
            )

        output_path = str(workspace / f"step_{step_index}_output.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            "-c:v", "libx264",
            "-c:a", "aac",
            output_path,
        ]
        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="resize",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    # Container → (video codec, audio codec, output extension)
    _TRANSCODE_CODEC_MAP: ClassVar[dict[str, tuple[str, str, str]]] = {
        "mp4": ("libx264", "aac", "mp4"),
        "webm": ("libvpx-vp9", "libopus", "webm"),
        "mov": ("qtrle", "pcm_s16le", "mov"),
    }

    async def _transcode(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Convert video to a different container/codec format (mp4, webm, or mov).

        If params.resolution is set, the video is scaled to the target resolution
        before being re-encoded in the target format.
        """
        fmt = params["format"]  # required=true, validated by Gate 3
        vcodec, acodec, ext = self._TRANSCODE_CODEC_MAP[fmt]
        resolution = params.get("resolution")

        output_path = str(workspace / f"step_{step_index}_output.{ext}")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
        ]

        # If resolution is specified, scale to target dimensions first.
        if resolution:
            media = probe_media(input_path)
            if media.width is None or media.height is None:
                return ProcessResult(
                    success=False,
                    error=ProcessError(
                        code="invalid_input",
                        summary="[transcode] Cannot determine source resolution",
                        cause="Input video has no video stream.",
                        fix="Provide a valid video file.",
                        raw_stderr="",
                    ),
                )
            ar = derive_aspect_ratio(media.width, media.height)
            dims = ensure_even(get_dimensions(ar, resolution))
            width, height = dims["width"], dims["height"]
            cmd.extend([
                "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            ])

        cmd.extend([
            "-c:v", vcodec,
            "-c:a", acodec,
            output_path,
        ])

        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="transcode",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    async def _cut(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Remove segments from the video by extracting kept ranges and concatenating them."""
        job_id_str = str(job_id)
        segments = params["segments"]
        if not segments:
            logger.warning(
                f"[{operation}] job={job_id_str} step={step_index} — segments array is empty"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="invalid_params",
                    summary="[cut] At least one segment must be provided.",
                    cause="segments array is empty.",
                    fix="Provide segments=[{start:float, end:float}, ...].",
                    raw_stderr="",
                ),
            )

        # Sort segments, then compute the gaps between/around them as kept ranges (what to keep, inverse of cut ranges)
        sorted_segs = sorted(segments, key=lambda s: s["start"])
        kept_ranges: list[tuple[float, float]] = []
        prev_end = 0.0
        for seg in sorted_segs:
            start, end = float(seg["start"]), float(seg["end"])
            if start > prev_end:
                kept_ranges.append((prev_end, start))  # gap before this segment is kept
            prev_end = max(prev_end, end)

        # If last segment doesn't reach end-of-file, keep the remaining tail
        media = probe_media(input_path)
        duration = media.duration_seconds or 0
        if prev_end < duration:
            kept_ranges.append((prev_end, duration))

        # Branch on actual streams present so audio-only sources don't produce a broken [0:v] reference
        has_video = media.video_codec is not None
        has_audio = media.audio_codec is not None

        if not kept_ranges:
            logger.warning(
                f"[{operation}] job={job_id_str} step={step_index} — "
                f"segments cover entire video; nothing to keep | segments={segments}"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="invalid_params",
                    summary="[cut] No valid ranges to keep after processing segments.",
                    cause="Segments may cover the entire video.",
                    fix="Ensure segments do not cover the entire duration.",
                    raw_stderr="",
                ),
            )

        # Build trim+setpts filters per kept range, then concat into one output
        # FFmpeg concat expects segment-interleaved order: [v0][a0][v1][a1]... not [v0][v1][a0][a1]
        n = len(kept_ranges)
        filter_parts: list[str] = []
        for i, (s, e) in enumerate(kept_ranges):
            if has_video:
                filter_parts.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]")
            if has_audio:
                filter_parts.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a{i}]")

        if has_video and has_audio:
            concat_parts = "[v0][a0]" + "".join(f"[v{i}][a{i}]" for i in range(1, n))
            concat_parts += f"concat=n={n}:v=1:a=1[vout][aout]"
            filter_complex = ";".join([*filter_parts, concat_parts])
            output_path = str(workspace / f"step_{step_index}_output.mp4")
            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-filter_complex", filter_complex,
                "-map", "[vout]",
                "-map", "[aout]",
                "-c:v", "libx264",
                "-c:a", "aac",
                output_path,
            ]
        elif has_video:
            concat_parts = "[v0]" + "".join(f"[v{i}]" for i in range(1, n))
            concat_parts += f"concat=n={n}:v=1:a=0[vout]"
            filter_complex = ";".join([*filter_parts, concat_parts])
            output_path = str(workspace / f"step_{step_index}_output.mp4")
            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-filter_complex", filter_complex,
                "-map", "[vout]",
                "-c:v", "libx264",
                output_path,
            ]
        else:
            concat_parts = "[a0]" + "".join(f"[a{i}]" for i in range(1, n))
            concat_parts += f"concat=n={n}:v=0:a=1[aout]"
            filter_complex = ";".join([*filter_parts, concat_parts])
            output_path = str(workspace / f"step_{step_index}_output.mp4")
            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-filter_complex", filter_complex,
                "-map", "[aout]",
                "-c:a", "aac",
                output_path,
            ]
        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="cut",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    _WATERMARK_POSITIONS: ClassVar[dict[str, tuple[str, str]]] = {
        "top_left": ("0", "0"),
        "top_right": ("W-w", "0"),
        "bottom_left": ("0", "H-h"),
        "bottom_right": ("W-w", "H-h"),
        "center": ("(W-w)/2", "(H-h)/2"),
    }

    async def _watermark(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Overlay a watermark image onto the video at the specified position."""
        job_id_str = str(job_id)
        image_url = params["image_url"]
        position = params.get("position", "bottom_right")
        coords = self._WATERMARK_POSITIONS.get(position, ("W-w", "H-h"))

        try:
            logger.info(f"Downloading watermark image from {image_url}")
            resp = requests.get(image_url, timeout=30)
            resp.raise_for_status()
        except Exception as exc:
            logger.warning(
                f"[{operation}] job={job_id_str} step={step_index} — "
                f"watermark image download failed: {exc} | image_url={image_url}"
            )
            logger.exception(
                f"[{operation}] job={job_id_str} step={step_index} watermark download failed"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="download_failed",
                    summary=f"[watermark] Failed to download watermark image: {exc}",
                    cause=f"HTTP GET to '{image_url}' failed.",
                    fix="Verify the image URL is publicly accessible.",
                    raw_stderr=str(exc),
                ),
            )

        ext = Path(image_url).suffix.lstrip(".") or "png"
        wm_path = str(workspace / f"step_{step_index}_watermark.{ext}")
        with open(wm_path, "wb") as f:
            f.write(resp.content)

        # Probe input video to get dimensions for overlay position calculation
        media = probe_media(input_path)
        width = media.width or 0
        height = media.height or 0

        # Replace W/H placeholders with actual dimensions — FFmpeg evaluates these at runtime
        overlay_x = coords[0].replace("W", str(width)).replace("w", "")
        overlay_y = coords[1].replace("H", str(height)).replace("h", "")

        output_path = str(workspace / f"step_{step_index}_output.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-i", wm_path,
            "-filter_complex", f"overlay={overlay_x}:{overlay_y}",
            "-c:v", "libx264",
            "-c:a", "aac",
            output_path,
        ]
        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
        with suppress(OSError):
            os.remove(wm_path)  # clean up downloaded image
        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="watermark",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    async def _subtitle(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Burn subtitles into the video from an SRT file. Auto-generated subtitles are not yet supported."""
        job_id_str = str(job_id)
        if params.get("auto"):
            logger.warning(
                f"[{operation}] job={job_id_str} step={step_index} — "
                f"auto subtitles requested but not implemented"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="not_implemented",
                    summary="[subtitle] Auto-generated subtitles are not yet supported.",
                    cause="auto mode requires a Whisper transcription integration.",
                    fix="Provide a subtitle file via file_url.",
                    raw_stderr="",
                ),
            )

        file_url = params.get("file_url")
        if not file_url:
            logger.warning(
                f"[{operation}] job={job_id_str} step={step_index} — "
                f"no file_url provided and auto=false"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="invalid_params",
                    summary="[subtitle] Either 'file_url' or 'auto: true' must be provided.",
                    cause="No subtitle source specified.",
                    fix="Provide file_url pointing to an SRT subtitle file.",
                    raw_stderr="",
                ),
            )

        try:
            logger.info(f"Downloading subtitle file from {file_url}")
            resp = requests.get(file_url, timeout=30)
            resp.raise_for_status()
        except Exception as exc:
            logger.warning(
                f"[{operation}] job={job_id_str} step={step_index} — "
                f"subtitle file download failed: {exc} | file_url={file_url}"
            )
            logger.exception(
                f"[{operation}] job={job_id_str} step={step_index} subtitle download failed"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="download_failed",
                    summary=f"[subtitle] Failed to download subtitle file: {exc}",
                    cause=f"HTTP GET to '{file_url}' failed.",
                    fix="Verify the subtitle URL is publicly accessible.",
                    raw_stderr=str(exc),
                ),
            )

        srt_path = str(workspace / f"step_{step_index}_subtitles.srt")
        with open(srt_path, "wb") as f:
            f.write(resp.content)

        output_path = str(workspace / f"step_{step_index}_output.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", f"subtitles={srt_path}",
            "-c:v", "libx264",
            "-c:a", "aac",
            output_path,
        ]
        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
        with suppress(OSError):
            os.remove(srt_path)  # clean up downloaded subtitle file
        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="subtitle",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    async def _join(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Concatenate multiple video clips into one output using the FFmpeg concat filter.

        The clip local paths are read from input_path, which is a JSON file produced by the
        download step when clips are provided via params.clips.

        If params.resolution is set, all clips are scaled to match the first clip's aspect
        ratio at the target preset before concatenating. Otherwise a simple concat filter is
        used (all clips must already have the same resolution).
        """
        import json

        if not input_path:
            input_path = str(workspace / "join_clips.json")

        try:
            with open(input_path, "r") as f:
                clip_paths = json.load(f)
        except Exception as exc:
            logger.exception(f"[{operation}] job={job_id} failed to read clip paths from {input_path}")
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="invalid_input",
                    summary=f"[join] Failed to read clip paths: {exc}",
                    cause="The download step did not produce a valid clip list.",
                    fix="Verify the download step completed successfully.",
                    raw_stderr=str(exc),
                ),
            )

        n = len(clip_paths)
        preset:str = params.get("resolution")

        # Determine output path and filter complex based on whether resolution is specified.
        if preset:
            # Probe first clip to determine target aspect ratio.
            try:
                first_media = probe_media(clip_paths[0])
            except Exception as exc:
                logger.exception(f"[{operation}] job={job_id} failed to probe first clip")
                return ProcessResult(
                    success=False,
                    error=ProcessError(
                        code="probe_failed",
                        summary=f"[join] Failed to probe first clip: {exc}",
                        cause="Could not read metadata from the first clip.",
                        fix="Verify all clip URLs are valid media files.",
                        raw_stderr=str(exc),
                    ),
                )

            if first_media.width is None or first_media.height is None:
                return ProcessResult(
                    success=False,
                    error=ProcessError(
                        code="invalid_input",
                        summary="[join] First clip has no video stream",
                        cause="Cannot determine resolution for join operation.",
                        fix="Verify all clips are valid video files.",
                        raw_stderr="",
                    ),
                )

            aspect_ratio = derive_aspect_ratio(first_media.width, first_media.height)
            target_dims = ensure_even(get_dimensions(aspect_ratio, preset))
            target_w, target_h = target_dims["width"], target_dims["height"]

            # Build scale+pad filter for each clip, then concat.
            filter_parts = []
            for i in range(n):
                filter_parts.append(
                    f"[{i}:v]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
                    f"pad={target_w}:{target_h}:-1:-1,setsar=1[v{i}_scaled]"
                )

            concat_inputs = "".join(f"[v{i}_scaled][{i}:a]" for i in range(n))

            filter_complex = (
                ";".join(filter_parts)
                + ";"
                + concat_inputs
                + f"concat=n={n}:v=1:a=1[vout][aout]"
            )
        else:
            # No resolution specified — simple concat (all clips must already match).
            filter_complex = (
                "".join(f"[{i}:v][{i}:a]" for i in range(n))
                + f"concat=n={n}:v=1:a=1[vout][aout]"
            )

        output_path = str(workspace / f"step_{step_index}_output.mp4")
        cmd = [
            "ffmpeg", "-y",
            *[arg for p in clip_paths for arg in ["-i", p]],
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-c:a", "aac",
            output_path,
        ]
        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)

        # Clean up downloaded clip files.
        for p in clip_paths:
            with suppress(OSError):
                os.remove(p)

        if not result.success:
            return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="join",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    # ── Meme caption helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _estimate_chars_per_line(font_size: int, band_width: int) -> int:
        char_width_approx = font_size * 0.6
        return max(1, int(band_width / char_width_approx))

    @staticmethod
    def _wrap_caption(text: str, chars_per_line: int) -> str:
        wrapped = textwrap.fill(text, width=chars_per_line)
        return wrapped.replace("\n", "\\n")

    @classmethod
    def _fit_font_size(cls, text: str, band_width: int, band_height: float) -> tuple[int, str]:
        size = _MEME_MAX_FONT_SIZE
        while size >= _MEME_MIN_FONT_SIZE:
            chars_per_line = cls._estimate_chars_per_line(size, band_width)
            wrapped = cls._wrap_caption(text, chars_per_line)
            lines = wrapped.count("\\n") + 1
            line_height = size * 1.2
            if lines * line_height <= band_height:
                return size, wrapped
            size -= 2
        chars_per_line = cls._estimate_chars_per_line(_MEME_MIN_FONT_SIZE, band_width)
        wrapped = cls._wrap_caption(text, chars_per_line)
        max_chars = int(chars_per_line * (band_height / (_MEME_MIN_FONT_SIZE * 1.2))) - 3
        if max_chars > 0 and len(wrapped) > max_chars:
            wrapped = wrapped[:max_chars] + "..."
        return _MEME_MIN_FONT_SIZE, wrapped

    # ── Meme caption ─────────────────────────────────────────────────────────────

    async def _meme(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Overlay a text caption in a white band at top or bottom of the frame."""
        caption = params.get("caption")
        if caption:
            caption = re.sub(r'https?://\S+', '', caption).strip()
        if not caption:
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="missing_caption",
                    summary="[meme] No caption provided",
                    cause="caption param is empty and no description was extracted from the source media",
                    fix="Provide a caption param or ensure the source has a description",
                    raw_stderr="",
                ),
            )
        position = params.get("position", "top")

        media = probe_media(input_path)
        has_video = media.video_codec is not None
        has_audio = media.audio_codec is not None
        width = media.width or 1280
        height = media.height or 720
        is_gif = input_path.lower().endswith(".gif")
        is_image = not has_video and not is_gif

        band_height = width // _MEME_BAND_RATIO
        font_size, wrapped_text = self._fit_font_size(caption, width, band_height)

        output_ext = Path(input_path).suffix.lstrip(".") or ("gif" if is_gif else "mp4")
        output_path = str(workspace / f"step_{step_index}_output.{output_ext}")

        if is_image:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.open(input_path).convert("RGBA")
            img_w, img_h = img.size

            new_h = img_h + band_height
            canvas = Image.new("RGBA", (img_w, new_h), _MEME_BACKGROUND_COLOR)

            if position == "top":
                canvas.paste(img, (0, band_height))
            else:
                canvas.paste(img, (0, 0))

            draw = ImageDraw.Draw(canvas)
            try:
                font = ImageFont.truetype(_get_meme_font_path(), font_size)
            except Exception:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), wrapped_text.replace("\\n", "\n"), font=font)
            text_h = bbox[3] - bbox[1]
            text_x = (img_w - (bbox[2] - bbox[0])) // 2
            if position == "top":
                text_y = (band_height - text_h) // 2
            else:
                text_y = img_h + (band_height - text_h) // 2

            draw.text((text_x, text_y), wrapped_text.replace("\\n", "\n"), fill=_MEME_FONT_COLOR, font=font)
            canvas.convert("RGB").save(output_path)

        else:
            pad_y = height if position == "top" else 0
            text_y = (band_height - font_size) // 2 if position == "top" else height + (band_height - font_size) // 2

            filter_complex = (
                f"[0:v]pad=iw:ih+{band_height}:0:{pad_y}:white,"
                f"drawtext=text='{wrapped_text}':"
                f"fontfile={_get_meme_font_path()}:"
                f"fontsize={font_size}:"
                f"fontcolor={_MEME_FONT_COLOR}:"
                f"x=(w-text_w)/2:"
                f"y={text_y}[out]"
            )

            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-filter_complex", filter_complex,
                "-map", "[out]",
            ]
            if has_audio and not is_gif:
                cmd += ["-map", "0:a", "-c:a", "aac"]
            cmd += [output_path]

            result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)
            if not result.success:
                return result

        artifact = self._build_output_artifact(
            output_path=output_path,
            job_id=job_id,
            step_index=step_index,
            operation="meme",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    # ── FFmpeg subprocess primitive ─────────────────────────────────────────

    async def _run_ffmpeg(
        self,
        cmd: list[str],
        operation: str,
        params: dict,
        input_path: str,
        output_path: str,
        job_id: uuid.UUID,
        step_index: int,
    ) -> ProcessResult:
        """Execute an FFmpeg command. Returns ProcessResult with output_path on success, error on failure."""
        job_id_str = str(job_id)
        logger.debug(f"FFmpeg cmd: {' '.join(cmd)}")
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            logger.error(f"ffmpeg binary not found on PATH — job={job_id_str}, step={step_index}, op={operation}")
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="ffmpeg_missing",
                    summary=f"[{operation}] FFmpeg is not installed on the worker",
                    cause="The 'ffmpeg' executable could not be found on PATH",
                    fix="Install FFmpeg on the worker host or set the configured path.",
                    raw_stderr="",
                ),
            )

        if proc.returncode != 0:
            stderr = proc.stderr or ""
            logger.warning(
                f"FFmpeg failed — job={job_id_str}, step={step_index}, op={operation}, exit={proc.returncode}"
            )
            error = await summarize_ffmpeg_error(
                operation=operation,
                params=params,
                input_path=input_path,
                output_path=output_path,
                stderr=stderr,
            )
            return ProcessResult(success=False, error=error)

        if not os.path.exists(output_path):
            stderr_tail = (proc.stderr or "")[-2000:]
            logger.error(
                f"FFmpeg exited 0 but output file missing — job={job_id_str}, step={step_index}, "
                f"op={operation}, path={output_path} | stderr_tail={stderr_tail}"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="missing_output",
                    summary=f"[{operation}] FFmpeg succeeded but produced no output file",
                    cause=f"Output path '{output_path}' does not exist after run",
                    fix="Inspect the FFmpeg command and the input file.",
                    raw_stderr=stderr_tail,
                ),
            )

        return ProcessResult(success=True, output_path=output_path)

    # ── Artifact construction ─────────────────────────────────────

    def _build_output_artifact(
        self,
        output_path: str,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
    ) -> Artifact:
        """Build an Artifact from the output file. Probes media info with ffprobe; platform="pipeline" marks it as FFmpeg-derived."""
        try:
            size_bytes = os.stat(output_path, follow_symlinks=True).st_size
        except OSError:
            size_bytes = 0

        container = Path(output_path).suffix.lstrip(".") or "unknown"

        short_job = str(job_id).split("-")[0]
        source = _SourceInfo(
            platform="pipeline",
            video_id=f"{short_job}_step_{step_index}",
            url=output_path,
        )
        file_info = _FileInfo(
            path=output_path,
            size_bytes=size_bytes,
            container=container,
        )
        media = probe_media(output_path)

        return Artifact(
            id=f"art_{short_job}_step_{step_index}",
            job_id=str(job_id),
            source=source,
            file=file_info,
            media=media,
            status=_ArtifactStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
        )