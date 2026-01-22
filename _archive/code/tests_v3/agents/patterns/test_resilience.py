# tests/agents/patterns/test_resilience.py
"""
Tests for Resilience patterns: H1 Exception Handling
"""

import pytest


class TestExceptionHandler:
    """Tests for ExceptionHandler (H1)."""
    
    def test_handler_importable(self):
        """Test ExceptionHandler can be imported."""
        from agents.resilience.exception_handling import ExceptionHandler
        assert ExceptionHandler is not None
    
    def test_handler_initialization(self):
        """Test ExceptionHandler can be initialized."""
        from agents.resilience.exception_handling import ExceptionHandler
        handler = ExceptionHandler()
        assert handler is not None
    
    def test_handler_has_classify_failure(self):
        """Test ExceptionHandler has classify_failure method."""
        from agents.resilience.exception_handling import ExceptionHandler
        handler = ExceptionHandler()
        assert hasattr(handler, 'classify_failure')
    
    def test_handler_has_get_recovery_strategy(self):
        """Test ExceptionHandler has get_recovery_strategy method."""
        from agents.resilience.exception_handling import ExceptionHandler
        handler = ExceptionHandler()
        assert hasattr(handler, 'get_recovery_strategy')
    
    def test_handler_has_handle(self):
        """Test ExceptionHandler has handle method."""
        from agents.resilience.exception_handling import ExceptionHandler
        handler = ExceptionHandler()
        assert hasattr(handler, 'handle')


class TestFailureType:
    """Tests for FailureType enum."""
    
    def test_failure_type_importable(self):
        """Test FailureType can be imported."""
        from agents.resilience.exception_handling import FailureType
        assert FailureType is not None
    
    def test_failure_type_is_enum(self):
        """Test FailureType is an enum."""
        from agents.resilience.exception_handling import FailureType
        from enum import Enum
        assert issubclass(FailureType, Enum)
    
    def test_failure_type_has_timeout(self):
        """Test FailureType has LLM_TIMEOUT."""
        from agents.resilience.exception_handling import FailureType
        assert hasattr(FailureType, 'LLM_TIMEOUT')
    
    def test_failure_type_has_rate_limit(self):
        """Test FailureType has LLM_RATE_LIMIT."""
        from agents.resilience.exception_handling import FailureType
        assert hasattr(FailureType, 'LLM_RATE_LIMIT')


class TestRecoveryStrategy:
    """Tests for RecoveryStrategy enum."""
    
    def test_recovery_strategy_importable(self):
        """Test RecoveryStrategy can be imported."""
        from agents.resilience.exception_handling import RecoveryStrategy
        assert RecoveryStrategy is not None
    
    def test_recovery_strategy_is_enum(self):
        """Test RecoveryStrategy is an enum."""
        from agents.resilience.exception_handling import RecoveryStrategy
        from enum import Enum
        assert issubclass(RecoveryStrategy, Enum)
    
    def test_recovery_strategy_has_retry(self):
        """Test RecoveryStrategy has RETRY_WITH_BACKOFF."""
        from agents.resilience.exception_handling import RecoveryStrategy
        assert hasattr(RecoveryStrategy, 'RETRY_WITH_BACKOFF')


class TestExceptionClassification:
    """Tests for exception classification."""
    
    def test_classify_timeout(self):
        """Test classifying timeout error."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType
        handler = ExceptionHandler()
        failure_type = handler.classify_failure(TimeoutError("Request timed out"))
        assert failure_type == FailureType.LLM_TIMEOUT
    
    def test_classify_rate_limit(self):
        """Test classifying rate limit error."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType
        handler = ExceptionHandler()
        failure_type = handler.classify_failure(Exception("429 Too Many Requests"))
        assert failure_type == FailureType.LLM_RATE_LIMIT
    
    def test_classify_unknown(self):
        """Test classifying unknown error."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType
        handler = ExceptionHandler()
        failure_type = handler.classify_failure(Exception("Something weird"))
        assert failure_type == FailureType.UNKNOWN


class TestRecoveryStrategies:
    """Tests for recovery strategies."""
    
    def test_timeout_recovery(self):
        """Test recovery strategy for timeout."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType, RecoveryStrategy
        handler = ExceptionHandler()
        strategy = handler.get_recovery_strategy(FailureType.LLM_TIMEOUT)
        assert strategy == RecoveryStrategy.RETRY_WITH_BACKOFF
    
    def test_rate_limit_recovery(self):
        """Test recovery strategy for rate limit."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType, RecoveryStrategy
        handler = ExceptionHandler()
        strategy = handler.get_recovery_strategy(FailureType.LLM_RATE_LIMIT)
        assert strategy == RecoveryStrategy.RETRY_WITH_BACKOFF
    
    def test_unknown_recovery(self):
        """Test recovery strategy for unknown."""
        from agents.resilience.exception_handling import ExceptionHandler, FailureType, RecoveryStrategy
        handler = ExceptionHandler()
        strategy = handler.get_recovery_strategy(FailureType.UNKNOWN)
        assert strategy == RecoveryStrategy.ESCALATE


class TestDecorators:
    """Tests for decorators."""
    
    def test_with_retry_importable(self):
        """Test with_retry can be imported."""
        from agents.resilience.exception_handling import with_retry
        assert with_retry is not None
    
    def test_with_exception_handling_importable(self):
        """Test with_exception_handling can be imported."""
        from agents.resilience.exception_handling import with_exception_handling
        assert with_exception_handling is not None
    
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
