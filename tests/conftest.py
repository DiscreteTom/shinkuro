"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_prompts_dir(tmp_path):
    """Create a directory with sample prompt markdown files."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    # Simple prompt
    (prompts_dir / "simple.md").write_text("This is a simple prompt.")

    # Prompt with frontmatter
    (prompts_dir / "greeting.md").write_text(
        """---
name: greet
title: Greeting Prompt
description: A friendly greeting
arguments:
  - name: name
    description: Person's name
---
Hello {name}! Welcome to the system."""
    )

    # Prompt with default arguments
    (prompts_dir / "welcome.md").write_text(
        """---
name: welcome
title: Welcome Message
description: Welcome message with customization
arguments:
  - name: greeting
    description: Greeting word
    default: "Welcome"
  - name: user
    description: Username
---
{greeting}, {user}!"""
    )

    return prompts_dir


@pytest.fixture
def empty_dir(tmp_path):
    """Create an empty directory."""
    empty = tmp_path / "empty"
    empty.mkdir()
    return empty
