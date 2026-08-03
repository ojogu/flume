# ── FFmpeg error summarization ──────────────────────────────────────────────
# Two-layer error explanation:
#   1. LLM summarizer (primary) — uses LiteLLM to phrase failures in plain English with cause and remediation. Added in Phase 2.
#   2. Heuristic parser (fallback) — recognizes common FFmpeg stderr patterns when the LLM is unavailable or its request fails.

# Phase 1 ships the heuristic layer only; the LLM call site is marked below so Phase 2 can wire it in without reshaping the contract.

from src.schema.processor import ProcessError
from src.utils.log import get_logger

logger = get_logger(__name__)


async def summarize_ffmpeg_error(
    operation: str,
    params: dict,
    input_path: str,
    output_path: str,
    stderr: str,
) -> ProcessError:
    """Summarize an FFmpeg failure into a structured ``ProcessError``.

    Args:
        operation: Operation name (e.g. "trim", "compress").
        params: Operation params from the pipeline spec.
        input_path: Absolute path to the input file passed to FFmpeg.
        output_path: Absolute path to the intended output file.
        stderr: Raw FFmpeg stderr output.

    Returns:
        ``ProcessError`` with code, summary, cause/fix when determinable, and the raw stderr preserved.
    """
    # Phase 2: try LLM summarization first. On any exception or empty
    # response, fall through to the heuristic parser. For now the LLM
    # path is a no-op and we go straight to heuristics.
    return _heuristic_parse(operation, params, input_path, output_path, stderr)


# ── Known FFmpeg error patterns ─────────────────────────────────────────────
# Ordered by frequency. The first match wins; each entry maps a substring of
# stderr to a stable error code + human summary + remediation hint.
_KNOWN_PATTERNS: list[tuple[str, str, str, str | None]] = [
    (
        "No such file or directory",
        "file_not_found",
        "Input file could not be found on disk.",
        "Verify the source URI resolved to a real file in the job workspace.",
    ),
    (
        "Invalid data found when processing input",
        "invalid_data",
        "FFmpeg could not read the input file — it is missing, empty, or corrupted.",
        "Re-download the source and check the file is complete before retrying.",
    ),
    (
        "Unknown decoder",
        "unknown_decoder",
        "The requested decoder is not available in this FFmpeg build.",
        "Install or rebuild FFmpeg with the required codec support.",
    ),
    (
        "Unknown encoder",
        "unknown_encoder",
        "The requested encoder is not available in this FFmpeg build.",
        "Install or rebuild FFmpeg with the required codec support.",
    ),
    (
        "Option not found",
        "invalid_option",
        "An FFmpeg option used by this operation is not recognized.",
        "Check the FFmpeg command flags against this build's supported options.",
    ),
    (
        "Could not find tag for codec",
        "unsupported_codec",
        "The requested codec is not supported in the chosen output container.",
        "Choose a container/format compatible with the requested codec.",
    ),
    (
        "Permission denied",
        "permission_denied",
        "FFmpeg could not write to the output path.",
        "Check that the workspace directory is writable by the worker process.",
    ),
    (
        "Disk full",
        "disk_full",
        "FFmpeg ran out of disk space while writing output.",
        "Free space on the workspace volume or reduce the output size.",
    ),
]


def _heuristic_parse(
    operation: str,
    params: dict,
    input_path: str,
    output_path: str,
    stderr: str,
) -> ProcessError:
    """Recognize common FFmpeg error patterns from stderr.

    Returns a generic ``ffmpeg_error`` with the last meaningful stderr line when no known pattern matches.
    """
    for needle, code, summary, fix in _KNOWN_PATTERNS:
        if needle in stderr:
            logger.info(
                f"FFmpeg error matched heuristic pattern '{code}' for operation '{operation}'"
            )
            return ProcessError(
                code=code,
                summary=f"[{operation}] {summary}",
                cause=f"FFmpeg stderr contained: '{needle}'",
                fix=fix,
                raw_stderr=stderr,
            )

    # No known pattern — best effort: surface the last non-empty stderr line
    last_line = ""
    for line in reversed(stderr.splitlines()):
        stripped = line.strip()
        if stripped:
            last_line = stripped
            break

    logger.warning(
        f"FFmpeg error for operation '{operation}' did not match any known pattern"
    )
    return ProcessError(
        code="ffmpeg_error",
        summary=f"[{operation}] FFmpeg failed: {last_line or 'unknown error'}",
        cause=None,
        fix=None,
        raw_stderr=stderr,
    )