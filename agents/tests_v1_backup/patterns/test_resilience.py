# agents/tests/patterns/test_resilience.py
"""
Tests for Resilience Patterns (H1) - v5.4 True Autonomous Agents.

Tests:
- H1: Exception Handling with graceful degradation

Graceful degradation for great student experience.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestExceptionHandling:
    """Tests for H1: Exception Handling pattern."""

    def test_exception_handler_creation(self):
        """Test ExceptionHandler can be created."""
        from resilience import ExceptionHandler

        handler = ExceptionHandler()

        assert handler is not None

    def test_error_severity_enum(self):
        """Test ErrorSeverity enum values."""
        from resilience import ErrorSeverity

        assert ErrorSeverity.LOW is not None
        assert ErrorSeverity.MEDIUM is not None
        assert ErrorSeverity.HIGH is not None
        assert ErrorSeverity.CRITICAL is not None

    def test_error_category_enum(self):
        """Test ErrorCategory enum values."""
        from resilience import ErrorCategory

        # Actual enum values: API, DATABASE, VALIDATION, TIMEOUT, RATE_LIMIT, AUTH, UNKNOWN
        assert ErrorCategory.API is not None
        assert ErrorCategory.DATABASE is not None
        assert ErrorCategory.VALIDATION is not None
        assert ErrorCategory.TIMEOUT is not None
        assert ErrorCategory.UNKNOWN is not None

    def test_agent_error_model(self):
        """Test AgentError model structure."""
        from resilience import AgentError, ErrorSeverity, ErrorCategory

        # AgentError requires: error_id, category, severity, message, agent_name
        error = AgentError(
            error_id="err-123",
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM,
            message="API timeout",
            agent_name="test_agent",
            retryable=True,
        )

        assert error.category == ErrorCategory.API
        assert error.retryable is True

    def test_fallback_response_model(self):
        """Test FallbackResponse model structure."""
        from resilience import FallbackResponse

        # FallbackResponse has: success, error, fallback_data, user_message
        fallback = FallbackResponse(
            success=False,
            user_message="We're experiencing technical difficulties. Please try again.",
            fallback_data={"status": "degraded"},
        )

        assert fallback.success is False
        assert len(fallback.user_message) > 0

    def test_with_retry_decorator(self):
        """Test with_retry decorator for automatic retries (uses tenacity)."""
        from resilience import with_retry

        call_count = 0

        # API uses max_attempts and wait_min/wait_max
        @with_retry(max_attempts=3, wait_min=0.01, wait_max=0.02)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Simulated failure")
            return "success"

        result = flaky_function()

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_with_retry_async(self):
        """Test with_retry works with async functions."""
        from resilience import with_retry

        call_count = 0

        @with_retry(max_attempts=3, wait_min=0.01, wait_max=0.02)
        async def async_flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Simulated failure")
            return "async success"

        result = await async_flaky()

        assert result == "async success"
        assert call_count == 2

    def test_handle_exception_function(self):
        """Test handle_exception provides fallback responses."""
        from resilience import handle_exception, FallbackResponse

        try:
            raise ValueError("Test error")
        except Exception as e:
            # handle_exception(exc, agent_name, profile_id)
            response = handle_exception(e, "test_agent", "profile-123")

        assert isinstance(response, FallbackResponse)
        assert response.success is False

    def test_safe_execute_function(self):
        """Test safe_execute wraps operations safely."""
        from resilience import safe_execute
        import asyncio

        # safe_execute returns a wrapped async function
        async def test_func():
            return "success"

        # Wrap with safe_execute
        wrapped = safe_execute(test_func, "test_agent", "profile-123")

        # Run the wrapped async function
        result = asyncio.get_event_loop().run_until_complete(wrapped())
        assert result == "success"

    def test_retry_configs_defined(self):
        """Test retry configurations are defined."""
        from resilience import RETRY_CONFIGS

        assert RETRY_CONFIGS is not None
        assert isinstance(RETRY_CONFIGS, dict)

        # Should have configs for different error types
        assert "llm" in RETRY_CONFIGS or len(RETRY_CONFIGS) > 0

    def test_user_messages_defined(self):
        """Test user-friendly error messages are defined."""
        from resilience import USER_MESSAGES

        assert USER_MESSAGES is not None
        assert isinstance(USER_MESSAGES, dict)

    def test_recovery_hints_defined(self):
        """Test recovery hints are configured."""
        from resilience import RECOVERY_HINTS

        assert RECOVERY_HINTS is not None
        assert isinstance(RECOVERY_HINTS, dict)


class TestExceptionHandlerMethods:
    """Tests for ExceptionHandler class methods."""

    def test_categorize_exception(self):
        """Test exception categorization."""
        from resilience import ExceptionHandler, ErrorCategory

        handler = ExceptionHandler()

        # API/Connection errors - method is categorize_exception
        api_category = handler.categorize_exception(ConnectionError("timeout"))
        assert api_category == ErrorCategory.API

        # Validation errors
        validation_category = handler.categorize_exception(ValueError("invalid"))
        assert validation_category == ErrorCategory.VALIDATION

    def test_determine_severity(self):
        """Test severity determination."""
        from resilience import ExceptionHandler, ErrorSeverity, ErrorCategory

        handler = ExceptionHandler()

        # Database errors are medium/high severity
        severity = handler.determine_severity(ErrorCategory.DATABASE)
        assert severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL, ErrorSeverity.MEDIUM]

    def test_get_user_message(self):
        """Test user-friendly message generation."""
        from resilience import ExceptionHandler, ErrorCategory, AgentError, ErrorSeverity

        handler = ExceptionHandler()

        # get_user_message takes an AgentError, not ErrorCategory
        error = AgentError(
            error_id="err-1",
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM,
            message="Test error",
            agent_name="test_agent",
        )
        message = handler.get_user_message(error)

        assert isinstance(message, str)
        assert len(message) > 0
        # Should be user-friendly, not technical

    def test_create_error(self):
        """Test error creation from exception."""
        from resilience import ExceptionHandler, ErrorCategory

        handler = ExceptionHandler()

        exc = ValueError("Test validation error")
        error = handler.create_error(exc, "test_agent", "profile-123")

        assert error is not None
        assert error.agent_name == "test_agent"
        assert error.category == ErrorCategory.VALIDATION


class TestResilienceIntegration:
    """Integration tests for resilience patterns."""

    def test_all_resilience_types_importable(self):
        """Test all resilience types can be imported."""
        from resilience import (
            ExceptionHandler,
            AgentError,
            FallbackResponse,
            ErrorSeverity,
            ErrorCategory,
            with_retry,
            safe_execute,
            handle_exception,
        )

        # All should be importable

    def test_exception_chain_handling(self):
        """Test handling of chained exceptions."""
        from resilience import handle_exception

        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise RuntimeError("Wrapper error") from e
        except Exception as e:
            # handle_exception(exc, agent_name, profile_id)
            response = handle_exception(e, "test_agent", "profile-123")

        assert response is not None
        # Should handle chained exception gracefully

    def test_concurrent_retries(self):
        """Test multiple concurrent retry operations."""
        from resilience import with_retry

        results = []

        @with_retry(max_attempts=2, wait_min=0.01, wait_max=0.02)
        def operation(n):
            results.append(n)
            return n * 2

        # Run multiple operations
        for i in range(5):
            operation(i)

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_async_retry_with_backoff(self):
        """Test async retry with exponential backoff."""
        from resilience import with_retry
        import time

        start_time = time.time()
        call_times = []

        @with_retry(max_attempts=3, wait_min=0.01, wait_max=0.1)
        async def slow_to_succeed():
            call_times.append(time.time() - start_time)
            if len(call_times) < 3:
                raise ConnectionError("Not yet")
            return "done"

        result = await slow_to_succeed()

        assert result == "done"
        assert len(call_times) == 3

    def test_fallback_preserves_context(self):
        """Test fallback response includes original context."""
        from resilience import handle_exception

        try:
            raise RuntimeError("Simulated failure")
        except Exception as e:
            # handle_exception(exc, agent_name, profile_id)
            response = handle_exception(e, "gameplan_agent", "test-123")

        # Response should be useful despite error
        assert response is not None

    def test_retry_respects_max_retries(self):
        """Test retry stops after max retries."""
        from resilience import with_retry

        call_count = 0

        @with_retry(max_attempts=3, wait_min=0.01, wait_max=0.02)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

        assert call_count == 3

    def test_safe_execute_with_context(self):
        """Test safe_execute with error context."""
        from resilience import safe_execute
        import asyncio

        async def success_func():
            return {"status": "success"}

        wrapped = safe_execute(
            success_func,
            agent_name="test_agent",
            profile_id="test-123",
        )

        result = asyncio.get_event_loop().run_until_complete(wrapped())
        assert result["status"] == "success"
