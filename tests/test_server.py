"""Tests for server.py SafeFormatter and prompt function creation."""

import asyncio
import pytest
from shinkuro.server import SafeFormatter, create_prompt_function
from shinkuro.file import PromptData, Argument
from fastmcp import FastMCP


def get_prompt_count(mcp: FastMCP) -> int:
    """Helper to synchronously get prompt count from FastMCP instance."""
    return len(asyncio.run(mcp._prompt_manager.list_prompts()))


class TestSafeFormatter:
    """Tests for SafeFormatter class."""

    def test_simple_substitution(self):
        """Test basic format string substitution."""
        formatter = SafeFormatter()
        result = formatter.format("Hello {name}", name="World")
        assert result == "Hello World"

    def test_multiple_substitutions(self):
        """Test multiple variable substitutions."""
        formatter = SafeFormatter()
        result = formatter.format("{greeting} {name}!", greeting="Hello", name="Alice")
        assert result == "Hello Alice!"

    def test_attribute_access_blocked(self):
        """Test that attribute access is blocked."""
        formatter = SafeFormatter()
        with pytest.raises(ValueError, match="must be a simple identifier"):
            formatter.format("{obj.__class__}", obj=object())

    def test_item_access_blocked(self):
        """Test that item access is blocked."""
        formatter = SafeFormatter()
        with pytest.raises(ValueError, match="must be a simple identifier"):
            formatter.format("{data[key]}", data={"key": "value"})

    def test_method_call_blocked(self):
        """Test that method calls are blocked."""
        formatter = SafeFormatter()
        with pytest.raises(ValueError, match="must be a simple identifier"):
            formatter.format("{name.upper()}", name="test")

    def test_missing_key_raises_error(self):
        """Test that missing keys raise KeyError."""
        formatter = SafeFormatter()
        with pytest.raises(KeyError):
            formatter.format("{missing}", name="value")

    def test_empty_string(self):
        """Test formatting empty string."""
        formatter = SafeFormatter()
        result = formatter.format("", name="value")
        assert result == ""

    def test_no_placeholders(self):
        """Test string with no placeholders."""
        formatter = SafeFormatter()
        result = formatter.format("Plain text", name="value")
        assert result == "Plain text"


class TestCreatePromptFunction:
    """Tests for create_prompt_function with security validation."""

    def test_prompt_without_arguments(self):
        """Test creating prompt function without arguments."""
        mcp = FastMCP(name="test")
        prompt_data = PromptData(
            name="simple",
            title="Simple Prompt",
            description="A simple prompt",
            arguments=[],
            content="Hello World",
        )
        create_prompt_function(mcp, prompt_data)
        # Verify prompt was registered
        assert get_prompt_count(mcp) == 1

    def test_prompt_with_valid_arguments(self):
        """Test creating prompt function with valid arguments."""
        mcp = FastMCP(name="test")
        prompt_data = PromptData(
            name="greeting",
            title="Greeting Prompt",
            description="A greeting prompt",
            arguments=[
                Argument(name="name", description="Person's name", default=None)
            ],
            content="Hello {name}",
        )
        create_prompt_function(mcp, prompt_data)
        assert get_prompt_count(mcp) == 1

    def test_prompt_with_dangerous_argument_name_skipped(self):
        """Test that prompts with dangerous argument names are skipped."""
        mcp = FastMCP(name="test")
        prompt_data = PromptData(
            name="dangerous",
            title="Dangerous Prompt",
            description="A prompt with dangerous argument",
            arguments=[
                Argument(name="__import__", description="Bad arg", default=None)
            ],
            content="Content {__import__}",
        )
        create_prompt_function(mcp, prompt_data)
        # Prompt should be skipped, not registered
        assert get_prompt_count(mcp) == 0

    def test_prompt_with_invalid_identifier_skipped(self):
        """Test that prompts with invalid identifier names are skipped."""
        mcp = FastMCP(name="test")
        prompt_data = PromptData(
            name="invalid",
            title="Invalid Prompt",
            description="A prompt with invalid argument",
            arguments=[
                Argument(name="123invalid", description="Bad arg", default=None)
            ],
            content="Content {123invalid}",
        )
        create_prompt_function(mcp, prompt_data)
        # Prompt should be skipped
        assert get_prompt_count(mcp) == 0

    def test_prompt_with_default_values(self):
        """Test creating prompt function with default argument values."""
        mcp = FastMCP(name="test")
        prompt_data = PromptData(
            name="greeting_default",
            title="Greeting with Default",
            description="A greeting with default",
            arguments=[
                Argument(name="name", description="Person's name", default="Friend")
            ],
            content="Hello {name}",
        )
        create_prompt_function(mcp, prompt_data)
        assert get_prompt_count(mcp) == 1

    def test_prompt_with_multiple_arguments(self):
        """Test creating prompt function with multiple arguments."""
        mcp = FastMCP(name="test")
        prompt_data = PromptData(
            name="multi_arg",
            title="Multi Argument Prompt",
            description="A prompt with multiple arguments",
            arguments=[
                Argument(name="greeting", description="Greeting", default="Hello"),
                Argument(name="name", description="Name", default=None),
                Argument(name="punctuation", description="End mark", default="!"),
            ],
            content="{greeting} {name}{punctuation}",
        )
        create_prompt_function(mcp, prompt_data)
        assert get_prompt_count(mcp) == 1

    def test_dunder_argument_name_blocked(self):
        """Test that dunder method names in arguments are blocked."""
        mcp = FastMCP(name="test")
        prompt_data = PromptData(
            name="dunder",
            title="Dunder Prompt",
            description="Prompt with dunder arg",
            arguments=[
                Argument(name="__custom__", description="Dunder arg", default=None)
            ],
            content="{__custom__}",
        )
        create_prompt_function(mcp, prompt_data)
        # Should be skipped
        assert get_prompt_count(mcp) == 0
