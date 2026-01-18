"""
Tool Calling - Execute tools from LLM function calls.

Pattern: D2
3P: OpenAI (function calling)
Lines: ~100 (thin wrapper)

Features:
- Execute tool from function call response
- Validate parameters
- Handle errors gracefully
- Return formatted results
- Graceful degradation
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel
from datetime import datetime
import logging
import json
import asyncio

logger = logging.getLogger(__name__)


class ToolCallResult(BaseModel):
    """Result of a tool call."""
    tool_name: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0


class ToolCaller:
    """
    Executes tools from LLM function calls.

    Pattern D2: Tool Calling
    3P: OpenAI (function calling format)

    Bridges LLM function calls to actual tool execution.
    """

    def __init__(self, registry=None):
        self.registry = registry
        self._initialized = registry is not None

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def call(
        self,
        tool_name: str,
        arguments: Union[str, Dict[str, Any]],
    ) -> ToolCallResult:
        """Execute a single tool call."""
        start_time = datetime.utcnow()

        if not self.is_available:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                error="Tool registry not available",
            )

        # Get tool definition
        tool = self.registry.get(tool_name)
        if not tool:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' not found",
            )

        if not tool.enabled:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' is disabled",
            )

        if not tool.handler:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' has no handler",
            )

        # Parse arguments if string
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError as e:
                return ToolCallResult(
                    tool_name=tool_name,
                    success=False,
                    error=f"Invalid arguments JSON: {e}",
                )

        try:
            # Execute the tool handler
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**arguments)
            else:
                result = tool.handler(**arguments)

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return ToolCallResult(
                tool_name=tool_name,
                success=True,
                result=result,
                execution_time_ms=execution_time,
            )
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error(f"Tool execution failed for {tool_name}: {e}")

            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
            )

    async def call_from_response(
        self,
        function_call: Dict[str, Any],
    ) -> ToolCallResult:
        """Execute tool from OpenAI function call response format."""
        tool_name = function_call.get("name", "")
        arguments = function_call.get("arguments", "{}")

        return await self.call(tool_name, arguments)

    async def call_multiple(
        self,
        tool_calls: List[Dict[str, Any]],
    ) -> List[ToolCallResult]:
        """Execute multiple tool calls sequentially."""
        results = []
        for call in tool_calls:
            result = await self.call_from_response(call)
            results.append(result)
        return results

    def format_result_for_llm(
        self,
        result: ToolCallResult,
    ) -> Dict[str, Any]:
        """Format result for sending back to LLM."""
        if result.success:
            content = result.result
            if not isinstance(content, str):
                content = json.dumps(content, default=str)
        else:
            content = f"Error: {result.error}"

        return {
            "role": "function",
            "name": result.tool_name,
            "content": content,
        }

    def format_results_for_llm(
        self,
        results: List[ToolCallResult],
    ) -> List[Dict[str, Any]]:
        """Format multiple results for sending back to LLM."""
        return [self.format_result_for_llm(r) for r in results]
