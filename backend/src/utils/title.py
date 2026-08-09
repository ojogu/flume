import re


def sanitize_title_for_filename(title: str | None) -> str:
    if not title:
        return ""

    sanitized = title.lower()

    sanitized = re.sub(r"[^a-z0-9\s\-]", "", sanitized)

    sanitized = re.sub(r"[\s\-]+", "-", sanitized)

    sanitized = sanitized.strip("-")

    if len(sanitized) > 100:
        sanitized = sanitized[:100].rstrip("-")

    return sanitized
