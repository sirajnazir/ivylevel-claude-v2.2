"""
Tests for Tool Patterns (D1, D2, D3, D4, D7)

Pattern: D1 (Registry), D2 (Calling), D3 (Schema), D4 (Parallel), D7 (Chaining)
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.tools.registry_v9 import ToolRegistry, ToolDefinition
from middleware.tools.calling_v9 import ToolCaller, ToolCallResult
from middleware.tools.schema_v9 import SchemaGenerator
from middleware.tools.parallel_v9 import ParallelToolExecutor, ParallelExecutionResult
from middleware.tools.chaining_v9 import ToolChainer, ChainStep, ChainResult


# ============= D1: Tool Registry Tests =============

class TestToolRegistry:
    """Tests for D1: Tool Registry."""

    @pytest.fixture
    def registry(self):
        return ToolRegistry()

    def test_is_available(self, registry):
        """Test registry is always available."""
        assert registry.is_available is True

    def test_register_tool(self, registry):
        """Test registering a tool."""
        result = registry.register(
            name="test_tool",
            description="A test tool",
            parameters={"input": {"type": "string"}},
        )

        assert result is True
        assert registry.get("test_tool") is not None

    def test_register_with_handler(self, registry):
        """Test registering a tool with handler."""
        def my_handler(x: int) -> int:
            return x * 2

        registry.register(
            name="double",
            description="Double a number",
            handler=my_handler,
        )

        tool = registry.get("double")
        assert tool.handler is not None

    def test_unregister_tool(self, registry):
        """Test unregistering a tool."""
        registry.register(name="temp", description="Temporary")

        result = registry.unregister("temp")

        assert result is True
        assert registry.get("temp") is None

    def test_list_tools(self, registry):
        """Test listing all tools."""
        registry.register(name="tool1", description="Tool 1")
        registry.register(name="tool2", description="Tool 2")

        tools = registry.list_tools()

        assert len(tools) == 2

    def test_list_by_category(self, registry):
        """Test listing tools by category."""
        registry.register(name="math1", description="Math", category="math")
        registry.register(name="text1", description="Text", category="text")

        math_tools = registry.list_tools(category="math")

        assert len(math_tools) == 1
        assert math_tools[0].category == "math"

    def test_enable_disable(self, registry):
        """Test enabling/disabling tools."""
        registry.register(name="toggle", description="Toggle me")

        registry.disable("toggle")
        assert registry.get("toggle").enabled is False

        registry.enable("toggle")
        assert registry.get("toggle").enabled is True

    def test_get_schema(self, registry):
        """Test getting OpenAI schema for a tool."""
        registry.register(
            name="add",
            description="Add two numbers",
            parameters={
                "a": {"type": "integer", "required": True},
                "b": {"type": "integer", "required": True},
            },
        )

        schema = registry.get_schema("add")

        assert schema["name"] == "add"
        assert "parameters" in schema

    def test_count(self, registry):
        """Test counting tools."""
        registry.register(name="t1", description="T1")
        registry.register(name="t2", description="T2")

        assert registry.count() == 2


# ============= D2: Tool Calling Tests =============

class TestToolCaller:
    """Tests for D2: Tool Calling."""

    @pytest.fixture
    def mock_registry(self):
        """Mock registry with a test tool."""
        registry = MagicMock()

        def sync_handler(x: int) -> int:
            return x * 2

        async def async_handler(x: int) -> int:
            return x * 3

        tool = ToolDefinition(
            name="double",
            description="Double a number",
            handler=sync_handler,
            enabled=True,
        )

        async_tool = ToolDefinition(
            name="triple",
            description="Triple a number",
            handler=async_handler,
            enabled=True,
        )

        disabled_tool = ToolDefinition(
            name="disabled",
            description="Disabled tool",
            handler=sync_handler,
            enabled=False,
        )

        def get_tool(name):
            tools = {"double": tool, "triple": async_tool, "disabled": disabled_tool}
            return tools.get(name)

        registry.get = get_tool
        return registry

    @pytest.fixture
    def caller(self, mock_registry):
        return ToolCaller(registry=mock_registry)

    @pytest.fixture
    def caller_no_registry(self):
        return ToolCaller(registry=None)

    def test_is_available_with_registry(self, caller):
        """Test availability with registry."""
        assert caller.is_available is True

    def test_is_available_without_registry(self, caller_no_registry):
        """Test availability without registry."""
        assert caller_no_registry.is_available is False

    @pytest.mark.asyncio
    async def test_call_sync_tool(self, caller):
        """Test calling a synchronous tool."""
        result = await caller.call("double", {"x": 5})

        assert result.success is True
        assert result.result == 10

    @pytest.mark.asyncio
    async def test_call_async_tool(self, caller):
        """Test calling an async tool."""
        result = await caller.call("triple", {"x": 5})

        assert result.success is True
        assert result.result == 15

    @pytest.mark.asyncio
    async def test_call_with_json_arguments(self, caller):
        """Test calling with JSON string arguments."""
        result = await caller.call("double", '{"x": 7}')

        assert result.success is True
        assert result.result == 14

    @pytest.mark.asyncio
    async def test_call_unknown_tool(self, caller):
        """Test calling unknown tool."""
        result = await caller.call("unknown", {})

        assert result.success is False
        assert "not found" in result.error

    @pytest.mark.asyncio
    async def test_call_disabled_tool(self, caller):
        """Test calling disabled tool."""
        result = await caller.call("disabled", {"x": 5})

        assert result.success is False
        assert "disabled" in result.error

    @pytest.mark.asyncio
    async def test_format_result_for_llm(self, caller):
        """Test formatting result for LLM."""
        result = ToolCallResult(
            tool_name="test",
            success=True,
            result={"key": "value"},
        )

        formatted = caller.format_result_for_llm(result)

        assert formatted["role"] == "function"
        assert formatted["name"] == "test"


# ============= D3: Schema Generation Tests =============

class TestSchemaGenerator:
    """Tests for D3: Schema Generation."""

    @pytest.fixture
    def generator(self):
        return SchemaGenerator()

    def test_is_available(self, generator):
        """Test generator is always available."""
        assert generator.is_available is True

    def test_from_function(self, generator):
        """Test generating schema from function."""
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        schema = generator.from_function(add)

        assert schema["name"] == "add"
        assert "parameters" in schema

    def test_from_dict(self, generator):
        """Test generating schema from dictionary."""
        schema = generator.from_dict(
            name="search",
            description="Search for items",
            parameters={
                "query": {"type": "string"},
                "limit": {"type": "integer"},
            },
            required=["query"],
        )

        assert schema["name"] == "search"
        assert schema["parameters"]["required"] == ["query"]

    def test_validate_schema(self, generator):
        """Test schema validation."""
        valid_schema = {
            "name": "test",
            "description": "Test function",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        }

        assert generator.validate_schema(valid_schema) is True

    def test_validate_invalid_schema(self, generator):
        """Test invalid schema validation."""
        invalid_schema = {"name": "test"}  # Missing required fields

        assert generator.validate_schema(invalid_schema) is False

    def test_merge_schemas(self, generator):
        """Test merging schemas by name."""
        schemas = [
            {"name": "a", "description": "A"},
            {"name": "b", "description": "B"},
            {"name": "a", "description": "A duplicate"},  # Duplicate
        ]

        merged = generator.merge_schemas(schemas)

        assert len(merged) == 2


# ============= D4: Parallel Execution Tests =============

class TestParallelToolExecutor:
    """Tests for D4: Parallel Tool Execution."""

    @pytest.fixture
    def mock_caller(self):
        """Mock tool caller."""
        caller = MagicMock()

        async def mock_call(call):
            return ToolCallResult(
                tool_name=call.get("name", "unknown"),
                success=True,
                result=f"result_{call.get('name')}",
                execution_time_ms=10,
            )

        caller.call_from_response = mock_call
        return caller

    @pytest.fixture
    def executor(self, mock_caller):
        return ParallelToolExecutor(tool_caller=mock_caller)

    @pytest.fixture
    def executor_no_caller(self):
        return ParallelToolExecutor(tool_caller=None)

    def test_is_available_with_caller(self, executor):
        """Test availability with caller."""
        assert executor.is_available is True

    def test_is_available_without_caller(self, executor_no_caller):
        """Test availability without caller."""
        assert executor_no_caller.is_available is False

    @pytest.mark.asyncio
    async def test_execute_multiple_tools(self, executor):
        """Test executing multiple tools in parallel."""
        tool_calls = [
            {"name": "tool1", "arguments": "{}"},
            {"name": "tool2", "arguments": "{}"},
            {"name": "tool3", "arguments": "{}"},
        ]

        result = await executor.execute(tool_calls)

        assert result.total_tools == 3
        assert result.successful == 3
        assert len(result.results) == 3

    @pytest.mark.asyncio
    async def test_execute_empty_list(self, executor):
        """Test executing empty list."""
        result = await executor.execute([])

        assert result.total_tools == 0
        assert result.successful == 0

    @pytest.mark.asyncio
    async def test_execute_graceful_degradation(self, executor_no_caller):
        """Test graceful degradation without caller."""
        result = await executor_no_caller.execute([{"name": "test"}])

        assert len(result.errors) > 0

    def test_set_concurrency(self, executor):
        """Test setting concurrency limit."""
        executor.set_concurrency(10)
        assert executor.max_concurrency == 10

    def test_set_timeout(self, executor):
        """Test setting timeout."""
        executor.set_timeout(60.0)
        assert executor.timeout == 60.0


# ============= D7: Tool Chaining Tests =============

class TestToolChainer:
    """Tests for D7: Tool Chaining."""

    @pytest.fixture
    def mock_caller(self):
        """Mock tool caller for chaining."""
        caller = MagicMock()

        async def mock_call(tool_name, arguments):
            # Return different results based on tool
            results = {
                "fetch": {"data": "fetched_data"},
                "process": {"processed": arguments.get("input", "")},
                "save": {"saved": True},
            }
            return ToolCallResult(
                tool_name=tool_name,
                success=True,
                result=results.get(tool_name, {"result": "ok"}),
            )

        caller.call = mock_call
        return caller

    @pytest.fixture
    def chainer(self, mock_caller):
        return ToolChainer(tool_caller=mock_caller)

    @pytest.fixture
    def chainer_no_caller(self):
        return ToolChainer(tool_caller=None)

    def test_is_available_with_caller(self, chainer):
        """Test availability with caller."""
        assert chainer.is_available is True

    def test_is_available_without_caller(self, chainer_no_caller):
        """Test availability without caller."""
        assert chainer_no_caller.is_available is False

    @pytest.mark.asyncio
    async def test_execute_simple_chain(self, chainer):
        """Test executing a simple chain."""
        steps = [
            ChainStep(tool_name="fetch", output_key="fetched"),
            ChainStep(
                tool_name="process",
                arguments={},
                input_mapping={"input": "fetched"},
                output_key="processed",
            ),
        ]

        result = await chainer.execute_chain(steps)

        assert result.success is True
        assert result.steps_completed == 2

    @pytest.mark.asyncio
    async def test_execute_with_initial_context(self, chainer):
        """Test executing chain with initial context."""
        steps = [
            ChainStep(
                tool_name="process",
                input_mapping={"input": "initial_value"},
            ),
        ]

        result = await chainer.execute_chain(
            steps,
            initial_context={"initial_value": "hello"},
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_with_condition(self, chainer):
        """Test conditional step execution."""
        steps = [
            ChainStep(
                tool_name="save",
                condition="should_save:truthy",
            ),
        ]

        # Without the condition met
        result = await chainer.execute_chain(
            steps,
            initial_context={"should_save": False},
        )

        # Step should be skipped
        assert result.steps_completed == 0

    @pytest.mark.asyncio
    async def test_create_chain_helper(self, chainer):
        """Test create_chain helper method."""
        steps = chainer.create_chain(
            {"tool_name": "fetch", "output_key": "data"},
            {"tool_name": "process"},
        )

        assert len(steps) == 2
        assert all(isinstance(s, ChainStep) for s in steps)

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, chainer_no_caller):
        """Test graceful degradation without caller."""
        steps = [ChainStep(tool_name="test")]

        result = await chainer_no_caller.execute_chain(steps)

        assert result.success is False
        assert len(result.errors) > 0


class TestChainResult:
    """Tests for ChainResult model."""

    def test_default_values(self):
        """Test default values."""
        result = ChainResult()

        assert result.success is True
        assert result.steps_completed == 0
        assert result.outputs == {}

    def test_custom_values(self):
        """Test custom values."""
        result = ChainResult(
            success=False,
            steps_completed=2,
            total_steps=3,
            errors=["Step 3 failed"],
        )

        assert result.success is False
        assert result.steps_completed == 2
        assert len(result.errors) == 1


# Run with: pytest tests/phase3/test_tools.py -v
