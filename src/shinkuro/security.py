"""Security utilities for input validation."""

import re
from pathlib import Path


def validate_safe_path(path: str, base_path: str | None = None) -> Path:
    """
    Validate that a path is safe and doesn't escape intended boundaries.

    Args:
        path: Path to validate
        base_path: Optional base path that the resolved path must be within

    Returns:
        Resolved Path object

    Raises:
        ValueError: If path contains unsafe patterns or escapes base_path
    """
    # Convert to Path and resolve to absolute path
    resolved = Path(path).resolve()

    # If base_path is provided, ensure resolved path is within it
    if base_path:
        base_resolved = Path(base_path).resolve()
        try:
            resolved.relative_to(base_resolved)
        except ValueError:
            raise ValueError(
                f"Path '{path}' resolves outside allowed base path '{base_path}'"
            )

    return resolved


def validate_python_identifier(name: str) -> None:
    """
    Validate that a string is a safe Python identifier.

    Args:
        name: String to validate as Python identifier

    Raises:
        ValueError: If name is not a valid identifier or is dangerous
    """
    # Must match Python identifier pattern
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
        raise ValueError(f"Invalid Python identifier: '{name}'")

    # Blacklist dangerous identifiers
    dangerous_names = {
        "__import__",
        "eval",
        "exec",
        "compile",
        "__builtins__",
        "__globals__",
        "__locals__",
        "__dict__",
        "__class__",
        "__bases__",
        "__subclasses__",
        "__init__",
        "__new__",
    }

    if name in dangerous_names:
        raise ValueError(f"Identifier '{name}' is not allowed for security reasons")

    # Prevent dunder methods
    if name.startswith("__") and name.endswith("__"):
        raise ValueError(f"Dunder methods are not allowed: '{name}'")


def validate_path_component(component: str) -> None:
    """
    Validate that a path component is safe (no traversal patterns).

    Args:
        component: Path component to validate (e.g., username or repo name)

    Raises:
        ValueError: If component contains unsafe patterns
    """
    if not component:
        raise ValueError("Path component cannot be empty")

    # Disallow path traversal patterns
    if component in (".", ".."):
        raise ValueError(f"Path component cannot be '{component}'")

    # Disallow path separators
    if "/" in component or "\\" in component:
        raise ValueError(f"Path component cannot contain separators: '{component}'")

    # Disallow null bytes
    if "\x00" in component:
        raise ValueError("Path component cannot contain null bytes")
