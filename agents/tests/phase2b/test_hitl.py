"""
Tests for G4: Atomic Operations Pattern
"""

import pytest
from datetime import datetime, timezone
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.hitl.atomic_operations_v8 import (
    AtomicOperationExecutor,
    AtomicOperation,
    AtomicOperationResult,
    IvyLevelRollbackHandlers,
)


class TestAtomicOperation:
    """Tests for AtomicOperation model."""

    def test_operation_creation(self):
        """Test AtomicOperation creation."""
        op = AtomicOperation(
            name="update_profile",
            description="Update user profile",
            target_resource="profile/123",
        )
        assert op.name == "update_profile"
        assert op.target_resource == "profile/123"

    def test_operation_with_payload(self):
        """Test AtomicOperation with payload."""
        op = AtomicOperation(
            name="update_profile",
            description="Update profile data",
            target_resource="profile/123",
            payload={"profile_id": "123", "name": "New Name"},
        )
        assert op.payload["profile_id"] == "123"
        assert op.payload["name"] == "New Name"


class TestAtomicOperationResult:
    """Tests for AtomicOperationResult model."""

    def test_result_creation(self):
        """Test AtomicOperationResult creation."""
        result = AtomicOperationResult(
            operation_id="op-123",
            success=True,
            result={"updated": True},
        )
        assert result.success == True
        assert result.result["updated"] == True

    def test_result_with_error(self):
        """Test AtomicOperationResult with error."""
        result = AtomicOperationResult(
            operation_id="op-456",
            success=False,
            error="Database connection failed",
        )
        assert result.success == False
        assert "Database" in result.error

    def test_result_with_rollback(self):
        """Test AtomicOperationResult with rollback."""
        result = AtomicOperationResult(
            operation_id="op-789",
            success=False,
            error="Validation failed",
            was_rolled_back=True,
        )
        assert result.was_rolled_back == True


class TestAtomicOperationExecutor:
    """Tests for AtomicOperationExecutor."""

    @pytest.fixture
    def executor(self, mock_supabase):
        return AtomicOperationExecutor(supabase_client=mock_supabase)

    def test_executor_creation(self, executor):
        """Test executor creation."""
        assert executor is not None

    @pytest.mark.asyncio
    async def test_execute_success(self, executor):
        """Test executing successful operation."""
        async def success_func(payload):
            return {"data": "value"}

        op = AtomicOperation(
            name="test_op",
            description="Test operation",
            target_resource="test/123",
        )
        result = await executor.execute(op, success_func)

        assert result.success == True
        assert result.result["data"] == "value"

    @pytest.mark.asyncio
    async def test_execute_with_error_and_rollback(self, executor):
        """Test executing operation that fails and rolls back."""
        call_count = {"execute": 0, "rollback": 0}

        async def failing_func(payload):
            call_count["execute"] += 1
            raise ValueError("Test error")

        async def rollback_func(rollback_data):
            call_count["rollback"] += 1

        op = AtomicOperation(
            name="failing_op",
            description="Failing operation",
            target_resource="test/123",
        )

        result = await executor.execute(op, failing_func, rollback_func)

        # Should have tried to rollback
        assert result.success == False
        assert call_count["rollback"] == 1

    @pytest.mark.asyncio
    async def test_execute_batch_success(self, executor):
        """Test executing batch of operations."""
        results_list = []

        async def op1_func(payload):
            results_list.append("op1")
            return "result1"

        async def op2_func(payload):
            results_list.append("op2")
            return "result2"

        ops = [
            AtomicOperation(name="op1", description="Op 1", target_resource="test/1"),
            AtomicOperation(name="op2", description="Op 2", target_resource="test/2"),
        ]

        batch_results = await executor.execute_batch(ops, [op1_func, op2_func])
        assert len(batch_results) == 2
        assert "op1" in results_list
        assert "op2" in results_list


class TestIvyLevelRollbackHandlers:
    """Tests for IvyLevelRollbackHandlers."""

    @pytest.fixture
    def handlers(self, mock_supabase):
        return IvyLevelRollbackHandlers(supabase_client=mock_supabase)

    def test_handlers_creation(self, handlers):
        """Test handlers creation."""
        assert handlers is not None

    @pytest.mark.asyncio
    async def test_profile_rollback(self, handlers):
        """Test profile rollback handler."""
        # Should not raise
        await handlers.rollback_profile(
            rollback_data={"previous_state": {"id": "123", "name": "Old Name"}},
        )

    @pytest.mark.asyncio
    async def test_task_rollback(self, handlers):
        """Test task rollback handler."""
        # Should not raise
        await handlers.rollback_task(
            rollback_data={"previous_state": {"id": "task-456", "status": "pending"}},
        )

    def test_get_handlers(self, handlers):
        """Test getting all handlers."""
        all_handlers = handlers.get_handlers()
        assert "profile" in all_handlers
        assert "task" in all_handlers
        assert callable(all_handlers["profile"])
        assert callable(all_handlers["task"])
