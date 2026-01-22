# Phase 3 Week 2: Tool Patterns Implementation Spec

## Overview

Week 2 focuses on implementing the Tool subsystem for dynamic tool registration, selection, validation, and execution.

| Pattern | ID | Priority | Dependencies |
|---------|-----|----------|--------------|
| Tool Registry | D1 | High | Supabase |
| Tool Selection | D2 | High | D1, OpenAI |
| Schema Validation | D3 | Medium | D1 |
| Tool Invocation | D4 | High | D1, D3 |
| Tool Chaining | D7 | Medium | D1, D4 |

### 3P Systems Used

| System | Purpose | Already in Use? |
|--------|---------|-----------------|
| **Supabase** | Tool registry storage | ✅ Yes |
| **OpenAI** | Tool selection via function calling | ✅ Yes |
| **Pydantic** | Schema validation | ✅ Yes |
| **LangChain Tools** | Tool abstraction (optional) | ✅ Yes |

---

## D1: Tool Registry

### Purpose
Central registry for all available tools/functions that agents can invoke. Supports dynamic registration, versioning, and categorization.

### 3P System Choice: **Supabase + Pydantic**

**Why:**
- ✅ Already using Supabase - persistent storage
- ✅ Already using Pydantic - schema validation
- ✅ JSON Schema support in Supabase (JSONB)
- ✅ No additional dependencies needed

### File: `middleware/tools/registry_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional, Callable, Type
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ToolCategory(str, Enum):
    """Categories of tools."""
    DATA_RETRIEVAL = "data_retrieval"
    DATA_MUTATION = "data_mutation"
    EXTERNAL_API = "external_api"
    COMPUTATION = "computation"
    COMMUNICATION = "communication"
    FILE_OPERATION = "file_operation"


class ToolParameter(BaseModel):
    """A parameter for a tool."""
    name: str
    type: str  # 'string', 'number', 'boolean', 'object', 'array'
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None  # For constrained values


class ToolSchema(BaseModel):
    """Schema definition for a tool."""
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    return_type: str = "object"
    return_description: str = ""
    examples: List[Dict[str, Any]] = []
    requires_approval: bool = False  # HITL gate required?
    max_retries: int = 3
    timeout_seconds: int = 30


class RegisteredTool(BaseModel):
    """A registered tool in the registry."""
    id: str
    schema: ToolSchema
    version: str = "1.0.0"
    is_active: bool = True
    usage_count: int = 0
    success_rate: float = 1.0
    avg_latency_ms: float = 0.0
    created_at: datetime
    updated_at: datetime


class ToolRegistry:
    """
    Central registry for tool management.

    Stores tool schemas in Supabase for persistence.
    Supports dynamic registration and versioning.
    """

    def __init__(self, supabase_client=None):
        """Initialize with Supabase client."""
        self.db = supabase_client
        self._cache: Dict[str, RegisteredTool] = {}  # In-memory cache
        self._handlers: Dict[str, Callable] = {}  # Tool handlers

    async def register(
        self,
        schema: ToolSchema,
        handler: Callable,
        version: str = "1.0.0",
    ) -> RegisteredTool:
        """
        Register a new tool.

        Args:
            schema: Tool schema definition
            handler: The function to call when tool is invoked
            version: Version string

        Returns:
            The registered tool
        """
        pass

    async def unregister(self, tool_name: str) -> bool:
        """Unregister a tool (soft delete)."""
        pass

    async def get(self, tool_name: str) -> Optional[RegisteredTool]:
        """Get a registered tool by name."""
        pass

    async def list_tools(
        self,
        category: Optional[ToolCategory] = None,
        active_only: bool = True,
    ) -> List[RegisteredTool]:
        """List all registered tools, optionally filtered."""
        pass

    async def get_schema_for_llm(
        self,
        tool_names: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get tool schemas in OpenAI function calling format.

        Returns:
            List of tool schemas ready for OpenAI API
        """
        pass

    def get_handler(self, tool_name: str) -> Optional[Callable]:
        """Get the handler function for a tool."""
        return self._handlers.get(tool_name)

    async def update_stats(
        self,
        tool_name: str,
        success: bool,
        latency_ms: float,
    ) -> None:
        """Update usage statistics for a tool."""
        pass

    async def refresh_cache(self) -> None:
        """Refresh the in-memory cache from database."""
        pass
```

### Database Schema

```sql
CREATE TABLE tool_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN (
        'data_retrieval', 'data_mutation', 'external_api',
        'computation', 'communication', 'file_operation'
    )),
    schema JSONB NOT NULL,  -- Full ToolSchema as JSON
    version TEXT DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    total_latency_ms BIGINT DEFAULT 0,
    requires_approval BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tool_registry_name ON tool_registry(name);
CREATE INDEX idx_tool_registry_category ON tool_registry(category);
CREATE INDEX idx_tool_registry_active ON tool_registry(is_active);
```

### Test File: `tests/phase3/test_tool_registry.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.tools.registry_v9 import (
    ToolRegistry,
    ToolSchema,
    ToolParameter,
    ToolCategory,
    RegisteredTool,
)


class TestToolRegistry:
    """Tests for D1: Tool Registry."""

    @pytest.fixture
    def mock_supabase(self):
        db = MagicMock()
        db.table = MagicMock(return_value=MagicMock(
            insert=MagicMock(return_value=MagicMock(
                execute=MagicMock(return_value=MagicMock(data=[{"id": "test-id"}]))
            )),
            select=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    execute=MagicMock(return_value=MagicMock(data=[]))
                ))
            )),
            update=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    execute=MagicMock(return_value=MagicMock(data=[]))
                ))
            ))
        ))
        return db

    @pytest.fixture
    def registry(self, mock_supabase):
        return ToolRegistry(supabase_client=mock_supabase)

    @pytest.fixture
    def sample_schema(self):
        return ToolSchema(
            name="get_profile",
            description="Retrieve a student profile",
            category=ToolCategory.DATA_RETRIEVAL,
            parameters=[
                ToolParameter(
                    name="profile_id",
                    type="string",
                    description="The profile UUID",
                    required=True,
                )
            ],
        )

    @pytest.mark.asyncio
    async def test_register_creates_tool(self, registry, sample_schema):
        """Test registering a new tool."""
        async def handler(profile_id: str):
            return {"id": profile_id}

        tool = await registry.register(
            schema=sample_schema,
            handler=handler,
        )

        assert tool is not None
        assert tool.schema.name == "get_profile"

    @pytest.mark.asyncio
    async def test_get_returns_registered_tool(self, registry):
        """Test getting a registered tool."""
        tool = await registry.get("get_profile")
        # Returns None if not found
        assert tool is None or isinstance(tool, RegisteredTool)

    @pytest.mark.asyncio
    async def test_list_tools_filters_by_category(self, registry):
        """Test listing tools by category."""
        tools = await registry.list_tools(
            category=ToolCategory.DATA_RETRIEVAL,
        )

        assert isinstance(tools, list)

    @pytest.mark.asyncio
    async def test_get_schema_for_llm_returns_openai_format(self, registry):
        """Test schema conversion to OpenAI format."""
        schemas = await registry.get_schema_for_llm()

        assert isinstance(schemas, list)
        for schema in schemas:
            assert "name" in schema
            assert "description" in schema

    @pytest.mark.asyncio
    async def test_unregister_soft_deletes(self, registry):
        """Test unregistering deactivates tool."""
        result = await registry.unregister("get_profile")

        assert result in [True, False]

    @pytest.mark.asyncio
    async def test_update_stats_tracks_usage(self, registry):
        """Test usage statistics tracking."""
        await registry.update_stats(
            tool_name="get_profile",
            success=True,
            latency_ms=150.0,
        )
        # Should not raise
```

---

## D2: Tool Selection

### Purpose
LLM-based selection of appropriate tools for a given task. Uses OpenAI function calling for reliable tool selection.

### 3P System Choice: **OpenAI Function Calling**

**Why:**
- ✅ Already using OpenAI - no new vendor
- ✅ Native function calling support - reliable JSON output
- ✅ Parallel tool calling support
- ✅ Better than prompting for tool selection

### File: `middleware/tools/selection_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from .registry_v9 import ToolRegistry, RegisteredTool

logger = logging.getLogger(__name__)


class ToolSelectionResult(BaseModel):
    """Result of tool selection."""
    selected_tools: List[str]
    tool_calls: List[Dict[str, Any]]  # OpenAI format tool calls
    reasoning: str
    confidence: float


class ToolSelector:
    """
    Selects appropriate tools for a task using OpenAI function calling.

    Uses the tool registry to get available tools, then lets
    OpenAI select which tools to call based on the user's request.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        openai_client=None,
        model: str = "gpt-4o-mini",
    ):
        """
        Initialize tool selector.

        Args:
            registry: Tool registry to get available tools
            openai_client: OpenAI client (already in use)
            model: Model to use for selection
        """
        self.registry = registry
        self.openai = openai_client
        self.model = model

    async def select(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None,
        available_categories: Optional[List[str]] = None,
        max_tools: int = 5,
    ) -> ToolSelectionResult:
        """
        Select tools for a user request.

        Uses OpenAI function calling to determine which tools
        are needed and with what arguments.

        Args:
            user_request: The user's request/task
            context: Additional context (profile data, etc.)
            available_categories: Limit to specific categories
            max_tools: Maximum tools to select

        Returns:
            ToolSelectionResult with selected tools and calls
        """
        pass

    async def select_with_plan(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ToolSelectionResult]:
        """
        Select tools with execution plan for complex tasks.

        Returns ordered list of tool selections for multi-step tasks.
        """
        pass

    def _build_system_prompt(
        self,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build system prompt for tool selection."""
        pass
```

### Test File: `tests/phase3/test_tool_selection.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.tools.selection_v9 import (
    ToolSelector,
    ToolSelectionResult,
)
from middleware.tools.registry_v9 import ToolRegistry


class TestToolSelector:
    """Tests for D2: Tool Selection."""

    @pytest.fixture
    def mock_registry(self):
        registry = MagicMock(spec=ToolRegistry)
        registry.get_schema_for_llm = AsyncMock(return_value=[
            {
                "name": "get_profile",
                "description": "Get student profile",
                "parameters": {"type": "object", "properties": {}},
            }
        ])
        return registry

    @pytest.fixture
    def mock_openai(self):
        client = MagicMock()
        client.chat = MagicMock()
        client.chat.completions = MagicMock()
        client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    tool_calls=[MagicMock(
                        function=MagicMock(
                            name="get_profile",
                            arguments='{"profile_id": "123"}'
                        )
                    )]
                )
            )]
        ))
        return client

    @pytest.fixture
    def selector(self, mock_registry, mock_openai):
        return ToolSelector(
            registry=mock_registry,
            openai_client=mock_openai,
        )

    @pytest.mark.asyncio
    async def test_select_returns_tools(self, selector):
        """Test basic tool selection."""
        result = await selector.select(
            user_request="Get my profile information",
        )

        assert isinstance(result, ToolSelectionResult)
        assert len(result.selected_tools) >= 0

    @pytest.mark.asyncio
    async def test_select_respects_max_tools(self, selector):
        """Test max_tools limit is respected."""
        result = await selector.select(
            user_request="Do many things",
            max_tools=2,
        )

        assert len(result.selected_tools) <= 2

    @pytest.mark.asyncio
    async def test_select_with_plan_returns_ordered_steps(self, selector):
        """Test multi-step tool selection."""
        results = await selector.select_with_plan(
            user_request="First get profile, then update it",
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_select_filters_by_category(self, selector):
        """Test category filtering."""
        result = await selector.select(
            user_request="Get data",
            available_categories=["data_retrieval"],
        )

        assert isinstance(result, ToolSelectionResult)
```

---

## D3: Schema Validation

### Purpose
Validates tool inputs and outputs against defined schemas before execution.

### 3P System Choice: **Pydantic**

**Why:**
- ✅ Already using Pydantic - no new dependency
- ✅ Native JSON Schema support
- ✅ Excellent error messages
- ✅ Type coercion built-in

### File: `middleware/tools/validation_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, ValidationError, create_model
import logging

from .registry_v9 import ToolSchema, ToolParameter

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """Result of schema validation."""
    valid: bool
    errors: List[str] = []
    coerced_data: Optional[Dict[str, Any]] = None


class SchemaValidator:
    """
    Validates tool inputs and outputs using Pydantic.

    Converts ToolSchema to Pydantic models for validation.
    Supports type coercion and detailed error messages.
    """

    def __init__(self):
        """Initialize validator."""
        self._model_cache: Dict[str, Type[BaseModel]] = {}

    def validate_input(
        self,
        schema: ToolSchema,
        input_data: Dict[str, Any],
    ) -> ValidationResult:
        """
        Validate input data against tool schema.

        Args:
            schema: The tool's schema
            input_data: Input data to validate

        Returns:
            ValidationResult with validity and any errors
        """
        pass

    def validate_output(
        self,
        schema: ToolSchema,
        output_data: Any,
    ) -> ValidationResult:
        """Validate output data against tool's return type."""
        pass

    def coerce_types(
        self,
        schema: ToolSchema,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Attempt to coerce input types to match schema.

        e.g., "123" -> 123 for integer fields
        """
        pass

    def _schema_to_pydantic(
        self,
        schema: ToolSchema,
    ) -> Type[BaseModel]:
        """Convert ToolSchema to Pydantic model."""
        pass

    def _parameter_to_field(
        self,
        param: ToolParameter,
    ) -> tuple:
        """Convert ToolParameter to Pydantic field."""
        pass
```

### Test File: `tests/phase3/test_schema_validation.py`

```python
import pytest
from middleware.tools.validation_v9 import (
    SchemaValidator,
    ValidationResult,
)
from middleware.tools.registry_v9 import (
    ToolSchema,
    ToolParameter,
    ToolCategory,
)


class TestSchemaValidator:
    """Tests for D3: Schema Validation."""

    @pytest.fixture
    def validator(self):
        return SchemaValidator()

    @pytest.fixture
    def sample_schema(self):
        return ToolSchema(
            name="test_tool",
            description="Test tool",
            category=ToolCategory.COMPUTATION,
            parameters=[
                ToolParameter(
                    name="count",
                    type="number",
                    description="A count",
                    required=True,
                ),
                ToolParameter(
                    name="name",
                    type="string",
                    description="A name",
                    required=False,
                    default="default",
                ),
            ],
        )

    def test_validate_input_accepts_valid_data(self, validator, sample_schema):
        """Test valid input passes validation."""
        result = validator.validate_input(
            schema=sample_schema,
            input_data={"count": 5, "name": "test"},
        )

        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_input_rejects_missing_required(self, validator, sample_schema):
        """Test missing required field fails validation."""
        result = validator.validate_input(
            schema=sample_schema,
            input_data={"name": "test"},  # missing count
        )

        assert result.valid is False
        assert len(result.errors) > 0

    def test_validate_input_uses_defaults(self, validator, sample_schema):
        """Test default values are applied."""
        result = validator.validate_input(
            schema=sample_schema,
            input_data={"count": 5},  # name uses default
        )

        assert result.valid is True
        assert result.coerced_data.get("name") == "default"

    def test_coerce_types_converts_strings(self, validator, sample_schema):
        """Test type coercion for string numbers."""
        coerced = validator.coerce_types(
            schema=sample_schema,
            input_data={"count": "5"},  # string instead of number
        )

        assert coerced["count"] == 5

    def test_validate_input_rejects_wrong_type(self, validator, sample_schema):
        """Test wrong type fails validation."""
        result = validator.validate_input(
            schema=sample_schema,
            input_data={"count": "not a number"},
        )

        assert result.valid is False
```

---

## D4: Tool Invocation

### Purpose
Executes registered tools with proper error handling, timeouts, and retry logic.

### 3P System Choice: **Tenacity + asyncio**

**Why:**
- ✅ Already using Tenacity - retry logic
- ✅ asyncio built-in - timeouts and async execution
- ✅ No additional dependencies

### File: `middleware/tools/invocation_v9.py`

### Interface

```python
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pydantic import BaseModel
import logging
import asyncio

from .registry_v9 import ToolRegistry, RegisteredTool
from .validation_v9 import SchemaValidator

logger = logging.getLogger(__name__)


class InvocationResult(BaseModel):
    """Result of tool invocation."""
    tool_name: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    latency_ms: float
    retries_used: int = 0


class ToolInvoker:
    """
    Executes registered tools with proper error handling.

    Features:
    - Input validation before execution
    - Timeout handling
    - Retry logic (via Tenacity)
    - Statistics tracking
    """

    def __init__(
        self,
        registry: ToolRegistry,
        validator: SchemaValidator,
    ):
        """
        Initialize invoker.

        Args:
            registry: Tool registry to get handlers
            validator: Schema validator for inputs
        """
        self.registry = registry
        self.validator = validator

    async def invoke(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout_override: Optional[int] = None,
    ) -> InvocationResult:
        """
        Invoke a registered tool.

        1. Validate arguments against schema
        2. Get handler from registry
        3. Execute with timeout and retry
        4. Update statistics

        Args:
            tool_name: Name of the tool to invoke
            arguments: Arguments for the tool
            timeout_override: Override default timeout (seconds)

        Returns:
            InvocationResult with success/failure and result
        """
        pass

    async def invoke_batch(
        self,
        invocations: List[Dict[str, Any]],
        parallel: bool = True,
    ) -> List[InvocationResult]:
        """
        Invoke multiple tools.

        Args:
            invocations: List of {"tool_name": str, "arguments": dict}
            parallel: Execute in parallel if True

        Returns:
            List of results in same order
        """
        pass

    async def _execute_with_retry(
        self,
        handler: Callable,
        arguments: Dict[str, Any],
        max_retries: int,
        timeout: int,
    ) -> tuple:
        """Execute handler with retry logic."""
        pass
```

### Test File: `tests/phase3/test_tool_invocation.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.tools.invocation_v9 import (
    ToolInvoker,
    InvocationResult,
)
from middleware.tools.registry_v9 import ToolRegistry
from middleware.tools.validation_v9 import SchemaValidator, ValidationResult


class TestToolInvoker:
    """Tests for D4: Tool Invocation."""

    @pytest.fixture
    def mock_registry(self):
        registry = MagicMock(spec=ToolRegistry)
        registry.get = AsyncMock(return_value=MagicMock(
            schema=MagicMock(
                max_retries=3,
                timeout_seconds=30,
            )
        ))
        registry.get_handler = MagicMock(return_value=AsyncMock(
            return_value={"success": True}
        ))
        registry.update_stats = AsyncMock()
        return registry

    @pytest.fixture
    def mock_validator(self):
        validator = MagicMock(spec=SchemaValidator)
        validator.validate_input = MagicMock(return_value=ValidationResult(
            valid=True,
            errors=[],
            coerced_data={"arg": "value"},
        ))
        return validator

    @pytest.fixture
    def invoker(self, mock_registry, mock_validator):
        return ToolInvoker(
            registry=mock_registry,
            validator=mock_validator,
        )

    @pytest.mark.asyncio
    async def test_invoke_returns_result(self, invoker):
        """Test successful invocation."""
        result = await invoker.invoke(
            tool_name="test_tool",
            arguments={"arg": "value"},
        )

        assert isinstance(result, InvocationResult)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_invoke_validates_input(self, invoker, mock_validator):
        """Test input is validated before execution."""
        await invoker.invoke(
            tool_name="test_tool",
            arguments={"arg": "value"},
        )

        mock_validator.validate_input.assert_called()

    @pytest.mark.asyncio
    async def test_invoke_rejects_invalid_input(self, invoker, mock_validator):
        """Test invalid input fails invocation."""
        mock_validator.validate_input.return_value = ValidationResult(
            valid=False,
            errors=["Missing required field"],
        )

        result = await invoker.invoke(
            tool_name="test_tool",
            arguments={},
        )

        assert result.success is False
        assert "Missing required field" in result.error

    @pytest.mark.asyncio
    async def test_invoke_respects_timeout(self, invoker, mock_registry):
        """Test timeout is enforced."""
        async def slow_handler(**kwargs):
            await asyncio.sleep(10)
            return {}

        mock_registry.get_handler.return_value = slow_handler

        result = await invoker.invoke(
            tool_name="test_tool",
            arguments={},
            timeout_override=1,  # 1 second timeout
        )

        assert result.success is False
        assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_invoke_batch_parallel(self, invoker):
        """Test parallel batch invocation."""
        results = await invoker.invoke_batch(
            invocations=[
                {"tool_name": "tool1", "arguments": {}},
                {"tool_name": "tool2", "arguments": {}},
            ],
            parallel=True,
        )

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_invoke_updates_stats(self, invoker, mock_registry):
        """Test statistics are updated after invocation."""
        await invoker.invoke(
            tool_name="test_tool",
            arguments={},
        )

        mock_registry.update_stats.assert_called()
```

---

## D7: Tool Chaining

### Purpose
Chains multiple tools together, passing output of one tool as input to the next.

### 3P System Choice: **LangChain RunnableSequence** (Optional)

**Why:**
- ✅ Already using LangChain - familiar pattern
- ✅ Built-in error handling and retries
- ✅ Supports async execution
- Alternative: Custom implementation (simpler, fewer dependencies)

**Recommendation:** Start with custom implementation, migrate to LangChain if needed.

### File: `middleware/tools/chaining_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel
import logging

from .registry_v9 import ToolRegistry
from .invocation_v9 import ToolInvoker, InvocationResult

logger = logging.getLogger(__name__)


class ChainStep(BaseModel):
    """A step in a tool chain."""
    tool_name: str
    arguments: Dict[str, Any] = {}
    output_key: str = "result"  # Key to store output for next step
    condition: Optional[str] = None  # Optional condition to continue


class ChainResult(BaseModel):
    """Result of chain execution."""
    success: bool
    steps_completed: int
    total_steps: int
    final_result: Optional[Any] = None
    step_results: List[InvocationResult] = []
    error: Optional[str] = None
    total_latency_ms: float = 0.0


class ToolChain:
    """
    Chains multiple tools together with data flow.

    Supports:
    - Sequential execution
    - Data passing between steps
    - Conditional execution
    - Error handling and rollback
    """

    def __init__(
        self,
        invoker: ToolInvoker,
    ):
        """
        Initialize tool chain.

        Args:
            invoker: Tool invoker for executing individual tools
        """
        self.invoker = invoker

    async def execute(
        self,
        steps: List[ChainStep],
        initial_context: Optional[Dict[str, Any]] = None,
        stop_on_error: bool = True,
    ) -> ChainResult:
        """
        Execute a chain of tools.

        Each step can access outputs from previous steps via context.

        Args:
            steps: List of chain steps to execute
            initial_context: Initial context data
            stop_on_error: Stop chain on first error

        Returns:
            ChainResult with all step results
        """
        pass

    async def execute_with_rollback(
        self,
        steps: List[ChainStep],
        rollback_handlers: Dict[str, Callable],
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> ChainResult:
        """
        Execute chain with rollback on failure.

        If any step fails, rollback handlers are called in reverse order.
        """
        pass

    def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate a step condition against context."""
        pass

    def _interpolate_arguments(
        self,
        arguments: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Interpolate context values into arguments.

        e.g., {"id": "${previous_step.id}"} -> {"id": "actual-value"}
        """
        pass
```

### Test File: `tests/phase3/test_tool_chaining.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.tools.chaining_v9 import (
    ToolChain,
    ChainStep,
    ChainResult,
)
from middleware.tools.invocation_v9 import ToolInvoker, InvocationResult


class TestToolChain:
    """Tests for D7: Tool Chaining."""

    @pytest.fixture
    def mock_invoker(self):
        invoker = MagicMock(spec=ToolInvoker)
        invoker.invoke = AsyncMock(return_value=InvocationResult(
            tool_name="test",
            success=True,
            result={"id": "123"},
            latency_ms=100.0,
        ))
        return invoker

    @pytest.fixture
    def chain(self, mock_invoker):
        return ToolChain(invoker=mock_invoker)

    @pytest.mark.asyncio
    async def test_execute_runs_all_steps(self, chain):
        """Test all steps are executed."""
        steps = [
            ChainStep(tool_name="step1"),
            ChainStep(tool_name="step2"),
            ChainStep(tool_name="step3"),
        ]

        result = await chain.execute(steps)

        assert result.success is True
        assert result.steps_completed == 3

    @pytest.mark.asyncio
    async def test_execute_passes_context_between_steps(self, chain, mock_invoker):
        """Test output is available to next step."""
        steps = [
            ChainStep(tool_name="get_id", output_key="user_id"),
            ChainStep(
                tool_name="get_profile",
                arguments={"id": "${user_id}"},
            ),
        ]

        await chain.execute(steps)

        # Second call should have interpolated argument
        calls = mock_invoker.invoke.call_args_list
        assert len(calls) == 2

    @pytest.mark.asyncio
    async def test_execute_stops_on_error(self, chain, mock_invoker):
        """Test chain stops on error when configured."""
        mock_invoker.invoke.side_effect = [
            InvocationResult(tool_name="step1", success=True, result={}, latency_ms=100),
            InvocationResult(tool_name="step2", success=False, error="Failed", latency_ms=100),
            InvocationResult(tool_name="step3", success=True, result={}, latency_ms=100),
        ]

        steps = [
            ChainStep(tool_name="step1"),
            ChainStep(tool_name="step2"),
            ChainStep(tool_name="step3"),
        ]

        result = await chain.execute(steps, stop_on_error=True)

        assert result.success is False
        assert result.steps_completed == 1  # Only first step completed

    @pytest.mark.asyncio
    async def test_execute_with_condition(self, chain, mock_invoker):
        """Test conditional step execution."""
        mock_invoker.invoke.return_value = InvocationResult(
            tool_name="test",
            success=True,
            result={"status": "active"},
            latency_ms=100,
        )

        steps = [
            ChainStep(tool_name="check_status", output_key="status"),
            ChainStep(
                tool_name="activate",
                condition="${status.status} == 'inactive'",  # Won't run
            ),
        ]

        result = await chain.execute(steps)

        # activate should be skipped
        assert result.steps_completed == 1

    @pytest.mark.asyncio
    async def test_execute_with_rollback(self, chain, mock_invoker):
        """Test rollback on failure."""
        rollback_called = []

        async def rollback_step1():
            rollback_called.append("step1")

        mock_invoker.invoke.side_effect = [
            InvocationResult(tool_name="step1", success=True, result={}, latency_ms=100),
            InvocationResult(tool_name="step2", success=False, error="Failed", latency_ms=100),
        ]

        steps = [
            ChainStep(tool_name="step1"),
            ChainStep(tool_name="step2"),
        ]

        await chain.execute_with_rollback(
            steps=steps,
            rollback_handlers={"step1": rollback_step1},
        )

        assert "step1" in rollback_called
```

---

## Implementation Checklist

### D1: Tool Registry
- [ ] Create `middleware/tools/__init__.py`
- [ ] Create `middleware/tools/registry_v9.py`
- [ ] Implement `ToolRegistry` class
- [ ] Add database migration
- [ ] Create tests in `tests/phase3/test_tool_registry.py`
- [ ] Run tests and verify passing

### D3: Schema Validation
- [ ] Create `middleware/tools/validation_v9.py`
- [ ] Implement `SchemaValidator` class
- [ ] Create tests in `tests/phase3/test_schema_validation.py`
- [ ] Run tests and verify passing

### D4: Tool Invocation
- [ ] Create `middleware/tools/invocation_v9.py`
- [ ] Implement `ToolInvoker` class
- [ ] Create tests in `tests/phase3/test_tool_invocation.py`
- [ ] Run tests and verify passing

### D2: Tool Selection
- [ ] Create `middleware/tools/selection_v9.py`
- [ ] Implement `ToolSelector` class
- [ ] Create tests in `tests/phase3/test_tool_selection.py`
- [ ] Run tests and verify passing

### D7: Tool Chaining
- [ ] Create `middleware/tools/chaining_v9.py`
- [ ] Implement `ToolChain` class
- [ ] Create tests in `tests/phase3/test_tool_chaining.py`
- [ ] Run tests and verify passing

### Integration
- [ ] Add all tool patterns to `stack_v9.py`
- [ ] Register IvyLevel tools (profile retrieval, etc.)
- [ ] Create integration tests

---

*Phase 3 Week 2 Specification*
*Generated: 2026-01-17*
