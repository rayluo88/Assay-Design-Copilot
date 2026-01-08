"""
Tool Abstraction & Registry.

Defines the `BaseTool` abstract interface that all Copilot capabilities must implement.
Also provides a `ToolRegistry` for dynamic discovery and instantiation of tools.
This abstraction decouples the Agent logic from specific tool implementations.
"""
import abc
import inspect
from typing import Any, Callable, Dict, Optional, Type
from pydantic import BaseModel

class ToolMetadata(BaseModel):
    name: str
    description: str
    version: str = "1.0.0"

class BaseTool(abc.ABC):
    """Abstract base class for all tools."""
    
    def __init__(self):
        self._metadata = self.define_metadata()

    @abc.abstractmethod
    def define_metadata(self) -> ToolMetadata:
        """Returns metadata about the tool."""
        pass

    @abc.abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """The main logic of the tool."""
        pass
        
    @property
    def name(self) -> str:
        return self._metadata.name

class ToolRegistry:
    """Registry to manage and retrieve available tools."""
    
    _tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool):
        """Register a tool instance."""
        if tool.name in cls._tools:
            # warn or overwrite? Let's overwrite for now.
            pass
        cls._tools[tool.name] = tool

    @classmethod
    def get(cls, name: str) -> Optional[BaseTool]:
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> Dict[str, ToolMetadata]:
        return {name: tool._metadata for name, tool in cls._tools.items()}

# Decorator for easy registration (optional)
def register_tool(cls_or_func):
    # This can be expanded to auto-wrap functions into BaseTool
    pass
