"""
H3: Retry Logic Pattern - Implementation

Intelligent retry with backoff for transient failures.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable, Type
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging
import asyncio
import random

logger = logging.getLogger(__name__)


class BackoffStrategy(str, Enum):
    """Backoff strategies for retry."""
    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"


class RetryConfig(BaseModel):
    """Configuration for retry logic."""
    max_retries: int = 3
    initial_delay_ms: int = 100
    max_delay_ms: int = 10000
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL_JITTER
    backoff_multiplier: float = 2.0
    retryable_exceptions: List[str] = Field(
        default_factory=lambda: ["TimeoutError", "ConnectionError", "HTTPError"]
    )
    non_retryable_exceptions: List[str] = Field(
        default_factory=lambda: ["ValueError", "KeyError", "AuthenticationError"]
    )


class RetryAttempt(BaseModel):
    """Record of a retry attempt."""
    attempt_number: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    error: Optional[str] = None
    delay_ms: int = 0


class RetryResult(BaseModel):
    """Result of retry execution."""
    success: bool = False
    final_result: Optional[Any] = None
    total_attempts: int = 0
    attempts: List[RetryAttempt] = Field(default_factory=list)
    total_duration_ms: int = 0
    final_error: Optional[str] = None


class RetryExecutor:
    """
    Executes operations with intelligent retry.

    Pattern H3: Retry Logic

    GUARDRAILS:
    - NEW class - does not modify existing retry
    - Configurable backoff strategies
    - Respects non-retryable exceptions
    """

    def __init__(
        self,
        config: Optional[RetryConfig] = None,
    ):
        """
        Initialize retry executor.

        Args:
            config: Retry configuration
        """
        self.config = config or RetryConfig()

    async def execute(
        self,
        func: Callable[[], Awaitable[Any]],
        operation_name: str = "operation",
    ) -> RetryResult:
        """
        Execute function with retry.

        Args:
            func: Async function to execute
            operation_name: Name for logging

        Returns:
            RetryResult with outcome
        """
        start_time = datetime.now(timezone.utc)
        attempts = []
        last_error = None

        for attempt in range(1, self.config.max_retries + 1):
            attempt_record = RetryAttempt(
                attempt_number=attempt,
                started_at=datetime.now(timezone.utc),
            )

            try:
                result = await func()

                attempt_record.completed_at = datetime.now(timezone.utc)
                attempt_record.success = True
                attempts.append(attempt_record)

                logger.debug(
                    f"{operation_name} succeeded on attempt {attempt}"
                )

                return RetryResult(
                    success=True,
                    final_result=result,
                    total_attempts=attempt,
                    attempts=attempts,
                    total_duration_ms=int(
                        (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    ),
                )

            except Exception as e:
                last_error = e
                attempt_record.completed_at = datetime.now(timezone.utc)
                attempt_record.error = str(e)

                # Check if retryable
                if not self._is_retryable(e):
                    logger.warning(
                        f"{operation_name} failed with non-retryable error: {e}"
                    )
                    attempts.append(attempt_record)
                    break

                # Calculate delay
                if attempt < self.config.max_retries:
                    delay_ms = self._calculate_delay(attempt)
                    attempt_record.delay_ms = delay_ms

                    logger.info(
                        f"{operation_name} failed on attempt {attempt}, "
                        f"retrying in {delay_ms}ms: {e}"
                    )

                    await asyncio.sleep(delay_ms / 1000)

                attempts.append(attempt_record)

        return RetryResult(
            success=False,
            total_attempts=len(attempts),
            attempts=attempts,
            total_duration_ms=int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            ),
            final_error=str(last_error) if last_error else None,
        )

    def _is_retryable(self, exception: Exception) -> bool:
        """Determine if exception is retryable."""
        exception_name = type(exception).__name__

        # Check non-retryable first
        if exception_name in self.config.non_retryable_exceptions:
            return False

        # Check retryable list
        if self.config.retryable_exceptions:
            return exception_name in self.config.retryable_exceptions

        # Default: retry on most exceptions
        return True

    def _calculate_delay(self, attempt: int) -> int:
        """Calculate delay for next retry."""
        initial = self.config.initial_delay_ms
        max_delay = self.config.max_delay_ms
        multiplier = self.config.backoff_multiplier

        if self.config.backoff_strategy == BackoffStrategy.CONSTANT:
            delay = initial

        elif self.config.backoff_strategy == BackoffStrategy.LINEAR:
            delay = initial * attempt

        elif self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = initial * (multiplier ** (attempt - 1))

        elif self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL_JITTER:
            base_delay = initial * (multiplier ** (attempt - 1))
            jitter = random.uniform(0, base_delay * 0.3)
            delay = base_delay + jitter

        else:
            delay = initial

        return min(int(delay), max_delay)

    async def execute_with_fallback(
        self,
        func: Callable[[], Awaitable[Any]],
        fallback_func: Callable[[], Awaitable[Any]],
        operation_name: str = "operation",
    ) -> RetryResult:
        """
        Execute with retry, using fallback if all retries fail.

        Args:
            func: Primary function
            fallback_func: Fallback function
            operation_name: Name for logging

        Returns:
            RetryResult with outcome
        """
        result = await self.execute(func, operation_name)

        if not result.success:
            logger.info(f"{operation_name} failed after retries, using fallback")
            try:
                fallback_result = await fallback_func()
                result.final_result = fallback_result
                result.success = True
            except Exception as e:
                result.final_error = f"Fallback also failed: {e}"

        return result


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.

    States:
    - CLOSED: Normal operation
    - OPEN: Failing fast, not calling service
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 3,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before trying half-open
            half_open_max_calls: Calls allowed in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max = half_open_max_calls

        self._state = "closed"
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls = 0

    async def call(
        self,
        func: Callable[[], Awaitable[Any]],
    ) -> Any:
        """
        Call function through circuit breaker.

        Args:
            func: Function to call

        Returns:
            Function result

        Raises:
            CircuitBreakerOpen: If circuit is open
        """
        if self._state == "open":
            if self._should_try_half_open():
                self._state = "half_open"
                self._half_open_calls = 0
            else:
                raise CircuitBreakerOpen("Circuit breaker is open")

        if self._state == "half_open":
            if self._half_open_calls >= self.half_open_max:
                raise CircuitBreakerOpen("Half-open call limit reached")
            self._half_open_calls += 1

        try:
            result = await func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _should_try_half_open(self) -> bool:
        """Check if should try half-open state."""
        if not self._last_failure_time:
            return True
        elapsed = (datetime.now(timezone.utc) - self._last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def _on_success(self) -> None:
        """Handle successful call."""
        if self._state == "half_open":
            self._state = "closed"
        self._failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = datetime.now(timezone.utc)

        if self._failure_count >= self.failure_threshold:
            self._state = "open"
            logger.warning("Circuit breaker opened")

    @property
    def state(self) -> str:
        """Get current state."""
        return self._state

    @property
    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self._state == "open"


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    pass
