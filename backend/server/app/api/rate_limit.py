import threading
import time
from collections import defaultdict, deque

from fastapi import Request

from app.api.errors import ApiError


class RateLimiter:
    """A simple per-IP sliding-window rate limiter usable as a FastAPI dependency.

    Each instance keeps its own counters, so different endpoints get independent
    budgets, e.g. ``Depends(RateLimiter(5, 60))`` allows 5 requests per minute.
    """

    def __init__(self, limit: int, window: float, scope: str = ""):
        self.limit = limit
        self.window = window
        self.scope = scope
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def __call__(self, request: Request) -> None:
        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        with self._lock:
            bucket = self._hits[ip]
            cutoff = now - self.window
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.limit:
                retry = int(self.window - (now - bucket[0])) + 1
                raise ApiError(
                    f"Too many requests — try again in {retry}s.", status_code=429
                )
            bucket.append(now)


# Shared limiters for the auth surface (brute-force protection).
login_limiter = RateLimiter(limit=10, window=60, scope="login")
register_limiter = RateLimiter(limit=5, window=60, scope="register")
code_limiter = RateLimiter(limit=10, window=60, scope="code")
scan_limiter = RateLimiter(limit=20, window=60, scope="scan")
