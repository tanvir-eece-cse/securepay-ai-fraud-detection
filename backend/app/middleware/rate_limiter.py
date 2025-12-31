"""
Rate Limiting Middleware
Redis-based rate limiting for API endpoints.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
import structlog

from app.core.config import settings
from app.core.redis import rate_limiter

logger = structlog.get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests based on IP address.
    Uses Redis sliding window algorithm.
    """
    
    EXEMPT_PATHS = [
        "/health",
        "/health/ready",
        "/health/live",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    
    async def dispatch(self, request: Request, call_next):
        """Process rate limiting for each request."""
        
        # Skip rate limiting for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)
        
        # Check per-minute rate limit
        is_allowed_minute, remaining_minute = await rate_limiter.is_allowed(
            f"minute:{client_ip}",
            settings.RATE_LIMIT_PER_MINUTE,
            60
        )
        
        if not is_allowed_minute:
            logger.warning(
                "Rate limit exceeded (per minute)",
                client_ip=client_ip,
                path=request.url.path
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                },
                headers={
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "60",
                    "Retry-After": "60"
                }
            )
        
        # Check per-hour rate limit
        is_allowed_hour, remaining_hour = await rate_limiter.is_allowed(
            f"hour:{client_ip}",
            settings.RATE_LIMIT_PER_HOUR,
            3600
        )
        
        if not is_allowed_hour:
            logger.warning(
                "Rate limit exceeded (per hour)",
                client_ip=client_ip,
                path=request.url.path
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Hourly rate limit exceeded. Please try again later.",
                    "retry_after": 3600
                },
                headers={
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_HOUR),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "3600",
                    "Retry-After": "3600"
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining-Minute"] = str(remaining_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(settings.RATE_LIMIT_PER_HOUR)
        response.headers["X-RateLimit-Remaining-Hour"] = str(remaining_hour)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        if request.client:
            return request.client.host
        
        return "unknown"
