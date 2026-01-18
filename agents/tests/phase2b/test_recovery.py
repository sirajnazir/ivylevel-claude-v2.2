"""
Tests for H2: Graceful Degradation and H3: Retry Logic Patterns
"""

import pytest
from datetime import datetime, timezone
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.recovery.graceful_degradation_v8 import (
    GracefulDegradationManager,
    FallbackConfig,
    ServiceHealth,
    IvyLevelFallbacks,
)
from middleware.recovery.retry_logic_v8 import (
    RetryExecutor,
    RetryConfig,
    BackoffStrategy,
    CircuitBreaker,
    CircuitBreakerOpen,
)


class TestFallbackConfig:
    """Tests for FallbackConfig model."""

    def test_config_creation(self):
        """Test FallbackConfig creation."""
        config = FallbackConfig(
            service_name="openai",
            fallback_name="openai_fallback",
            trigger_after_failures=3,
        )
        assert config.service_name == "openai"
        assert config.trigger_after_failures == 3

    def test_config_with_recovery(self):
        """Test FallbackConfig with recovery settings."""
        config = FallbackConfig(
            service_name="supabase",
            fallback_name="supabase_fallback",
            trigger_after_failures=5,
            recovery_after_successes=10,
        )
        assert config.recovery_after_successes == 10


class TestServiceHealth:
    """Tests for ServiceHealth model."""

    def test_health_creation(self):
        """Test ServiceHealth creation."""
        from middleware.recovery.graceful_degradation_v8 import ServiceStatus
        health = ServiceHealth(
            service_name="openai",
            status=ServiceStatus.HEALTHY,
        )
        assert health.status == ServiceStatus.HEALTHY
        assert health.consecutive_failures == 0

    def test_health_degraded(self):
        """Test degraded service health."""
        from middleware.recovery.graceful_degradation_v8 import ServiceStatus
        health = ServiceHealth(
            service_name="openai",
            status=ServiceStatus.UNAVAILABLE,
            consecutive_failures=3,
            error_message="Rate limit exceeded",
        )
        assert health.status == ServiceStatus.UNAVAILABLE
        assert health.consecutive_failures == 3


class TestGracefulDegradationManager:
    """Tests for GracefulDegradationManager."""

    @pytest.fixture
    def manager(self):
        return GracefulDegradationManager()

    def test_manager_creation(self, manager):
        """Test manager creation."""
        assert manager is not None
        assert manager.health_interval == 30

    def test_manager_creation_with_params(self):
        """Test manager creation with custom params."""
        manager = GracefulDegradationManager(
            health_check_interval=60,
        )
        assert manager.health_interval == 60

    def test_register_fallback(self, manager):
        """Test registering a fallback."""
        async def fallback(args):
            return "fallback"

        manager.register_fallback(
            service_name="test_service",
            fallback_handler=fallback,
        )
        assert "test_service" in manager._fallback_handlers

    @pytest.mark.asyncio
    async def test_call_with_fallback_success(self, manager):
        """Test successful call without fallback."""
        async def primary():
            return "primary_result"

        result = await manager.call_with_fallback(
            service_name="test_service",
            primary_func=primary,
        )
        assert result == "primary_result"

    @pytest.mark.asyncio
    async def test_call_with_fallback_failure(self, manager):
        """Test call with failure triggers fallback."""
        async def failing_primary():
            raise Exception("Primary failed")

        async def fallback(args):
            return "fallback_result"

        manager.register_fallback("test_service", fallback)

        result = await manager.call_with_fallback(
            service_name="test_service",
            primary_func=failing_primary,
        )
        assert result == "fallback_result"

    @pytest.mark.asyncio
    async def test_service_health_tracking(self, manager):
        """Test service health is tracked."""
        async def failing():
            raise Exception("Failed")

        async def fallback(args):
            return "fallback"

        manager.register_fallback("tracked_service", fallback)

        # Fail multiple times
        for _ in range(3):
            await manager.call_with_fallback(
                service_name="tracked_service",
                primary_func=failing,
            )

        health = manager.get_service_health("tracked_service")
        assert health.consecutive_failures >= 3


class TestIvyLevelFallbacks:
    """Tests for IvyLevelFallbacks."""

    @pytest.mark.asyncio
    async def test_llm_fallback(self):
        """Test LLM fallback execution."""
        result = await IvyLevelFallbacks.llm_fallback({})
        assert "apologize" in result.lower() or "technical" in result.lower()

    @pytest.mark.asyncio
    async def test_database_fallback(self):
        """Test database fallback execution."""
        result = await IvyLevelFallbacks.database_fallback({"cached_data": {"key": "value"}})
        assert result["status"] == "cached"

    @pytest.mark.asyncio
    async def test_embedding_fallback(self):
        """Test embedding fallback execution."""
        result = await IvyLevelFallbacks.embedding_fallback({"dimension": 10})
        assert len(result) == 10
        assert all(v == 0.0 for v in result)


class TestBackoffStrategy:
    """Tests for BackoffStrategy enum."""

    def test_strategy_values(self):
        """Test backoff strategy values."""
        assert BackoffStrategy.CONSTANT.value == "constant"
        assert BackoffStrategy.LINEAR.value == "linear"
        assert BackoffStrategy.EXPONENTIAL.value == "exponential"
        assert BackoffStrategy.EXPONENTIAL_JITTER.value == "exponential_jitter"


class TestRetryConfig:
    """Tests for RetryConfig model."""

    def test_config_creation(self):
        """Test RetryConfig creation."""
        config = RetryConfig(
            max_retries=3,
            initial_delay_ms=100,
        )
        assert config.max_retries == 3
        assert config.initial_delay_ms == 100

    def test_config_with_strategy(self):
        """Test RetryConfig with strategy."""
        config = RetryConfig(
            max_retries=5,
            initial_delay_ms=200,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            max_delay_ms=5000,
        )
        assert config.backoff_strategy == BackoffStrategy.EXPONENTIAL
        assert config.max_delay_ms == 5000

    def test_config_with_exceptions(self):
        """Test RetryConfig with specific exceptions."""
        config = RetryConfig(
            max_retries=3,
            initial_delay_ms=100,
            retryable_exceptions=["ValueError", "ConnectionError"],
        )
        assert "ValueError" in config.retryable_exceptions


class TestCircuitBreakerStates:
    """Tests for circuit breaker states."""

    def test_state_values(self):
        """Test circuit breaker state values."""
        breaker = CircuitBreaker()
        # States are strings: "closed", "open", "half_open"
        assert breaker.state == "closed"
        assert not breaker.is_open


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""

    @pytest.fixture
    def breaker(self):
        return CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=1,  # 1 second for tests
        )

    def test_breaker_creation(self, breaker):
        """Test circuit breaker creation."""
        assert breaker.state == "closed"

    def test_breaker_creation_with_params(self):
        """Test circuit breaker creation with params."""
        breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            half_open_max_calls=2,
        )
        assert breaker.failure_threshold == 5
        assert breaker.half_open_max == 2

    @pytest.mark.asyncio
    async def test_successful_call(self, breaker):
        """Test recording success through call."""
        async def success():
            return "ok"
        result = await breaker.call(success)
        assert result == "ok"
        assert breaker._failure_count == 0

    @pytest.mark.asyncio
    async def test_failures_open_circuit(self, breaker):
        """Test failures open circuit."""
        async def failing():
            raise Exception("Failed")

        for _ in range(3):
            try:
                await breaker.call(failing)
            except Exception:
                pass

        assert breaker.state == "open"

    def test_is_open_property(self, breaker):
        """Test is_open property when closed."""
        assert breaker.is_open == False

    @pytest.mark.asyncio
    async def test_open_circuit_raises(self, breaker):
        """Test open circuit raises CircuitBreakerOpen."""
        async def failing():
            raise Exception("Failed")

        # Fail enough to open
        for _ in range(3):
            try:
                await breaker.call(failing)
            except Exception:
                pass

        # Next call should raise CircuitBreakerOpen
        with pytest.raises(CircuitBreakerOpen):
            await breaker.call(failing)


class TestRetryExecutor:
    """Tests for RetryExecutor."""

    @pytest.fixture
    def executor(self):
        return RetryExecutor()

    def test_executor_creation(self, executor):
        """Test executor creation."""
        assert executor is not None

    @pytest.mark.asyncio
    async def test_execute_success(self, executor):
        """Test executing successful function."""
        async def success_func():
            return "success"

        result = await executor.execute(success_func)
        assert result.success == True
        assert result.final_result == "success"

    @pytest.mark.asyncio
    async def test_execute_with_retries(self, executor):
        """Test execution with retries."""
        call_count = {"count": 0}

        async def failing_then_success():
            call_count["count"] += 1
            if call_count["count"] < 3:
                raise ConnectionError("Temporary failure")
            return "success"

        config = RetryConfig(
            max_retries=3,
            initial_delay_ms=10,  # Fast for testing
        )

        executor = RetryExecutor(config)
        result = await executor.execute(failing_then_success)
        assert result.success == True
        assert result.final_result == "success"
        assert call_count["count"] == 3

    @pytest.mark.asyncio
    async def test_execute_max_retries_exceeded(self, executor):
        """Test max retries exceeded."""
        async def always_fail():
            raise ConnectionError("Always fails")

        config = RetryConfig(
            max_retries=2,
            initial_delay_ms=10,
        )

        executor = RetryExecutor(config)
        result = await executor.execute(always_fail)
        assert result.success == False
        assert result.final_error is not None

    @pytest.mark.asyncio
    async def test_execute_with_fallback(self, executor):
        """Test execution with fallback on failure."""
        async def failing():
            raise ConnectionError("Failed")

        async def fallback():
            return "fallback_result"

        config = RetryConfig(max_retries=1, initial_delay_ms=10)
        executor = RetryExecutor(config)

        result = await executor.execute_with_fallback(failing, fallback)
        assert result.success == True
        assert result.final_result == "fallback_result"
