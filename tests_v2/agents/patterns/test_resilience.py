# tests/agents/patterns/test_resilience.py
"""
Tests for Resilience patterns: H1 Exception Handling
CORRECTED to match actual implementation API
"""

import pytest


class TestFailureType:
    """Tests for FailureType enum."""
    
    def test_failure_type_exists(self):
        """Test FailureType enum exists."""
        from agents.resilience.exception_handling import FailureType
        
        assert FailureType is not None
    
    def test_failure_type_values(self):
        """Test FailureType has expected values."""
        from agents.resilience.exception_handling import FailureType
        
        # Should have common failure types
        assert hasattr(FailureType, 'LLM_TIMEOUT')
        assert hasattr(FailureType, 'LLM_RATE_LIMIT')


class TestRecoveryStrategy:
    """Tests for RecoveryStrategy enum."""
    
    def test_recovery_strategy_exists(self):
        """Test RecoveryStrategy enum exists."""
        from agents.resilience.exception_handling import RecoveryStrategy
        
        assert RecoveryStrategy is not None
    
    def test_recovery_strategy_values(self):
        """Test RecoveryStrategy has expected values."""
        from agents.resilience.exception_handling import RecoveryStrategy
        
        values = [e.value for e in RecoveryStrategy]
        assert len(values) > 0


class TestExceptionHandler:
    """Tests for Exception Handler (H1)."""
    
    def test_handler_initialization(self):
        """Test ExceptionHandler initialization."""
        from agents.resilience.exception_handling import ExceptionHandler
        
        handler = ExceptionHandler()
        assert handler is not None
    
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
    
    def test_classify_unknown(self):
        """Test classification of unknown errors."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType
        
        handler = ExceptionHandler()
        
        failure_type = handler.classify_failure(Exception("Something weird happened"))
        
        assert failure_type == FailureType.UNKNOWN
    
    def test_get_recovery_strategy(self):
        """Test getting recovery strategy."""
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
        """Test recovery strategy for tool failure."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType, RecoveryStrategy
        
        handler = ExceptionHandler()
        
        strategy = handler.get_recovery_strategy(FailureType.TOOL_FAILURE)
        
        assert strategy == RecoveryStrategy.FALLBACK
    
    def test_recovery_strategy_unknown(self):
        """Test recovery strategy for unknown escalates."""
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
    
    @pytest.mark.asyncio
    async def test_handle_returns_dict(self):
        """Test handle returns expected format."""
        from agents.resilience.exception_handling import ExceptionHandler
        
        handler = ExceptionHandler()
        
        result = await handler.handle(
            error=Exception("Test error"),
            context={},
        )
        
        assert isinstance(result, dict)
        assert "action_taken" in result


class TestRetryDecorator:
    """Tests for retry decorator."""
    
    def test_with_retry_exists(self):
        """Test with_retry decorator exists."""
        from agents.resilience.exception_handling import with_retry
        
        assert with_retry is not None
    
    def test_with_retry_callable(self):
        """Test with_retry is callable."""
        from agents.resilience.exception_handling import with_retry
        
        # Should be able to create decorator
        decorator = with_retry(max_attempts=3)
        assert callable(decorator)


class TestExceptionHandlingDecorator:
    """Tests for exception handling decorator."""
    
    def test_decorator_exists(self):
        """Test with_exception_handling decorator exists."""
        from agents.resilience.exception_handling import with_exception_handling
        
        assert with_exception_handling is not None
    
    def test_decorator_callable(self):
        """Test with_exception_handling is callable."""
        from agents.resilience.exception_handling import with_exception_handling
        
        decorator = with_exception_handling(fallback_result={})
        assert callable(decorator)
    
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
