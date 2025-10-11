"""Test fixtures and factories for creating test data."""

from pathlib import Path
from shinkuro.model import Argument, PromptData


def create_argument(
    name: str = "test_arg",
    description: str = "Test argument",
    default: str | None = None,
) -> Argument:
    """Create a test Argument instance."""
    return Argument(name=name, description=description, default=default)


def create_prompt_data(
    name: str = "test_prompt",
    title: str = "Test Prompt",
    description: str = "Test description",
    arguments: list[Argument] | None = None,
    content: str = "Test content",
) -> PromptData:
    """Create a test PromptData instance."""
    return PromptData(
        name=name,
        title=title,
        description=description,
        arguments=arguments or [],
        content=content,
    )


def create_markdown_file_content(
    content: str = "Hello world",
    name: str | None = None,
    title: str | None = None,
    description: str | None = None,
    arguments: list[dict] | None = None,
) -> str:
    """Create markdown file content with optional frontmatter."""
    if not any([name, title, description, arguments]):
        return content

    frontmatter = "---\n"
    if name:
        frontmatter += f"name: {name}\n"
    if title:
        frontmatter += f"title: {title}\n"
    if description:
        frontmatter += f"description: {description}\n"
    if arguments:
        frontmatter += "arguments:\n"
        for arg in arguments:
            frontmatter += f"  - name: {arg['name']}\n"
            if "description" in arg:
                frontmatter += f"    description: {arg['description']}\n"
            if "default" in arg:
                frontmatter += f"    default: {arg['default']}\n"
    frontmatter += "---\n"

    return frontmatter + content


def create_test_files(files: dict[str, str]) -> dict[Path, str]:
    """Convert string paths to Path objects for MockFileSystem."""
    return {Path(path): content for path, content in files.items()}
