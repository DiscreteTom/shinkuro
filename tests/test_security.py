"""Tests for security validation functions."""

import pytest
from pathlib import Path
from shinkuro.security import (
    validate_safe_path,
    validate_python_identifier,
    validate_path_component,
)


class TestValidateSafePath:
    """Tests for validate_safe_path function."""

    def test_valid_absolute_path(self, tmp_path):
        """Test validation of valid absolute path."""
        test_path = tmp_path / "test"
        test_path.mkdir()
        result = validate_safe_path(str(test_path))
        assert result == test_path

    def test_valid_relative_path(self, tmp_path):
        """Test validation of valid relative path."""
        test_path = tmp_path / "test"
        test_path.mkdir()
        result = validate_safe_path(str(test_path))
        assert result.is_absolute()

    def test_path_traversal_blocked_with_base(self, tmp_path):
        """Test that path traversal is blocked when base_path is provided."""
        base = tmp_path / "base"
        base.mkdir()
        # Try to escape base directory
        with pytest.raises(ValueError, match="resolves outside allowed base path"):
            validate_safe_path("../../../etc", str(base))

    def test_path_within_base_allowed(self, tmp_path):
        """Test that path within base is allowed."""
        base = tmp_path / "base"
        base.mkdir()
        sub = base / "sub"
        sub.mkdir()
        result = validate_safe_path(str(sub), str(base))
        assert result == sub

    def test_symlink_escape_blocked(self, tmp_path):
        """Test that symlinks escaping base are blocked."""
        base = tmp_path / "base"
        base.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        link = base / "link"
        link.symlink_to(outside)

        with pytest.raises(ValueError, match="resolves outside allowed base path"):
            validate_safe_path(str(link), str(base))


class TestValidatePythonIdentifier:
    """Tests for validate_python_identifier function."""

    def test_valid_identifier(self):
        """Test valid Python identifiers."""
        validate_python_identifier("valid_name")
        validate_python_identifier("_private")
        validate_python_identifier("CamelCase")
        validate_python_identifier("snake_case_123")

    def test_invalid_identifier_pattern(self):
        """Test invalid identifier patterns."""
        with pytest.raises(ValueError, match="Invalid Python identifier"):
            validate_python_identifier("123invalid")
        with pytest.raises(ValueError, match="Invalid Python identifier"):
            validate_python_identifier("invalid-name")
        with pytest.raises(ValueError, match="Invalid Python identifier"):
            validate_python_identifier("invalid.name")
        with pytest.raises(ValueError, match="Invalid Python identifier"):
            validate_python_identifier("")

    def test_dangerous_identifiers_blocked(self):
        """Test that dangerous identifiers are blocked."""
        dangerous = [
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
        ]
        for name in dangerous:
            with pytest.raises(ValueError, match="not allowed for security reasons"):
                validate_python_identifier(name)

    def test_dunder_methods_blocked(self):
        """Test that custom dunder methods are blocked."""
        with pytest.raises(ValueError, match="Dunder methods are not allowed"):
            validate_python_identifier("__custom__")
        # __init__ is caught by dangerous identifiers check
        with pytest.raises(ValueError, match="not allowed for security reasons"):
            validate_python_identifier("__init__")

    def test_single_underscore_allowed(self):
        """Test that single underscore prefixes are allowed."""
        validate_python_identifier("_private")
        validate_python_identifier("_internal_var")


class TestValidatePathComponent:
    """Tests for validate_path_component function."""

    def test_valid_component(self):
        """Test valid path components."""
        validate_path_component("username")
        validate_path_component("repo-name")
        validate_path_component("my.repo")
        validate_path_component("Project_123")

    def test_empty_component_blocked(self):
        """Test that empty components are blocked."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_path_component("")

    def test_dot_traversal_blocked(self):
        """Test that . and .. are blocked."""
        with pytest.raises(ValueError, match="cannot be"):
            validate_path_component(".")
        with pytest.raises(ValueError, match="cannot be"):
            validate_path_component("..")

    def test_path_separators_blocked(self):
        """Test that path separators are blocked."""
        with pytest.raises(ValueError, match="cannot contain separators"):
            validate_path_component("user/name")
        with pytest.raises(ValueError, match="cannot contain separators"):
            validate_path_component("user\\name")

    def test_null_bytes_blocked(self):
        """Test that null bytes are blocked."""
        with pytest.raises(ValueError, match="cannot contain null bytes"):
            validate_path_component("user\x00name")
