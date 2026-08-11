import os

import litellm

from src.utils.config import config
from src.utils.log import get_logger

logger = get_logger(__name__)

ERROR_SUMMARY_PROMPT = """You are an expert FFmpeg troubleshooting assistant. Given an FFmpeg operation that failed, explain what went wrong in plain English with a specific cause and a suggested fix.

Respond using ONLY this JSON structure (no extra text):
{{"code": "a_short_error_code_like_snake_case", "summary": "one line human readable description", "cause": "likely root cause", "fix": "suggested remediation"}}

FFmpeg operation that failed: {operation}
Parameters: {params}
Last 20 lines of FFmpeg stderr:
{stderr_lines}

Only respond with the JSON object, no markdown formatting or explanation."""


async def summarize_with_llm(
    operation: str,
    params: dict,
    stderr: str,
) -> str:
    """Call the LLM to explain an FFmpeg failure. Raises on error — caller falls through to heuristic."""
    stderr_lines = "\n".join(stderr.strip().splitlines()[-20:])
    prompt = ERROR_SUMMARY_PROMPT.format(
        operation=operation,
        params=params,
        stderr_lines=stderr_lines,
    )

    logger.info(f"Calling LiteLLM for error summarization: model={config.model}, operation={operation}")

    response = await litellm.acompletion(
        model=config.model,
        api_base=config.api_base,
        api_key=config.api_key,
        messages=[{"role": "user", "content": prompt}],
         timeout=45.0,
    )

    content = response.choices[0].message.content
    logger.debug(f"LLM response: {content}")
    return content
