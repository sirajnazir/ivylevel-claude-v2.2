"""
Pattern H1: Exception Handling
v5.4 True Autonomous Agents

3P: Tenacity for retries
USP: Graceful degradation for student experience
"""

from typing import Dict, Any, List, Optional, Callable, TypeVar, Type
from datetime import datetime
from functools import wraps
from enum import Enum
import logging
import traceback

# Import tenacity for retry logic
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        stop_after_delay,
        wait_exponential,
        wait_random,
        retry_if_exception_type,
        before_sleep_log,
        after_log,
        RetryError,
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    logging.warning("tenacity not installed, using fallback retry logic")

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""
    LOW = "low"           # Minor issue, continue normally
    MEDIUM = "medium"     # Issue requires attention
    HIGH = "high"         # Significant problem
    CRITICAL = "critical" # System failure


class ErrorCategory(str, Enum):
    """Categories of errors."""
    API = "api"               # External API errors
    DATABASE = "database"     # Database errors
    VALIDATION = "validation" # Validation errors
    TIMEOUT = "timeout"       # Timeout errors
    RATE_LIMIT = "rate_limit" # Rate limiting
    AUTH = "auth"            # Authentication errors
    UNKNOWN = "unknown"      # Unknown errors


class AgentError(BaseModel):
    """Structured error information."""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    agent_name: str
    profile_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    stack_trace: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retryable: bool = True
    recovery_hint: Optional[str] = None


class FallbackResponse(BaseModel):
    """Fallback response when errors occur."""
    success: bool = False
    error: Optional[AgentError] = None
    fallback_data: Dict[str, Any] = Field(default_factory=dict)
    user_message: str = "We encountered an issue. Please try again."


# Retry configurations by error category
RETRY_CONFIGS = {
    ErrorCategory.API: {
        "max_attempts": 3,
        "wait_min": 1,
        "wait_max": 10,
        "exponential_base": 2,
    },
    ErrorCategory.DATABASE: {
        "max_attempts": 2,
        "wait_min": 0.5,
        "wait_max": 5,
        "exponential_base": 2,
    },
    ErrorCategory.TIMEOUT: {
        "max_attempts": 2,
        "wait_min": 2,
        "wait_max": 10,
        "exponential_base": 2,
    },
    ErrorCategory.RATE_LIMIT: {
        "max_attempts": 3,
        "wait_min": 5,
        "wait_max": 60,
        "exponential_base": 3,
    },
}

# User-friendly error messages (USP: student-appropriate)
USER_MESSAGES = {
    ErrorCategory.API: "We're having trouble connecting to our services. Please try again in a moment.",
    ErrorCategory.DATABASE: "We couldn't load your data right now. Please refresh and try again.",
    ErrorCategory.TIMEOUT: "This is taking longer than expected. Please try again.",
    ErrorCategory.RATE_LIMIT: "You're sending requests too quickly. Please wait a moment.",
    ErrorCategory.AUTH: "There's an issue with your session. Please log in again.",
    ErrorCategory.VALIDATION: "There was an issue with the information provided. Please check and try again.",
    ErrorCategory.UNKNOWN: "Something unexpected happened. We're looking into it.",
}

# Recovery hints by category
RECOVERY_HINTS = {
    ErrorCategory.API: "Check API key and endpoint configuration",
    ErrorCategory.DATABASE: "Verify database connection and query",
    ErrorCategory.TIMEOUT: "Consider increasing timeout or optimizing query",
    ErrorCategory.RATE_LIMIT: "Implement request throttling",
    ErrorCategory.AUTH: "Refresh authentication tokens",
    ErrorCategory.VALIDATION: "Review input data format and requirements",
}


class ExceptionHandler:
    """
    Centralized exception handling for agents.

    Pattern H1: Exception Handling (3P: Tenacity)

    Key principles:
    1. Never crash silently
    2. Always provide user-friendly feedback
    3. Retry transient failures
    4. Log everything for debugging
    5. Graceful degradation when possible
    """

    def __init__(self):
        self._errors: List[AgentError] = []
        self._error_handlers: Dict[ErrorCategory, Callable] = {}

    def categorize_exception(self, exc: Exception) -> ErrorCategory:
        """
        Categorize an exception.

        Args:
            exc: The exception

        Returns:
            ErrorCategory
        """
        exc_type = type(exc).__name__
        exc_str = str(exc).lower()

        # API errors
        if any(t in exc_type for t in ["HTTP", "API", "Request", "Connection"]):
            return ErrorCategory.API

        # Database errors
        if any(t in exc_type for t in ["Database", "SQL", "Postgres", "Supabase"]):
            return ErrorCategory.DATABASE

        # Timeout errors
        if "timeout" in exc_type.lower() or "timeout" in exc_str:
            return ErrorCategory.TIMEOUT

        # Rate limit errors
        if any(t in exc_str for t in ["rate limit", "too many requests", "429"]):
            return ErrorCategory.RATE_LIMIT

        # Auth errors
        if any(t in exc_str for t in ["unauthorized", "forbidden", "401", "403"]):
            return ErrorCategory.AUTH

        # Validation errors
        if any(t in exc_type for t in ["Validation", "Value", "Type"]):
            return ErrorCategory.VALIDATION

        return ErrorCategory.UNKNOWN

    def determine_severity(
        self,
        category: ErrorCategory,
        retry_count: int = 0,
    ) -> ErrorSeverity:
        """Determine error severity."""
        if category == ErrorCategory.AUTH:
            return ErrorSeverity.HIGH

        if retry_count >= 3:
            return ErrorSeverity.HIGH

        if category in [ErrorCategory.DATABASE, ErrorCategory.API]:
            return ErrorSeverity.MEDIUM

        return ErrorSeverity.LOW

    def create_error(
        self,
        exc: Exception,
        agent_name: str,
        profile_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> AgentError:
        """
        Create structured error from exception.

        Args:
            exc: The exception
            agent_name: Name of the agent
            profile_id: Student's profile ID
            context: Additional context
            retry_count: Number of retries attempted

        Returns:
            AgentError
        """
        import uuid

        category = self.categorize_exception(exc)
        severity = self.determine_severity(category, retry_count)

        error = AgentError(
            error_id=str(uuid.uuid4()),
            category=category,
            severity=severity,
            message=str(exc),
            agent_name=agent_name,
            profile_id=profile_id,
            context=context or {},
            stack_trace=traceback.format_exc(),
            retryable=category in [
                ErrorCategory.API,
                ErrorCategory.DATABASE,
                ErrorCategory.TIMEOUT,
                ErrorCategory.RATE_LIMIT,
            ],
            recovery_hint=RECOVERY_HINTS.get(category),
        )

        self._errors.append(error)
        self._log_error(error)

        return error

    def _log_error(self, error: AgentError) -> None:
        """Log error with appropriate level."""
        log_msg = (
            f"[{error.category.value}] {error.agent_name}: {error.message} "
            f"(Profile: {error.profile_id}, ID: {error.error_id})"
        )

        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_msg)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_msg)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

    def get_user_message(self, error: AgentError) -> str:
        """Get user-friendly message for error."""
        return USER_MESSAGES.get(
            error.category,
            USER_MESSAGES[ErrorCategory.UNKNOWN]
        )

    def create_fallback_response(
        self,
        error: AgentError,
        fallback_data: Optional[Dict[str, Any]] = None,
    ) -> FallbackResponse:
        """
        Create a fallback response for the user.

        USP: Always give students something helpful.
        """
        return FallbackResponse(
            success=False,
            error=error,
            fallback_data=fallback_data or {},
            user_message=self.get_user_message(error),
        )

    def register_handler(
        self,
        category: ErrorCategory,
        handler: Callable[[AgentError], Any],
    ) -> None:
        """Register custom handler for error category."""
        self._error_handlers[category] = handler

    def handle(self, error: AgentError) -> Any:
        """Execute registered handler for error."""
        handler = self._error_handlers.get(error.category)
        if handler:
            return handler(error)
        return None

    def get_recent_errors(
        self,
        limit: int = 10,
        category: Optional[ErrorCategory] = None,
    ) -> List[AgentError]:
        """Get recent errors, optionally filtered."""
        errors = self._errors
        if category:
            errors = [e for e in errors if e.category == category]
        return sorted(errors, key=lambda e: e.timestamp, reverse=True)[:limit]


# Retry decorator using tenacity
def with_retry(
    max_attempts: int = 3,
    wait_min: float = 1,
    wait_max: float = 10,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for adding retry logic to functions.

    Uses tenacity if available, otherwise simple fallback.

    Args:
        max_attempts: Maximum retry attempts
        wait_min: Minimum wait between retries (seconds)
        wait_max: Maximum wait between retries (seconds)
        exceptions: Exception types to retry on
    """
    if TENACITY_AVAILABLE:
        return retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(min=wait_min, max=wait_max),
            retry=retry_if_exception_type(exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.DEBUG),
            reraise=True,
        )
    else:
        # Fallback without tenacity
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                import asyncio
                last_exception = None
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            wait_time = min(wait_min * (2 ** attempt), wait_max)
                            logger.warning(
                                f"Attempt {attempt + 1} failed: {e}. "
                                f"Retrying in {wait_time}s..."
                            )
                            await asyncio.sleep(wait_time)
                if last_exception:
                    raise last_exception
                raise RuntimeError("Retry logic failed unexpectedly")
            return wrapper
        return decorator


def safe_execute(
    func: Callable[..., T],
    agent_name: str,
    profile_id: Optional[str] = None,
    fallback_value: Optional[T] = None,
) -> Callable[..., T]:
    """
    Wrap a function with safe execution and error handling.

    Args:
        func: Function to wrap
        agent_name: Name of the agent
        profile_id: Student's profile ID
        fallback_value: Value to return on error

    Returns:
        Wrapped function
    """
    handler = ExceptionHandler()

    @wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error = handler.create_error(
                e,
                agent_name,
                profile_id,
                {"args": str(args)[:100], "kwargs": str(kwargs)[:100]},
            )
            if fallback_value is not None:
                return fallback_value
            raise

    return wrapper


# Convenience functions
def handle_exception(
    exc: Exception,
    agent_name: str,
    profile_id: Optional[str] = None,
) -> FallbackResponse:
    """
    Quick helper to handle an exception.

    Usage:
        try:
            result = await some_operation()
        except Exception as e:
            return handle_exception(e, "awards_agent", profile_id)
    """
    handler = ExceptionHandler()
    error = handler.create_error(exc, agent_name, profile_id)
    return handler.create_fallback_response(error)
