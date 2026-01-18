"""
Tool Chaining - Chain tools together with data flow.

Pattern: D7
3P: Extends A9 (Prompt Chaining pattern)
Lines: ~120 (thin wrapper)

Features:
- Chain multiple tools
- Pass outputs as inputs
- Conditional branching
- Error handling in chains
- Graceful degradation
"""

from typing import Optional, List, Dict, Any, Callable
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ChainStep(BaseModel):
    """A single step in a tool chain."""
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    output_key: str = "result"  # Key to store output under
    input_mapping: Dict[str, str] = Field(default_factory=dict)  # Map previous outputs to inputs
    condition: Optional[str] = None  # Skip if condition not met


class ChainResult(BaseModel):
    """Result of executing a tool chain."""
    success: bool = True
    steps_completed: int = 0
    total_steps: int = 0
    outputs: Dict[str, Any] = Field(default_factory=dict)
    final_result: Optional[Any] = None
    errors: List[str] = []
    total_time_ms: float = 0


class ToolChainer:
    """
    Chains tools together with data flow between them.

    Pattern D7: Tool Chaining
    3P: Extends A9 (Prompt Chaining)

    Creates pipelines of tools where outputs flow to inputs.
    """

    def __init__(self, tool_caller=None):
        self.tool_caller = tool_caller
        self._initialized = tool_caller is not None

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def execute_chain(
        self,
        steps: List[ChainStep],
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> ChainResult:
        """Execute a chain of tools."""
        start_time = datetime.utcnow()
        result = ChainResult(
            total_steps=len(steps),
            outputs=initial_context.copy() if initial_context else {},
        )

        if not self.is_available:
            result.success = False
            result.errors.append("Tool caller not available")
            return result

        for i, step in enumerate(steps):
            try:
                # Check condition
                if step.condition and not self._evaluate_condition(
                    step.condition, result.outputs
                ):
                    logger.debug(f"Skipping step {i} ({step.tool_name}): condition not met")
                    continue

                # Build arguments with input mapping
                arguments = self._build_arguments(step, result.outputs)

                # Execute the tool
                tool_result = await self.tool_caller.call(
                    tool_name=step.tool_name,
                    arguments=arguments,
                )

                if not tool_result.success:
                    result.success = False
                    result.errors.append(
                        f"Step {i} ({step.tool_name}) failed: {tool_result.error}"
                    )
                    break

                # Store output
                result.outputs[step.output_key] = tool_result.result
                result.steps_completed += 1

            except Exception as e:
                result.success = False
                result.errors.append(f"Step {i} ({step.tool_name}) exception: {e}")
                break

        # Set final result to last output
        if result.steps_completed > 0:
            last_step = steps[result.steps_completed - 1]
            result.final_result = result.outputs.get(last_step.output_key)

        result.total_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        return result

    def _build_arguments(
        self,
        step: ChainStep,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build arguments by combining static args with mapped inputs."""
        arguments = step.arguments.copy()

        # Apply input mapping
        for arg_name, context_key in step.input_mapping.items():
            if context_key in context:
                arguments[arg_name] = context[context_key]

        return arguments

    def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate a simple condition against context."""
        try:
            # Support simple conditions like "key:exists" or "key:value"
            if ":" in condition:
                key, check = condition.split(":", 1)

                if check == "exists":
                    return key in context

                if check == "truthy":
                    return bool(context.get(key))

                if check == "falsy":
                    return not bool(context.get(key))

                # Check for specific value
                return str(context.get(key)) == check

            # Just check if key exists
            return condition in context
        except Exception:
            return False

    def create_chain(
        self,
        *steps: Dict[str, Any],
    ) -> List[ChainStep]:
        """Helper to create chain from dictionaries."""
        return [ChainStep(**s) for s in steps]

    async def execute_parallel_chains(
        self,
        chains: List[List[ChainStep]],
        initial_contexts: Optional[List[Dict[str, Any]]] = None,
    ) -> List[ChainResult]:
        """Execute multiple chains in parallel (A9 pattern)."""
        import asyncio

        contexts = initial_contexts or [{}] * len(chains)

        tasks = [
            self.execute_chain(chain, context)
            for chain, context in zip(chains, contexts)
        ]

        return await asyncio.gather(*tasks)

    async def execute_conditional_chain(
        self,
        condition_check: Callable[[Dict[str, Any]], str],
        branches: Dict[str, List[ChainStep]],
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> ChainResult:
        """Execute a chain based on a condition result."""
        context = initial_context or {}

        try:
            # Determine which branch to take
            branch_name = condition_check(context)

            if branch_name not in branches:
                return ChainResult(
                    success=False,
                    errors=[f"Branch '{branch_name}' not found"],
                    outputs=context,
                )

            # Execute the selected branch
            return await self.execute_chain(
                steps=branches[branch_name],
                initial_context=context,
            )
        except Exception as e:
            return ChainResult(
                success=False,
                errors=[f"Condition check failed: {e}"],
                outputs=context,
            )
