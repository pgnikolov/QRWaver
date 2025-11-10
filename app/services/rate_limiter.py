import time
from typing import Dict, Tuple
from flask import Request


class SimpleRateLimiter:
    """
    A simple rate limiter class used to limit the number of requests from a specific source within
    a given time window. Designed for scenarios where controlling request rates is necessary to
    prevent abuse or overload on a system.

    This rate limiter supports custom configuration for the maximum limit of requests and the time
    window in seconds over which the limit applies. It identifies request sources based on their IP
    address, either provided directly or through the "X-Forwarded-For" header when behind a proxy.

    :ivar limit: The maximum number of requests allowed within the time window.
    :type limit: int
    :ivar window: The duration of the time window in seconds during which the request count is measured.
    :type window: int
    """

    def __init__(self, limit: int = 3, window_seconds: int = 300):
        self.limit = limit
        self.window = window_seconds
        self._hits: Dict[str, Tuple[int, float]] = {}  # ip -> (count, window_start_epoch)

    def _key(self, req: Request) -> str:
        # Prefer X-Forwarded-For behind proxy; fallback to remote_addr
        forwarded = (req.headers.get("X-Forwarded-For") or "").split(",")[0].strip()
        return forwarded or (req.remote_addr or "unknown")

    def allow(self, req: Request) -> Tuple[bool, int]:
        """
        Returns (allowed?, remaining).
        """
        key = self._key(req)
        now = time.time()
        count, start = self._hits.get(key, (0, now))

        if now - start > self.window:
            # new window
            count, start = (0, now)

        if count >= self.limit:
            remaining = 0
            self._hits[key] = (count, start)
            return False, remaining

        count += 1
        remaining = max(0, self.limit - count)
        self._hits[key] = (count, start)
        return True, remaining
