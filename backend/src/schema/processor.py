from pydantic import BaseModel

from src.schema.artifact import Artifact


class ProcessError(BaseModel):
    """Structured FFmpeg failure returned by the error summarization layer.

    Attributes:
        code: Stable error code (e.g. "file_not_found", "invalid_codec", "ffmpeg_error").
        summary: One-line human-readable description of what failed.
        cause: Likely cause of the failure, if determinable. None when unknown.
        fix: Suggested remediation for the developer/user. None when unknown.
        raw_stderr: The original FFmpeg stderr output, preserved for debugging.
    """
    code: str
    summary: str
    cause: str | None = None
    fix: str | None = None
    raw_stderr: str


class ProcessResult(BaseModel):
    """Outcome of a single FFmpeg operation execution.

    Exactly one of ``artifact`` (success) or ``error`` (failure) is populated.
    ``output_path`` is set on success and points to the produced file on disk.

    Attributes:
        success: Whether the operation completed without error.
        output_path: Absolute path to the output file on disk. None on failure.
        artifact: Built ``Artifact`` for the output file. None on failure.
        error: Structured error when ``success`` is False. None on success.
    """
    success: bool
    output_path: str | None = None
    artifact: Artifact | None = None
    error: ProcessError | None = None