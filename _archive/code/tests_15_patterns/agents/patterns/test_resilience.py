# tests/agents/patterns/test_resilience.py
"""
Tests for Resilience patterns: H1 Exception Handling
"""

import pytest
from unittest.mock import AsyncMock


class TestExceptionHandler:
    """Tests for Exception Handler (H1)."""
    
    def test_classify_timeout(self):
        """Test classification of timeout errors."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType
        
        handler = ExceptionHandler()
        
        failure_type = handler.classify_failure(TimeoutError("Request timed out"))
        
        assert failure_type == FailureType.LLM_TIMEOUT
    
    def test_classify_rate_limit(self):
        """Test classification of rate limit errors."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType
        
        handler = ExceptionHandler()
        
        failure_type = handler.classify_failure(Exception("429 Too Many Requests"))
        
        assert failure_type == FailureType.LLM_RATE_LIMIT
    
    def test_classify_database_error(self):
        """Test classification of database errors."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType
        
        handler = ExceptionHandler()
        
        failure_type = handler.classify_failure(Exception("Database connection failed"))
        
        assert failure_type == FailureType.DATABASE_ERROR
    
    def test_classify_tool_failure(self):
        """Test classification of tool failures."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType
        
        handler = ExceptionHandler()
        
        failure_type = handler.classify_failure(Exception("Tool execution failed"))
        
        assert failure_type == FailureType.TOOL_FAILURE
    
    def test_classify_validation_error(self):
        """Test classification of validation errors."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType
        
        handler = ExceptionHandler()
        
        failure_type = handler.classify_failure(Exception("Pydantic validation error"))
        
        assert failure_type == FailureType.VALIDATION_ERROR
    
    def test_classify_unknown(self):
        """Test classification of unknown errors."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType
        
        handler = ExceptionHandler()
        
        failure_type = handler.classify_failure(Exception("Something weird happened"))
        
        assert failure_type == FailureType.UNKNOWN
    
    def test_recovery_strategy_timeout(self):
        """Test recovery strategy for timeout."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType, RecoveryStrategy
        
        handler = ExceptionHandler()
        
        strategy = handler.get_recovery_strategy(FailureType.LLM_TIMEOUT)
        
        assert strategy == RecoveryStrategy.RETRY_WITH_BACKOFF
    
    def test_recovery_strategy_rate_limit(self):
        """Test recovery strategy for rate limit."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType, RecoveryStrategy
        
        handler = ExceptionHandler()
        
        strategy = handler.get_recovery_strategy(FailureType.LLM_RATE_LIMIT)
        
        assert strategy == RecoveryStrategy.RETRY_WITH_BACKOFF
    
    def test_recovery_strategy_tool_failure(self):
        """Test recovery strategy for tool failure - should fallback."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType, RecoveryStrategy
        
        handler = ExceptionHandler()
        
        strategy = handler.get_recovery_strategy(FailureType.TOOL_FAILURE)
        
        assert strategy == RecoveryStrategy.FALLBACK
    
    def test_recovery_strategy_unknown_escalates(self):
        """Test recovery strategy for unknown - should escalate."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType, RecoveryStrategy
        
        handler = ExceptionHandler()
        
        strategy = handler.get_recovery_strategy(FailureType.UNKNOWN)
        
        assert strategy == RecoveryStrategy.ESCALATE
    
    @pytest.mark.asyncio
    async def test_handle_with_fallback(self):
        """Test handling with fallback."""
        from agents.resilience.exception_handling import ExceptionHandler
        
        handler = ExceptionHandler()
        
        result = await handler.handle(
            error=Exception("Tool failed"),
            context={"function": "test"},
            fallback=lambda: {"fallback": True},
        )
        
        assert result["recovered"] is True
        assert result["result"]["fallback"] is True
    
    @pytest.mark.asyncio
    async def test_handle_graceful_degradation(self):
        """Test graceful degradation for validation errors."""
        from agents.resilience.exception_handling import ExceptionHandler
        
        handler = ExceptionHandler()
        
        result = await handler.handle(
            error=Exception("Validation error occurred"),
            context={"function": "test"},
            fallback=None,
        )
        
        assert "action_taken" in result
    
    @pytest.mark.asyncio
    async def test_handle_escalation(self):
        """Test escalation for unrecoverable errors."""
        from agents.resilience.exception_handling import ExceptionHandler
        
        handler = ExceptionHandler()
        
        result = await handler.handle(
            error=Exception("Unknown catastrophic failure"),
            context={"function": "test"},
            fallback=None,
        )
        
        # Should escalate
        assert "action_taken" in result


class TestRetryDecorator:
    """Tests for retry decorator."""
    
    @pytest.mark.asyncio
    async def test_retry_success_first_try(self):
        """Test successful call on first try."""
        from agents.resilience.exception_handling import with_retry
        
        call_count = 0
        
        @with_retry(max_attempts=3)
        async def succeeds():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await succeeds()
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_success_after_failure(self):
        """Test successful call after initial failures."""
        from agents.resilience.exception_handling import with_retry
        
        call_count = 0
        
        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.02)
        async def succeeds_eventually():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = await succeeds_eventually()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Test that retries eventually give up."""
        from agents.resilience.exception_handling import with_retry
        
        @with_retry(max_attempts=2, min_wait=0.01, max_wait=0.02)
        async def always_fails():
            raise ConnectionError("Permanent failure")
        
        with pytest.raises(ConnectionError):
            await always_fails()


class TestExceptionHandlingDecorator:
    """Tests for exception handling decorator."""
    
    @pytest.mark.asyncio
    async def test_decorator_success(self):
        """Test decorator with successful function."""
        from agents.resilience.exception_handling import with_exception_handling
        
        @with_exception_handling(fallback_result={"error": True})
        async def succeeds():
            return {"success": True}
        
        result = await succeeds()
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_decorator_fallback(self):
        """Test decorator uses fallback on error."""
        from agents.resilience.exception_handling import with_exception_handling
        
        @with_exception_handling(fallback_result={"fallback": True})
        async def fails():
            raise Exception("Test error")
        
        result = await fails()
        
        assert result["fallback"] is True
