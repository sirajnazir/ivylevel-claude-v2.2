"""
Tool Registry - Central registry for available tools.

Pattern: D1
3P: Supabase (optional persistence)
Lines: ~100 (thin wrapper)

Features:
- Register/unregister tools
- Get tool by name
- List available tools
- Tool metadata and schemas
- Graceful degradation
"""

from typing import Optional, List, Dict, Any, Callable
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """A registered tool definition."""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    returns: Optional[str] = None
    category: str = "general"
    enabled: bool = True
    handler: Optional[Callable] = None

    class Config:
        arbitrary_types_allowed = True


class ToolRegistry:
    """
    Central registry for available tools.

    Pattern D1: Tool Registry
    3P: In-memory (with optional Supabase persistence)

    Manages tool registration, discovery, and metadata.
    """

    TABLE = "phase3_tool_registry"

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._tools: Dict[str, ToolDefinition] = {}
        self._initialized = True  # Always available (in-memory)

    @property
    def is_available(self) -> bool:
        return self._initialized

    def register(
        self,
        name: str,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        returns: Optional[str] = None,
        category: str = "general",
        handler: Optional[Callable] = None,
    ) -> bool:
        """Register a tool."""
        try:
            tool = ToolDefinition(
                name=name,
                description=description,
                parameters=parameters or {},
                returns=returns,
                category=category,
                handler=handler,
            )
            self._tools[name] = tool

            # Persist to Supabase if available
            if self.supabase:
                try:
                    self.supabase.table(self.TABLE).upsert({
                        "name": name,
                        "description": description,
                        "parameters": parameters or {},
                        "returns": returns,
                        "category": category,
                        "enabled": True,
                        "updated_at": datetime.utcnow().isoformat(),
                    }).execute()
                except Exception as e:
                    logger.warning(f"Failed to persist tool registration: {e}")

            return True
        except Exception as e:
            logger.error(f"Failed to register tool {name}: {e}")
            return False

    def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]

            # Remove from Supabase if available
            if self.supabase:
                try:
                    self.supabase.table(self.TABLE).delete().eq(
                        "name", name
                    ).execute()
                except Exception as e:
                    logger.warning(f"Failed to remove tool from persistence: {e}")

            return True
        return False

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(
        self,
        category: Optional[str] = None,
        enabled_only: bool = True,
    ) -> List[ToolDefinition]:
        """List all registered tools."""
        tools = list(self._tools.values())

        if enabled_only:
            tools = [t for t in tools if t.enabled]

        if category:
            tools = [t for t in tools if t.category == category]

        return tools

    def list_names(
        self,
        category: Optional[str] = None,
    ) -> List[str]:
        """List tool names only."""
        tools = self.list_tools(category=category)
        return [t.name for t in tools]

    def enable(self, name: str) -> bool:
        """Enable a tool."""
        if name in self._tools:
            self._tools[name].enabled = True
            return True
        return False

    def disable(self, name: str) -> bool:
        """Disable a tool."""
        if name in self._tools:
            self._tools[name].enabled = False
            return True
        return False

    def get_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get OpenAI function schema for a tool."""
        tool = self.get(name)
        if not tool:
            return None

        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": tool.parameters,
                "required": [
                    k for k, v in tool.parameters.items()
                    if v.get("required", False)
                ],
            },
        }

    def get_all_schemas(
        self,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get OpenAI function schemas for all enabled tools."""
        tools = self.list_tools(category=category)
        return [self.get_schema(t.name) for t in tools if self.get_schema(t.name)]

    def count(self, category: Optional[str] = None) -> int:
        """Count registered tools."""
        return len(self.list_tools(category=category))

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
