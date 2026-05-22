"""Helper functions for reading and writing graph state"""

from typing import Any, Dict

def get_state_value(state: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from graph state"""
    return state.get(key, default)

def set_state_value(state: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    """Safely set a value in graph state"""
    state[key] = value
    return state

def merge_state(state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merge updates into state"""
    state.update(updates)
    return state

def get_nested_state(state: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get nested state value using dot notation (e.g., 'plan.phases.0.name')"""
    keys = path.split(".")
    current = state
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, list):
            try:
                current = current[int(key)]
            except (ValueError, IndexError):
                return default
        else:
            return default
    return current if current is not None else default
