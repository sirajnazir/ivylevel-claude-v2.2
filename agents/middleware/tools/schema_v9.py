"""
Function Schema Generation - Generate OpenAI function schemas.

Pattern: D3
3P: OpenAI (function schema format)
Lines: ~100 (thin wrapper)

Features:
- Generate schema from Python function
- Generate schema from Pydantic model
- Generate schema from dictionary
- Validate schema format
- Graceful degradation
"""

from typing import Optional, Dict, Any, List, Callable, Type, get_type_hints
from pydantic import BaseModel
from datetime import datetime
import logging
import inspect

logger = logging.getLogger(__name__)


# Python type to JSON schema type mapping
TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
    type(None): "null",
}


class SchemaGenerator:
    """
    Generates OpenAI function schemas from various sources.

    Pattern D3: Function Schema Generation
    3P: OpenAI (function schema format)

    Converts Python functions and Pydantic models to OpenAI schemas.
    """

    def __init__(self):
        self._initialized = True

    @property
    def is_available(self) -> bool:
        return self._initialized

    def from_function(
        self,
        func: Callable,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate schema from a Python function."""
        try:
            # Get function signature
            sig = inspect.signature(func)
            hints = get_type_hints(func) if hasattr(func, "__annotations__") else {}

            # Build parameters schema
            properties = {}
            required = []

            for name, param in sig.parameters.items():
                if name in ("self", "cls"):
                    continue

                param_type = hints.get(name, Any)
                json_type = TYPE_MAP.get(param_type, "string")

                param_schema = {"type": json_type}

                # Add description from docstring if available
                if func.__doc__:
                    param_schema["description"] = f"Parameter: {name}"

                properties[name] = param_schema

                # Required if no default value
                if param.default is inspect.Parameter.empty:
                    required.append(name)

            return {
                "name": func.__name__,
                "description": description or func.__doc__ or f"Function {func.__name__}",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
        except Exception as e:
            logger.error(f"Failed to generate schema from function: {e}")
            return {}

    def from_pydantic(
        self,
        model: Type[BaseModel],
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate schema from a Pydantic model."""
        try:
            # Get JSON schema from Pydantic
            json_schema = model.model_json_schema()

            # Extract properties and required fields
            properties = json_schema.get("properties", {})
            required = json_schema.get("required", [])

            # Clean up properties (remove Pydantic-specific fields)
            clean_properties = {}
            for prop_name, prop_schema in properties.items():
                clean_schema = {
                    "type": prop_schema.get("type", "string"),
                }
                if "description" in prop_schema:
                    clean_schema["description"] = prop_schema["description"]
                if "enum" in prop_schema:
                    clean_schema["enum"] = prop_schema["enum"]
                if "default" in prop_schema:
                    clean_schema["default"] = prop_schema["default"]

                clean_properties[prop_name] = clean_schema

            return {
                "name": name or model.__name__,
                "description": description or model.__doc__ or f"Model {model.__name__}",
                "parameters": {
                    "type": "object",
                    "properties": clean_properties,
                    "required": required,
                },
            }
        except Exception as e:
            logger.error(f"Failed to generate schema from Pydantic model: {e}")
            return {}

    def from_dict(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Dict[str, Any]],
        required: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate schema from a dictionary definition."""
        return {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required or [],
            },
        }

    def validate_schema(
        self,
        schema: Dict[str, Any],
    ) -> bool:
        """Validate that a schema is properly formatted."""
        try:
            # Required top-level fields
            if "name" not in schema:
                logger.error("Schema missing 'name' field")
                return False

            if "description" not in schema:
                logger.error("Schema missing 'description' field")
                return False

            if "parameters" not in schema:
                logger.error("Schema missing 'parameters' field")
                return False

            params = schema["parameters"]
            if params.get("type") != "object":
                logger.error("Parameters type must be 'object'")
                return False

            if "properties" not in params:
                logger.error("Parameters missing 'properties' field")
                return False

            return True
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False

    def merge_schemas(
        self,
        schemas: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Merge and deduplicate schemas by name."""
        seen = {}
        for schema in schemas:
            name = schema.get("name")
            if name and name not in seen:
                seen[name] = schema
        return list(seen.values())
