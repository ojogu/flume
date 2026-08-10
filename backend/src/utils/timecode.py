"""Timecode parsing utilities for human-readable time inputs.

Supports three time formats:
  - HH:MM:SS.SSS  (e.g., "01:30:05.500")
  - MM:SS.SSS     (e.g., "1:30:05.500" or "90:05.500")
  - Bare seconds   (e.g., "3605.5")

All formats are parsed to a float representing total seconds.
"""

from __future__ import annotations


def parse_timecode(value: str) -> float:
    """Parse a timecode string to total seconds as a float.

    Accepted formats:
      - "HH:MM:SS.SSS"  — hours, minutes, seconds with optional milliseconds
      - "MM:SS.SSS" — minutes and seconds with optional milliseconds
      - "SS.SSS" — bare seconds (int or float); returned as-is

    MM:SS is disambiguated from HH:MM:SS by the number of colons:
      - 2 colons  → HH:MM:SS
      - 1 colon   → MM:SS

    Args:
        value: A timecode string (e.g., "1:30:05.500", "90:05.500", "3605.5")

    Returns:
        Total seconds as a float. Milliseconds are supported (e.g., "1:00.500" → 60.5).

    Raises:
        ValueError: If the string cannot be parsed as a valid timecode.
    """
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")

    value = value.strip()
    if not value:
        raise ValueError("Empty timecode string")

    parts = value.split(":")
    total_seconds: float

    if len(parts) == 3:
        # HH:MM:SS.SSS
        try:
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
        except ValueError as e:
            raise ValueError(f"Invalid numeric component in HH:MM:SS timecode '{value}'") from e

        if hours < 0 or minutes < 0 or seconds < 0:
            raise ValueError(f"Negative components not allowed in timecode '{value}'")
        if minutes >= 60:
            raise ValueError(f"Minutes component ({minutes}) exceeds 59 in timecode '{value}'")

        total_seconds = hours * 3600 + minutes * 60 + seconds

    elif len(parts) == 2:
        # MM:SS.SSS
        try:
            minutes = float(parts[0])
            seconds = float(parts[1])
        except ValueError as e:
            raise ValueError(f"Invalid numeric component in MM:SS timecode '{value}'") from e

        if minutes < 0 or seconds < 0:
            raise ValueError(f"Negative components not allowed in timecode '{value}'")

        total_seconds = minutes * 60 + seconds

    elif len(parts) == 1:
        # Bare seconds
        try:
            total_seconds = float(parts[0])
        except ValueError as e:
            raise ValueError(f"Invalid bare seconds value '{value}'") from e

        if total_seconds < 0:
            raise ValueError(f"Negative seconds not allowed in timecode '{value}'")

    else:
        raise ValueError(f"Too many colons in timecode '{value}'")

    return total_seconds
