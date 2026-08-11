# ── FFmpeg error summarization ──────────────────────────────────────────────
# Two-layer error explanation:
#   1. LLM summarizer (primary) — uses LiteLLM to phrase failures in plain English with cause and remediation. Added in Phase 2.
#   2. Heuristic parser (fallback) — recognizes common FFmpeg stderr patterns when the LLM is unavailable or its request fails.


from src.schema.processor import ProcessError
from src.service.llm import summarize_with_llm
from src.utils.log import get_logger
from src.utils.redis import get_redis_sync
import hashlib
import re
import json

logger = get_logger(__name__)

LLM_ERROR_CACHE_TTL = 3600

# Keyed on sha256(operation + stderr[:500]) — identical failures produce identical keys.
def _build_cache_key(operation: str, stderr: str) -> str:
    sig = f"{operation}:{stderr[:500]}".encode()
    return f"llm_error:{hashlib.sha256(sig).hexdigest()}"


async def _parse_llm_response(raw: str) -> ProcessError | None:
    text = raw.strip()

    code = summary = cause = fix = None

    m = re.search(r'"code"\s*:\s*"([^"]+)"', text)
    if m:
        code = m.group(1)
    m = re.search(r'"summary"\s*:\s*"([^"]+)"', text)
    if m:
        summary = m.group(1)
    m = re.search(r'"cause"\s*:\s*"([^"]*)"', text)
    if m:
        cause = m.group(1) or None
    m = re.search(r'"fix"\s*:\s*"([^"]*)"', text)
    if m:
        fix = m.group(1) or None

    if code and summary:
        return ProcessError(
            code=code,
            summary=summary,
            cause=cause,
            fix=fix,
            raw_stderr="",
        )

    return None


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
    # Cache LLM responses for 1hr to avoid repeated API calls for the same error.
    cache_key = _build_cache_key(operation, stderr)

    try:
        redis = get_redis_sync()
        cached = redis.get(cache_key)
        if cached:
            logger.info(f"LLM error cache hit for operation '{operation}'")
            data = json.loads(cached)
            return ProcessError(raw_stderr=stderr, **data)
    except Exception as exc:
        logger.warning(f"Redis cache read failed for key {cache_key}: {exc}")

    raw_response = None
    try:
        raw_response = await summarize_with_llm(operation, params, stderr)
        parsed = await _parse_llm_response(raw_response)
        if parsed:
            try:
                redis = get_redis_sync()
                redis.setex(
                    cache_key,
                    LLM_ERROR_CACHE_TTL,
                    json.dumps({"code": parsed.code, "summary": parsed.summary, "cause": parsed.cause, "fix": parsed.fix}),
                )
                logger.info(f"Cached LLM error summary for operation '{operation}'")
            except Exception as exc:
                logger.warning(f"Redis cache write failed for key {cache_key}: {exc}")

            parsed.raw_stderr = stderr
            return parsed
        logger.warning(f"LLM response did not parse into ProcessError fields: {raw_response}")
    except Exception as exc:
        logger.warning(f"LLM summarization failed for operation '{operation}': {exc}")

    return _heuristic_parse(operation, params, input_path, output_path, stderr)


# ── Known FFmpeg error patterns ─────────────────────────────────────────────
# Ordered by frequency. The first match wins; each entry maps a substring of stderr to a stable error code + human summary + remediation hint.
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