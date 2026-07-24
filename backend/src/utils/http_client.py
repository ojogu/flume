"""HTTP client factory for outbound requests.

Centralizes httpx.AsyncClient configuration (timeouts, connection pool limits)
so callers don't repeat boilerplate. Each call returns a fresh client — callers
manage lifecycle via ``async with``.

Note: httpx.AsyncClient is bound to the event loop it was created on, so we
cannot use a singleton across Celery workers (each task gets its own event loop).
"""

import httpx

DEFAULT_TIMEOUT = 30.0
DEFAULT_LIMITS = httpx.Limits(max_connections=60, max_keepalive_connections=20)


def get_http_client(timeout: float = DEFAULT_TIMEOUT) -> httpx.AsyncClient:
    """Return a configured AsyncClient with standardised pool and timeout settings.

    Args:
        timeout: Request timeout in seconds. Use ``httpx.Timeout(None)`` to disable.

    Returns:
        An ``httpx.AsyncClient`` instance. Caller must close via ``async with``.
    """
    return httpx.AsyncClient(timeout=timeout, limits=DEFAULT_LIMITS)
