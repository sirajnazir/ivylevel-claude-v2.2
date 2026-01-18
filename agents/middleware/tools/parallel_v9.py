"""
Parallel Tool Execution - Execute multiple tools concurrently.

Pattern: D4
3P: asyncio (native Python)
Lines: ~100 (thin wrapper)

Features:
- Execute tools in parallel
- Configurable concurrency limit
- Timeout handling
- Aggregate results
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


class ParallelExecutionResult(BaseModel):
    """Result of parallel tool execution."""
    total_tools: int = 0
    successful: int = 0
    failed: int = 0
    results: List[Dict[str, Any]] = []
    total_time_ms: float = 0
    errors: List[str] = []


class ParallelToolExecutor:
    """
    Executes multiple tools in parallel.

    Pattern D4: Parallel Tool Execution
    3P: asyncio (native Python)

    Manages concurrent tool execution with limits and timeouts.
    """

    DEFAULT_CONCURRENCY = 5
    DEFAULT_TIMEOUT = 30.0  # seconds

    def __init__(
        self,
        tool_caller=None,
        max_concurrency: int = DEFAULT_CONCURRENCY,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.tool_caller = tool_caller
        self.max_concurrency = max_concurrency
        self.timeout = timeout
        self._initialized = tool_caller is not None

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def execute(
        self,
        tool_calls: List[Dict[str, Any]],
    ) -> ParallelExecutionResult:
        """Execute multiple tool calls in parallel."""
        start_time = datetime.utcnow()
        result = ParallelExecutionResult(total_tools=len(tool_calls))

        if not self.is_available:
            result.errors.append("Tool caller not available")
            return result

        if not tool_calls:
            return result

        # Create semaphore for concurrency limiting
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def execute_with_limit(call: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    tool_result = await asyncio.wait_for(
                        self.tool_caller.call_from_response(call),
                        timeout=self.timeout,
                    )
                    return {
                        "tool_name": tool_result.tool_name,
                        "success": tool_result.success,
                        "result": tool_result.result,
                        "error": tool_result.error,
                        "execution_time_ms": tool_result.execution_time_ms,
                    }
                except asyncio.TimeoutError:
                    tool_name = call.get("name", "unknown")
                    return {
                        "tool_name": tool_name,
                        "success": False,
                        "result": None,
                        "error": f"Timeout after {self.timeout}s",
                        "execution_time_ms": self.timeout * 1000,
                    }
                except Exception as e:
                    tool_name = call.get("name", "unknown")
                    return {
                        "tool_name": tool_name,
                        "success": False,
                        "result": None,
                        "error": str(e),
                        "execution_time_ms": 0,
                    }

        # Execute all tools concurrently
        tasks = [execute_with_limit(call) for call in tool_calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for r in results:
            if isinstance(r, Exception):
                result.failed += 1
                result.errors.append(str(r))
            elif isinstance(r, dict):
                result.results.append(r)
                if r.get("success"):
                    result.successful += 1
                else:
                    result.failed += 1
                    if r.get("error"):
                        result.errors.append(r["error"])

        # Calculate total time
        result.total_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return result

    async def execute_with_dependencies(
        self,
        tool_calls: List[Dict[str, Any]],
        dependencies: Optional[Dict[str, List[str]]] = None,
    ) -> ParallelExecutionResult:
        """
        Execute tools respecting dependencies.

        Dependencies format: {"tool_name": ["depends_on_1", "depends_on_2"]}
        Tools without dependencies run first.
        """
        if not dependencies:
            return await self.execute(tool_calls)

        start_time = datetime.utcnow()
        result = ParallelExecutionResult(total_tools=len(tool_calls))

        if not self.is_available:
            result.errors.append("Tool caller not available")
            return result

        # Build execution order
        tool_map = {call.get("name"): call for call in tool_calls}
        executed = set()
        all_results = []

        while len(executed) < len(tool_calls):
            # Find tools that can run (dependencies satisfied)
            ready = []
            for call in tool_calls:
                name = call.get("name")
                if name in executed:
                    continue

                deps = dependencies.get(name, [])
                if all(d in executed for d in deps):
                    ready.append(call)

            if not ready:
                # Circular dependency or missing tools
                remaining = [c.get("name") for c in tool_calls if c.get("name") not in executed]
                result.errors.append(f"Cannot resolve dependencies for: {remaining}")
                break

            # Execute ready tools in parallel
            batch_result = await self.execute(ready)
            all_results.extend(batch_result.results)
            result.successful += batch_result.successful
            result.failed += batch_result.failed
            result.errors.extend(batch_result.errors)

            # Mark as executed
            for call in ready:
                executed.add(call.get("name"))

        result.results = all_results
        result.total_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return result

    def set_concurrency(self, max_concurrency: int) -> None:
        """Update concurrency limit."""
        self.max_concurrency = max(1, max_concurrency)

    def set_timeout(self, timeout: float) -> None:
        """Update timeout."""
        self.timeout = max(1.0, timeout)
