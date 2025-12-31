"""
Audit Logging Middleware
Comprehensive audit logging for all API requests.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import structlog
import time
import uuid
import json

from app.core.logging import audit_logger

logger = structlog.get_logger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for audit logging of all API requests and responses.
    """
    
    SENSITIVE_HEADERS = [
        "authorization",
        "cookie",
        "x-api-key"
    ]
    
    EXEMPT_PATHS = [
        "/health",
        "/health/ready",
        "/health/live"
    ]
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response for audit trail."""
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Skip audit for health checks
        if request.url.path in self.EXEMPT_PATHS:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        
        # Capture request details
        start_time = time.time()
        
        request_details = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "headers": self._sanitize_headers(dict(request.headers))
        }
        
        # Extract user from token if present
        user_id = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.core.security import JWTService
                token = auth_header.split(" ")[1]
                payload = JWTService.decode_token(token)
                user_id = payload.get("sub")
                request_details["user_id"] = user_id
            except Exception:
                pass
        
        # Read and cache request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                request_details["body_size"] = len(body)
                
                # Try to parse and sanitize JSON body
                if body:
                    try:
                        body_json = json.loads(body)
                        request_details["body"] = self._sanitize_body(body_json)
                    except json.JSONDecodeError:
                        request_details["body"] = "non-json"
            except Exception:
                pass
        
        logger.info("API request", **request_details)
        
        # Process request
        try:
            # Restore body for route handlers
            if body is not None:
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
            
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            response_details = {
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2)
            }
            
            if user_id:
                response_details["user_id"] = user_id
            
            # Determine log level based on status code
            if response.status_code < 400:
                logger.info("API response", **response_details)
            elif response.status_code < 500:
                logger.warning("API response (client error)", **response_details)
            else:
                logger.error("API response (server error)", **response_details)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(
                "API request failed",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2),
                exc_info=True
            )
            
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _sanitize_headers(self, headers: dict) -> dict:
        """Remove sensitive information from headers."""
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in self.SENSITIVE_HEADERS:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        return sanitized
    
    def _sanitize_body(self, body: dict) -> dict:
        """Remove sensitive information from request body."""
        sensitive_fields = [
            "password", "token", "secret", "key",
            "credit_card", "cvv", "pin", "otp",
            "access_token", "refresh_token"
        ]
        
        sanitized = {}
        for key, value in body.items():
            if any(field in key.lower() for field in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_body(value)
            else:
                sanitized[key] = value
        
        return sanitized
