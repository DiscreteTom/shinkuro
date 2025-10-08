"""Integration tests for shinkuro server functionality."""

import asyncio
import pytest
from pathlib import Path
from shinkuro.server import create_server
from fastmcp import FastMCP


def get_prompt_count(mcp: FastMCP) -> int:
    """Helper to synchronously get prompt count from FastMCP instance."""
    return len(asyncio.run(mcp._prompt_manager.list_prompts()))


class TestServerIntegration:
    """Integration tests for server creation and prompt loading."""

    def test_create_server_with_simple_prompts(self, tmp_path):
        """Test creating server with simple prompts."""
        # Create test markdown files
        (tmp_path / "simple.md").write_text("This is a simple prompt.")
        (tmp_path / "another.md").write_text("Another simple prompt.")

        mcp = create_server(str(tmp_path))
        assert mcp is not None
        assert get_prompt_count(mcp) == 2

    def test_create_server_with_prompts_with_arguments(self, tmp_path):
        """Test creating server with prompts that have arguments."""
        greeting_md = tmp_path / "greeting.md"
        greeting_md.write_text(
            """---
name: greet
title: Greeting
description: A greeting prompt
arguments:
  - name: name
    description: Person's name
---
Hello {name}!"""
        )

        mcp = create_server(str(tmp_path))
        assert get_prompt_count(mcp) == 1

    def test_create_server_with_mixed_prompts(self, tmp_path):
        """Test creating server with mix of simple and parameterized prompts."""
        # Simple prompt
        (tmp_path / "simple.md").write_text("Simple content")

        # Parameterized prompt
        param_md = tmp_path / "param.md"
        param_md.write_text(
            """---
arguments:
  - name: var
    description: A variable
---
Content with {var}"""
        )

        mcp = create_server(str(tmp_path))
        assert get_prompt_count(mcp) == 2

    def test_create_server_skips_invalid_prompts(self, tmp_path):
        """Test that server creation skips prompts with invalid arguments."""
        # Valid prompt
        (tmp_path / "valid.md").write_text("Valid prompt")

        # Invalid prompt with dangerous argument name
        invalid_md = tmp_path / "invalid.md"
        invalid_md.write_text(
            """---
arguments:
  - name: __import__
    description: Dangerous arg
---
Content {__import__}"""
        )

        mcp = create_server(str(tmp_path))
        # Should only have the valid prompt
        assert get_prompt_count(mcp) == 1

    def test_create_server_with_nested_directories(self, tmp_path):
        """Test server creation with nested directory structure."""
        subdir1 = tmp_path / "subdir1"
        subdir2 = tmp_path / "subdir2"
        subdir1.mkdir()
        subdir2.mkdir()

        (tmp_path / "root.md").write_text("Root prompt")
        (subdir1 / "sub1.md").write_text("Subdir 1 prompt")
        (subdir2 / "sub2.md").write_text("Subdir 2 prompt")

        mcp = create_server(str(tmp_path))
        assert get_prompt_count(mcp) == 3

    def test_create_server_empty_directory(self, tmp_path):
        """Test creating server with empty directory."""
        mcp = create_server(str(tmp_path))
        assert mcp is not None
        assert get_prompt_count(mcp) == 0

    def test_prompt_with_multiple_arguments(self, tmp_path):
        """Test prompt with multiple arguments."""
        multi_md = tmp_path / "multi.md"
        multi_md.write_text(
            """---
arguments:
  - name: greeting
    description: Greeting word
    default: Hello
  - name: name
    description: Person's name
  - name: punctuation
    description: Ending punctuation
    default: "!"
---
{greeting} {name}{punctuation}"""
        )

        mcp = create_server(str(tmp_path))
        assert get_prompt_count(mcp) == 1

    def test_prompt_content_preserved(self, tmp_path):
        """Test that prompt content is preserved correctly."""
        content = """# Title

This is a complex prompt with:
- Multiple lines
- Special characters: !@#$%
- Code blocks:
```python
def hello():
    print("world")
```"""
        (tmp_path / "complex.md").write_text(content)

        mcp = create_server(str(tmp_path))
        assert get_prompt_count(mcp) == 1
        # Content should be preserved in the prompt

    def test_frontmatter_with_special_characters(self, tmp_path):
        """Test frontmatter with special characters in strings."""
        special_md = tmp_path / "special.md"
        special_md.write_text(
            """---
name: special_chars
title: "Title with quotes and apostrophes"
description: Description with special chars
---
Content"""
        )

        mcp = create_server(str(tmp_path))
        assert get_prompt_count(mcp) == 1

    def test_safe_formatter_in_prompts(self, tmp_path):
        """Test that SafeFormatter is used in generated prompts."""
        # Create a prompt that would fail without SafeFormatter
        param_md = tmp_path / "safe.md"
        param_md.write_text(
            """---
arguments:
  - name: value
    description: A safe value
---
The value is: {value}"""
        )

        mcp = create_server(str(tmp_path))
        assert get_prompt_count(mcp) == 1
        # Prompt should be registered with SafeFormatter protecting it
