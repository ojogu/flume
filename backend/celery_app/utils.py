# Celery tasks run synchronously, but our service layer uses async packages.
# This helper runs an async coroutine in a dedicated thread with its own event loop,
# preventing event-loop conflicts with FastAPI's async context.

import asyncio
import concurrent
def run_async_in_sync(coro):
    """
    Helper function to run async code in sync Celery tasks
    Creates a fresh event loop in a separate thread to avoid conflicts.
    """

    def _run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_in_thread)
        return future.result()
