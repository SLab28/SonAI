"""SonAI Tool Registry — maps tool names to callable functions.
Populated by imports from backend.tools.* and backend.generation.*.
"""
from typing import Callable, Any

TOOL_REGISTRY: dict[str, Callable] = {}


def register_tool(name: str):
    """Decorator to register a tool function."""
    def wrapper(fn):
        TOOL_REGISTRY[name] = fn
        return fn
    return wrapper
