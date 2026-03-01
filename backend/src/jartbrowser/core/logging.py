"""
Logging configuration for production
"""

import logging
import sys
from typing import Any, Dict

import structlog


def configure_logging(
    log_level: str = "INFO",
    environment: str = "development",
    json_logs: bool = False,
) -> None:
    """Configure structured logging for the application"""

    # Determine if we should use JSON logging
    use_json = json_logs or environment == "production"

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if use_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging capability to any class"""

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__module__ + "." + self.__class__.__name__)
        return self._logger


def log_request(
    logger: structlog.stdlib.BoundLogger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    extra: Dict[str, Any] = None,
) -> None:
    """Log an HTTP request"""
    logger.info(
        "http_request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        **(extra or {}),
    )


def log_error(
    logger: structlog.stdlib.BoundLogger,
    error: Exception,
    context: Dict[str, Any] = None,
) -> None:
    """Log an error with context"""
    logger.error(
        "error_occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        **(context or {}),
    )


def log_user_action(
    logger: structlog.stdlib.BoundLogger,
    user_id: str,
    action: str,
    metadata: Dict[str, Any] = None,
) -> None:
    """Log a user action for analytics"""
    logger.info(
        "user_action",
        user_id=user_id,
        action=action,
        **(metadata or {}),
    )
