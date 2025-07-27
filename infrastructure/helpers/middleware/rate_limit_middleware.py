"""
Rate Limiting Middleware

Simple in-memory rate limiting implementation with configurable limits per IP.
Provides protection against abuse and DoS attacks.
"""

import json
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from infrastructure.helpers.logger.logger_config import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware:
    """Simple in-memory rate limiting middleware"""

    def __init__(self, app, requests_per_second: int = 10, window_size: int = 60):
        self.app = app
        self.requests_per_second = requests_per_second
        self.window_size = window_size
        self.requests: Dict[str, Deque[float]] = defaultdict(lambda: deque())

    def _get_client_ip(self, environ) -> str:
        """Get client IP with fallbacks"""
        # Check for forwarded headers first
        forwarded_for = environ.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header
        real_ip = environ.get("HTTP_X_REAL_IP")
        if real_ip:
            return real_ip

        # Fallback to remote address
        return environ.get("REMOTE_ADDR") or "unknown"

    def _clean_old_requests(self, client_ip: str) -> None:
        """Remove requests older than window size"""
        current_time = time.time()
        client_requests = self.requests[client_ip]

        # Remove requests older than window_size
        while client_requests and current_time - client_requests[0] > self.window_size:
            client_requests.popleft()

    def _is_rate_limited(self, client_ip: str) -> Tuple[bool, Dict[str, int]]:
        """Check if client is rate limited"""
        current_time = time.time()
        client_requests = self.requests[client_ip]

        # Clean old requests
        self._clean_old_requests(client_ip)

        # Check if we're at the limit
        if len(client_requests) >= self.requests_per_second:
            return True, {
                "limit": self.requests_per_second,
                "remaining": 0,
                "reset_time": int(client_requests[0] + self.window_size),
            }

        # Add current request
        client_requests.append(current_time)

        return False, {
            "limit": self.requests_per_second,
            "remaining": self.requests_per_second - len(client_requests),
            "reset_time": int(current_time + self.window_size),
        }

    def __call__(self, environ, start_response):
        """WSGI middleware implementation"""

        # Get path info for endpoint checking
        path_info = environ.get("PATH_INFO", "")

        # Skip rate limiting for health checks
        if path_info in [
            "/api/health",
            "/api/health/detailed",
            "/api/version",
        ]:
            return self.app(environ, start_response)

        # Get client IP
        client_ip = self._get_client_ip(environ)
        is_limited, headers = self._is_rate_limited(client_ip)

        if is_limited:
            logger.warning(
                "rate_limit_exceeded",
                client_ip=client_ip,
                limit=self.requests_per_second,
            )

            # Create rate limit exceeded response
            status = "429 Too Many Requests"
            response_headers = [
                ("Content-Type", "application/json"),
                ("X-RateLimit-Limit", str(headers["limit"])),
                ("X-RateLimit-Remaining", str(headers["remaining"])),
                ("X-RateLimit-Reset", str(headers["reset_time"])),
            ]

            error_response = {
                "error": {
                    "type": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": headers["reset_time"] - int(time.time()),
                }
            }

            response_body = json.dumps(error_response).encode("utf-8")
            response_headers.append(("Content-Length", str(len(response_body))))

            start_response(status, response_headers)
            return [response_body]

        logger.debug(
            "rate_limit_check_passed",
            client_ip=client_ip,
            remaining=headers["remaining"],
        )

        # Store headers for later use in response
        environ["rate_limit_headers"] = headers

        # Process request normally
        return self.app(environ, start_response)
