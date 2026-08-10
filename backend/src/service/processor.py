# ── FFmpeg operation execution layer ─────────────────────────────────────────
# Responsibilities:
#   1. Build FFmpeg command lists per operation (trim, cut, compress, ...)
#   2. Run FFmpeg via subprocess and capture stdout/stderr
#   3. On failure, route stderr to the LLM error summarizer
#   4. On success, build an ``Artifact`` describing the output file

# Class-based service mirroring ``JobService``/``EventService``: constructed with an ``AsyncSession`` so it can be wired through the same dependency injection paths and share the DB transaction with its caller.

# Runs inside Celery workers (sync execution context). The async methods below are driven by ``run_async_in_sync`` exactly like the download task.

from __future__ import annotations

import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar

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

logger = get_logger(__name__)


class ProcessorService:
    """FFmpeg execution service.

    Each operation is a private method that builds the FFmpeg command list, invokes ``_run_ffmpeg``, and (on success) attaches an ``Artifact`` built from the output file. ``execute_operation`` is the single public entry point used by the ``jobs.media.execute`` Celery task.

    Args:
        db: Async SQLAlchemy session. Currently unused by FFmpeg execution itself but kept for symmetry with the other services so the same injection pattern applies and future DB-touching helpers (e.g. ffprobe enrichment) can land without a constructor change.
    """

    # ── Handler registry ──────────────────────────────────
    # Maps operation name → bound method name. Kept at the top of the class so the supported operations read as a table of contents; new operations (Phase 3+) plug in by adding a method + an entry here. Method names are strings (not direct references) because the class body can't forward-reference methods defined below — resolution happens at call time via getattr.
    
    
    _HANDLERS: ClassVar[dict[str, str]] = {
        "trim": "_trim",
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
        """Dispatch to the per-operation handler.

        Args:
            job_id: Owning job UUID. Used to build artifact identifiers.
            step_index: Zero-based step index for this operation. Used to name the output file uniquely within the workspace.
            operation: Operation name from ``pipeline_steps`` (e.g. "trim").
            params: Operation params from ``pipeline_steps``.
            input_path: Absolute path to the input file (previous step's output or, for step_index 0, the downloaded file).
            workspace: Absolute path to the job's isolated workspace.

        Returns:
            ``ProcessResult`` with either a built ``Artifact`` (success) or a
            structured ``ProcessError`` (failure).
        """
        handler_name = self._HANDLERS.get(operation)
        if handler_name is None:
            logger.error(f"No handler registered for operation '{operation}' — job={job_id}, step={step_index}")
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
            f"Executing operation '{operation}' for job {job_id} step {step_index} "
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
        """Clip a segment from the input between ``start`` and ``end``.

        Re-encodes to H.264 video + AAC audio so the cut is frame-accurate regardless of keyframe boundaries. Output container is mp4.

        `start` and `end` are pre-validated and normalized as floats by Gate 3 (validate_params) — no parsing or type coercion needed here.
        """
        start = params["start"]
        end = params["end"]

        if end <= start:
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
        """Execute an FFmpeg command list and capture the result.

        Returns a ProcessResult:
          success → `output_path` populated, no artifact (caller attaches).
          failure → `error` populated via the LLM summarizer.
        """
        logger.debug(f"FFmpeg cmd: {' '.join(cmd)}")
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            logger.error(f"ffmpeg binary not found on PATH — job={job_id}, step={step_index}, op={operation}")
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
                f"FFmpeg failed — job={job_id}, step={step_index}, op={operation}, exit={proc.returncode}"
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
                f"FFmpeg exited 0 but output file missing — job={job_id}, step={step_index}, op={operation}, path={output_path}"
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
        """Build an ``Artifact`` for an operation's output file.

        ``SourceInfo`` is pipeline-flavored: platform="pipeline" signals that this artifact was derived by FFmpeg, not downloaded. Media info is populated by probing the output file with ffprobe so the Artifact accurately reflects
        the media on disk.
        """
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