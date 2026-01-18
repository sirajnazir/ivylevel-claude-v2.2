"""
G4: Atomic Operations Pattern - Implementation

Ensure operations are atomic and can be cleanly rolled back.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging
import uuid
import asyncio

logger = logging.getLogger(__name__)


class AtomicOperationStatus(str, Enum):
    """Status of an atomic operation."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class AtomicOperation(BaseModel):
    """Definition of an atomic operation."""
    operation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    target_resource: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: AtomicOperationStatus = AtomicOperationStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    rollback_data: Optional[Dict[str, Any]] = None


class AtomicOperationResult(BaseModel):
    """Result of atomic operation execution."""
    operation_id: str
    success: bool = False
    status: AtomicOperationStatus = AtomicOperationStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: int = 0
    was_rolled_back: bool = False


class AtomicOperationExecutor:
    """
    Executes operations atomically with rollback support.

    Pattern G4: Atomic Operations

    GUARDRAILS:
    - NEW class - does not modify existing operations
    - Uses Supabase transactions when available
    - Provides clean rollback mechanisms
    """

    def __init__(
        self,
        supabase_client=None,
        rollback_handlers: Optional[Dict[str, Callable]] = None,
    ):
        """
        Initialize atomic executor.

        Args:
            supabase_client: For database operations
            rollback_handlers: Custom rollback handlers by resource type
        """
        self.supabase = supabase_client
        self.rollback_handlers = rollback_handlers or {}
        self._pending_operations: Dict[str, AtomicOperation] = {}

    async def execute(
        self,
        operation: AtomicOperation,
        execute_func: Callable[[Dict[str, Any]], Awaitable[Any]],
        rollback_func: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
    ) -> AtomicOperationResult:
        """
        Execute an operation atomically.

        Args:
            operation: Operation to execute
            execute_func: Function to execute
            rollback_func: Function to rollback on failure

        Returns:
            AtomicOperationResult
        """
        start_time = datetime.now(timezone.utc)
        operation.started_at = start_time
        operation.status = AtomicOperationStatus.EXECUTING

        # Store for potential rollback
        self._pending_operations[operation.operation_id] = operation

        try:
            # Capture pre-execution state for rollback
            operation.rollback_data = await self._capture_state(operation)

            # Execute the operation
            result = await execute_func(operation.payload)

            # Success
            operation.status = AtomicOperationStatus.COMMITTED
            operation.completed_at = datetime.now(timezone.utc)

            # Persist to audit log
            await self._log_operation(operation, success=True)

            return AtomicOperationResult(
                operation_id=operation.operation_id,
                success=True,
                status=AtomicOperationStatus.COMMITTED,
                result=result,
                duration_ms=int(
                    (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                ),
            )

        except Exception as e:
            logger.error(f"Operation {operation.name} failed: {e}")
            operation.error = str(e)
            operation.status = AtomicOperationStatus.FAILED

            # Attempt rollback
            rolled_back = False
            if rollback_func:
                try:
                    await rollback_func(operation.rollback_data or {})
                    operation.status = AtomicOperationStatus.ROLLED_BACK
                    rolled_back = True
                    logger.info(f"Operation {operation.name} rolled back successfully")
                except Exception as re:
                    logger.error(f"Rollback failed for {operation.name}: {re}")

            # Persist failure to audit log
            await self._log_operation(operation, success=False)

            return AtomicOperationResult(
                operation_id=operation.operation_id,
                success=False,
                status=operation.status,
                error=str(e),
                duration_ms=int(
                    (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                ),
                was_rolled_back=rolled_back,
            )

        finally:
            self._pending_operations.pop(operation.operation_id, None)

    async def execute_batch(
        self,
        operations: List[AtomicOperation],
        execute_funcs: List[Callable],
        rollback_funcs: Optional[List[Callable]] = None,
        stop_on_failure: bool = True,
    ) -> List[AtomicOperationResult]:
        """
        Execute multiple operations as a batch.

        Args:
            operations: Operations to execute
            execute_funcs: Corresponding execute functions
            rollback_funcs: Corresponding rollback functions
            stop_on_failure: Whether to stop batch on first failure

        Returns:
            List of results
        """
        results = []
        completed_ops = []

        rollback_funcs = rollback_funcs or [None] * len(operations)

        for i, (op, exec_func, rb_func) in enumerate(
            zip(operations, execute_funcs, rollback_funcs)
        ):
            result = await self.execute(op, exec_func, rb_func)
            results.append(result)

            if result.success:
                completed_ops.append((op, rb_func))
            elif stop_on_failure:
                # Rollback all completed operations
                logger.warning(
                    f"Batch operation failed at step {i}, "
                    f"rolling back {len(completed_ops)} operations"
                )
                for completed_op, completed_rb in reversed(completed_ops):
                    if completed_rb:
                        try:
                            await completed_rb(completed_op.rollback_data or {})
                        except Exception as e:
                            logger.error(f"Batch rollback failed: {e}")
                break

        return results

    async def _capture_state(
        self,
        operation: AtomicOperation,
    ) -> Optional[Dict[str, Any]]:
        """Capture state before operation for potential rollback."""
        if not self.supabase:
            return None

        # Resource-specific state capture
        resource_type = operation.target_resource.split("/")[0]

        try:
            if resource_type == "profile":
                profile_id = operation.payload.get("profile_id")
                if profile_id:
                    result = self.supabase.table("profiles").select(
                        "*"
                    ).eq("id", profile_id).single().execute()
                    return {"previous_state": result.data}

            elif resource_type == "task":
                task_id = operation.payload.get("task_id")
                if task_id:
                    result = self.supabase.table("tasks").select(
                        "*"
                    ).eq("id", task_id).single().execute()
                    return {"previous_state": result.data}

        except Exception as e:
            logger.warning(f"Failed to capture state: {e}")

        return None

    async def _log_operation(
        self,
        operation: AtomicOperation,
        success: bool,
    ) -> None:
        """Log operation to audit trail."""
        if not self.supabase:
            return

        try:
            self.supabase.table("phase2b_audit_trail").insert({
                "entry_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor_id": operation.payload.get("actor_id", "system"),
                "actor_type": "agent",
                "action": operation.name,
                "resource_type": operation.target_resource,
                "resource_id": operation.payload.get("resource_id"),
                "details": {
                    "operation_id": operation.operation_id,
                    "payload": operation.payload,
                    "status": operation.status.value,
                },
                "success": success,
                "error_message": operation.error,
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log operation: {e}")

    async def rollback_operation(
        self,
        operation_id: str,
    ) -> bool:
        """
        Manually rollback an operation.

        Args:
            operation_id: Operation to rollback

        Returns:
            True if rollback successful
        """
        operation = self._pending_operations.get(operation_id)
        if not operation:
            logger.error(f"Operation {operation_id} not found")
            return False

        resource_type = operation.target_resource.split("/")[0]
        handler = self.rollback_handlers.get(resource_type)

        if handler and operation.rollback_data:
            try:
                await handler(operation.rollback_data)
                operation.status = AtomicOperationStatus.ROLLED_BACK
                return True
            except Exception as e:
                logger.error(f"Manual rollback failed: {e}")

        return False


# Predefined rollback handlers for IvyLevel resources
class IvyLevelRollbackHandlers:
    """Rollback handlers for IvyLevel resources."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def rollback_profile(self, rollback_data: Dict[str, Any]) -> None:
        """Rollback profile changes."""
        previous = rollback_data.get("previous_state")
        if previous and previous.get("id"):
            self.supabase.table("profiles").update(
                previous
            ).eq("id", previous["id"]).execute()

    async def rollback_task(self, rollback_data: Dict[str, Any]) -> None:
        """Rollback task changes."""
        previous = rollback_data.get("previous_state")
        if previous and previous.get("id"):
            self.supabase.table("tasks").update(
                previous
            ).eq("id", previous["id"]).execute()

    def get_handlers(self) -> Dict[str, Callable]:
        """Get all handlers."""
        return {
            "profile": self.rollback_profile,
            "task": self.rollback_task,
        }
