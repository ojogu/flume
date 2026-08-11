# ── FFmpeg operation execution layer ─────────────────────────────────────────
# Executes media operations (trim, mute, compress, cut, watermark, subtitle, etc.) by building FFmpeg command lists, running them via subprocess, and returning a ProcessResult. On failure, stderr is routed to the LLM error summarizer.

from __future__ import annotations

import asyncio
import os
import subprocess
import uuid
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar

import requests
import yt_dlp
from sqlalchemy.ext.asyncio import AsyncSession

from src.schema.artifact import (
    Artifact,
    _ArtifactStatus,
    _FileInfo,
    _SourceInfo,
)
from src.schema.processor import ProcessError, ProcessResult
from src.service.llm_error_summarizer import summarize_ffmpeg_error
from src.service.storage import storage
from src.utils.ffprobe import probe_media
from src.utils.http_client import get_http_client
from src.utils.log import get_logger

logger = get_logger(__name__)


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
        end = params["end"]

        if end <= start:
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
        start = params["start"]
        end = params["end"]
        fps = params.get("fps", 15)

        palette_path = str(workspace / f"step_{step_index}_palette.png")  # intermediate; cleaned up after
        output_path = str(workspace / f"step_{step_index}_output.gif")

        # Pass 1: generate palette
        cmd_palette = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ss", str(start),
            "-to", str(end),
            "-vf", f"fps={fps},palettegen",
            palette_path,
        ]
        result = await self._run_ffmpeg(cmd_palette, operation, params, input_path, palette_path, job_id, step_index)
        if not result.success:
            return result

        # Pass 2: apply palette to produce GIF
        cmd_gif = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ss", str(start),
            "-to", str(end),
            "-i", palette_path,
            "-filter_complex", f"fps={fps},paletteuse",
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
        """Re-encode video at a lower CRF to reduce file size. Audio is re-encoded to AAC."""
        quality = params.get("quality", "medium")
        crf = self._CRF_MAP[quality]
        output_path = str(workspace / f"step_{step_index}_output.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", "medium",  # balance between encoding speed and compression
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
            operation="compress",
        )
        return ProcessResult(success=True, output_path=output_path, artifact=artifact)

    _RESIZE_PRESETS: ClassVar[dict[str, tuple[int, int]]] = {
        "360p": (640, 360),
        "480p": (854, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "4k": (3840, 2160),
    }

    async def _resize(
        self,
        input_path: str,
        workspace: Path,
        job_id: uuid.UUID,
        step_index: int,
        operation: str,
        params: dict,
    ) -> ProcessResult:
        """Scale video to a target resolution using a preset or explicit width/height."""
        job_id_str = str(job_id)
        preset = params.get("preset")
        if preset:
            width, height = self._RESIZE_PRESETS.get(preset, (1280, 720))
        else:
            width = params.get("width")
            height = params.get("height")
            if not width and not height:
                logger.warning(
                    f"[{operation}] job={job_id_str} step={step_index} — "
                    f"neither preset nor width/height provided in params={params}"
                )
                return ProcessResult(
                    success=False,
                    error=ProcessError(
                        code="invalid_params",
                        summary="[resize] Either 'preset' or 'width'/'height' must be provided.",
                        cause="No resize target specified.",
                        fix="Provide preset=720p or width=1280&height=720.",
                        raw_stderr="",
                    ),
                )
            width = width or -1  # -1 tells FFmpeg to infer this dimension from the other and preserve aspect
            height = height or -1

        output_path = str(workspace / f"step_{step_index}_output.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            # Reduce only the dimension that exceeds target; the other scales automatically to preserve aspect
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
        """Convert video to a different container/codec format (mp4, webm, or mov)."""
        fmt = params["format"]  # required=true, validated by Gate 3
        vcodec, acodec, ext = self._TRANSCODE_CODEC_MAP[fmt]
        output_path = str(workspace / f"step_{step_index}_output.{ext}")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-c:v", vcodec,
            "-c:a", acodec,
            output_path,
        ]
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
        """Concatenate multiple video clips into one output using the FFmpeg concat filter."""
        job_id_str = str(job_id)
        clips = params["clips"]  # list of URLs; min 2, max 10 — validated by Gate 3
        n = len(clips)
        clip_paths: list[str] = []

        for i, clip_url in enumerate(clips):
            clip_url = clip_url.strip()
            try:
                if clip_url.startswith("uploads/"):
                    # R2 presigned GET — stream download asynchronously
                    ext = Path(clip_url).suffix.lstrip(".") or "mp4"
                    local_path = str(workspace / f"join_clip_{i}.{ext}")
                    presigned = await storage.generate_presigned_download_url(clip_url)
                    client = get_http_client(timeout=300.0)
                    async with client.stream("GET", presigned) as resp:
                        resp.raise_for_status()
                        with open(local_path, "wb") as f:
                            async for chunk in resp.aiter_bytes():
                                f.write(chunk)
                    await client.aclose()
                else:
                    # Platform URL — yt-dlp with custom output name to avoid collision
                    local_path = str(workspace / f"join_clip_{i}.mp4")
                    opts: dict = {
                        "outtmpl": str(workspace / f"join_clip_{i}.%(ext)s"),
                        "format": "bestvideo+bestaudio/best",
                        "quiet": True,
                        "no_warnings": True,
                        "merge_output_format": "mp4",
                    }
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self._download_clip_sync, clip_url, str(workspace), i, opts)

                clip_paths.append(local_path)
            except Exception as exc:
                logger.warning(
                    f"[{operation}] job={job_id_str} step={step_index} clip[{i}] download failed: {exc} | url={clip_url}"
                )
                logger.exception(
                    f"[{operation}] job={job_id_str} step={step_index} clip[{i}] download failed"
                )
                # Clean up any partial clip files
                for p in clip_paths:
                    with suppress(OSError):
                        os.remove(p)
                return ProcessResult(
                    success=False,
                    error=ProcessError(
                        code="download_failed",
                        summary=f"[join] Failed to download clip {i+1}/{n}: {exc}",
                        cause=f"Clip {i+1} at '{clip_url}' could not be downloaded.",
                        fix="Verify all clip URLs are accessible.",
                        raw_stderr=str(exc),
                    ),
                )

        # Build concat filter complex — re-encodes all clips to a common format
        filter_complex = (
            "".join(f"[{i}:v][{i}:a]" for i in range(n))
            + f"concat=n={n}:v=1:a=1[vout][aout]"
        )
        output_path = str(workspace / f"step_{step_index}_output.mp4")
        cmd = [
            "ffmpeg", "-y",
            *[["-i", p] for p in clip_paths],
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-c:a", "aac",
            output_path,
        ]
        result = await self._run_ffmpeg(cmd, operation, params, input_path, output_path, job_id, step_index)

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

    @staticmethod
    def _download_clip_sync(url: str, workspace_dir: str, index: int, opts: dict) -> None:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

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
            logger.error(
                f"FFmpeg exited 0 but output file missing — job={job_id_str}, step={step_index}, op={operation}, path={output_path}"
            )
            return ProcessResult(
                success=False,
                error=ProcessError(
                    code="missing_output",
                    summary=f"[{operation}] FFmpeg succeeded but produced no output file",
                    cause=f"Output path '{output_path}' does not exist after run",
                    fix="Inspect the FFmpeg command and the input file.",
                    raw_stderr=proc.stderr or "",
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