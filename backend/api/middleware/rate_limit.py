"""
backend/api/middleware/rate_limit.py
Simple in-memory sliding-window rate limiter for auth + stream endpoints.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_lock = Lock()
_buckets: dict[str, deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _allow(key: str, limit: int, window_s: float = 60.0) -> bool:
    now = time.monotonic()
    with _lock:
        q = _buckets[key]
        while q and now - q[0] > window_s:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(now)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method.upper()
        ip = _client_ip(request)

        limit = None
        if method == "POST" and path.endswith("/api/v1/auth/login"):
            limit = settings.rate_limit_login_per_minute
            bucket = f"login:{ip}"
        elif method == "POST" and path.endswith("/api/v1/chat/stream"):
            limit = settings.rate_limit_stream_per_minute
            bucket = f"chat:{ip}"
        elif method == "POST" and path.endswith("/api/v1/institution/assistant/stream"):
            limit = settings.rate_limit_stream_per_minute
            bucket = f"inst-assist:{ip}"
        else:
            return await call_next(request)

        if limit is not None and not _allow(bucket, limit):
            logger.warning(
                "rate_limit_exceeded path=%s ip=%s limit=%s",
                path,
                ip,
                limit,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Çok fazla istek. Biraz sonra tekrar dene.",
                        "details": None,
                    },
                    "meta": {},
                },
            )
        return await call_next(request)
