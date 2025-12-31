"""
Structured Logging Configuration
Production-ready logging with JSON formatting and correlation IDs.
"""

import logging
import sys
from typing import Any, Dict
import structlog
from structlog.types import EventDict, WrappedLogger

from app.core.config import settings


def add_app_context(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict
) -> EventDict:
    """Add application context to log events."""
    event_dict["service"] = "securepay-ai-backend"
    event_dict["version"] = settings.VERSION
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def censor_sensitive_data(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict
) -> EventDict:
    """Censor sensitive data from logs."""
    sensitive_keys = [
        "password", "token", "secret", "key", "authorization",
        "credit_card", "card_number", "cvv", "pin", "otp"
    ]
    
    def censor_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for k, v in d.items():
            if any(sensitive in k.lower() for sensitive in sensitive_keys):
                result[k] = "***CENSORED***"
            elif isinstance(v, dict):
                result[k] = censor_dict(v)
            else:
                result[k] = v
        return result
    
    return censor_dict(event_dict)


def setup_logging() -> None:
    """Configure structured logging for the application."""
    
    # Determine log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Shared processors for all loggers
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_app_context,
        censor_sensitive_data,
        structlog.processors.StackInfoRenderer(),
    ]
    
    if settings.DEBUG:
        # Development: Pretty printing
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Production: JSON formatting
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


class RequestLogger:
    """
    Utility class for logging HTTP requests with context.
    """
    
    def __init__(self, request_id: str):
        self.logger = structlog.get_logger()
        self.request_id = request_id
    
    def log_request(
        self,
        method: str,
        path: str,
        client_ip: str,
        user_id: str = None
    ) -> None:
        """Log incoming request."""
        self.logger.info(
            "Request received",
            request_id=self.request_id,
            method=method,
            path=path,
            client_ip=client_ip,
            user_id=user_id
        )
    
    def log_response(
        self,
        status_code: int,
        duration_ms: float
    ) -> None:
        """Log response sent."""
        log_level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
        
        getattr(self.logger, log_level)(
            "Response sent",
            request_id=self.request_id,
            status_code=status_code,
            duration_ms=round(duration_ms, 2)
        )
    
    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any] = None
    ) -> None:
        """Log error with context."""
        self.logger.error(
            "Error occurred",
            request_id=self.request_id,
            error=str(error),
            error_type=type(error).__name__,
            context=context or {},
            exc_info=True
        )


class AuditLogger:
    """
    Audit logger for security-relevant events.
    """
    
    def __init__(self):
        self.logger = structlog.get_logger("audit")
    
    def log_authentication(
        self,
        user_id: str,
        success: bool,
        method: str,
        ip_address: str,
        user_agent: str = None,
        reason: str = None
    ) -> None:
        """Log authentication attempt."""
        self.logger.info(
            "authentication_attempt",
            event_type="authentication",
            user_id=user_id,
            success=success,
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            reason=reason
        )
    
    def log_authorization(
        self,
        user_id: str,
        resource: str,
        action: str,
        allowed: bool,
        reason: str = None
    ) -> None:
        """Log authorization decision."""
        self.logger.info(
            "authorization_check",
            event_type="authorization",
            user_id=user_id,
            resource=resource,
            action=action,
            allowed=allowed,
            reason=reason
        )
    
    def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        fields_accessed: list = None
    ) -> None:
        """Log data access for compliance."""
        self.logger.info(
            "data_access",
            event_type="data_access",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            fields_accessed=fields_accessed or []
        )
    
    def log_transaction(
        self,
        transaction_id: str,
        user_id: str,
        action: str,
        amount: float = None,
        currency: str = None,
        risk_score: float = None,
        decision: str = None
    ) -> None:
        """Log transaction for audit trail."""
        self.logger.info(
            "transaction_event",
            event_type="transaction",
            transaction_id=transaction_id,
            user_id=user_id,
            action=action,
            amount=amount,
            currency=currency,
            risk_score=risk_score,
            decision=decision
        )
    
    def log_security_event(
        self,
        event_name: str,
        severity: str,
        user_id: str = None,
        details: Dict[str, Any] = None
    ) -> None:
        """Log security-relevant event."""
        log_method = self.logger.warning if severity in ["medium", "high"] else self.logger.info
        log_method(
            "security_event",
            event_type="security",
            event_name=event_name,
            severity=severity,
            user_id=user_id,
            details=details or {}
        )


# Global audit logger instance
audit_logger = AuditLogger()
