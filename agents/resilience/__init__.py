"""
Resilience Patterns - v5.4 True Autonomous Agents

Patterns implemented:
- H1: Exception Handling (3P: Tenacity)

Graceful degradation for great student experience.
"""

from .exception_handling import (
    ExceptionHandler,
    AgentError,
    FallbackResponse,
    ErrorSeverity,
    ErrorCategory,
    with_retry,
    safe_execute,
    handle_exception,
    RETRY_CONFIGS,
    USER_MESSAGES,
    RECOVERY_HINTS,
)

__all__ = [
    "ExceptionHandler",
    "AgentError",
    "FallbackResponse",
    "ErrorSeverity",
    "ErrorCategory",
    "with_retry",
    "safe_execute",
    "handle_exception",
    "RETRY_CONFIGS",
    "USER_MESSAGES",
    "RECOVERY_HINTS",
]
