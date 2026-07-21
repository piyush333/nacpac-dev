"""Tool registry for agent tools."""

from typing import Callable, Dict, Any, Optional
import json


class ToolRegistry:
    """Registry for self-registering tools."""

    _tools: Dict[str, Callable] = {}
    _schemas: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        func: Callable,
        description: str = "",
        input_schema: Optional[Dict] = None
    ):
        """Register a tool."""
        cls._tools[name] = func
        cls._schemas[name] = {
            "name": name,
            "description": description,
            "input_schema": input_schema or {}
        }
        print(f"✓ Registered tool: {name}")

    @classmethod
    def get_tool(cls, name: str) -> Optional[Callable]:
        """Get a tool by name."""
        return cls._tools.get(name)

    @classmethod
    def get_all_tools(cls) -> Dict[str, Callable]:
        """Get all registered tools."""
        return cls._tools.copy()

    @classmethod
    def get_tool_schemas(cls) -> Dict[str, Dict]:
        """Get schemas for all tools (for Claude)."""
        return cls._schemas.copy()

    @classmethod
    def call_tool(cls, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool = cls.get_tool(name)
        if not tool:
            return {"success": False, "error": f"Tool not found: {name}"}

        try:
            result = tool(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def get_tools_for_claude(cls) -> list:
        """Get tools in Claude API format."""
        tools = []
        for name, schema in cls._schemas.items():
            tools.append({
                "name": name,
                "description": schema["description"],
                "input_schema": {
                    "type": "object",
                    "properties": schema["input_schema"].get("properties", {}),
                    "required": schema["input_schema"].get("required", [])
                }
            })
        return tools
