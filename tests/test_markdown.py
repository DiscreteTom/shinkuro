"""Tests for prompts/markdown.py module."""

import pytest
from mcp.types import TextContent
from shinkuro.prompts.markdown import MarkdownPrompt
from shinkuro.formatters import BraceFormatter, DollarFormatter
from .fixtures import create_prompt_data, create_argument


@pytest.mark.asyncio
async def test_markdown_prompt_from_prompt_data():
    prompt_data = create_prompt_data(
        name="test",
        title="Test Prompt",
        description="Test description",
        arguments=[create_argument("user", "User name", None)],
        content="Hello {user}",
    )

    prompt = MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())

    assert prompt.name == "test"
    assert prompt.title == "Test Prompt"
    assert prompt.description == "Test description"
    assert prompt.arguments is not None
    assert len(prompt.arguments) == 1
    assert prompt.arguments[0].name == "user"
    assert prompt.arguments[0].required is True
    assert prompt.content == "Hello {user}"


@pytest.mark.asyncio
async def test_markdown_prompt_with_defaults():
    prompt_data = create_prompt_data(
        arguments=[create_argument("user", "User name", "guest")],
        content="Hello {user}",
    )

    prompt = MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())

    assert prompt.arguments is not None
    assert prompt.arguments[0].required is False
    assert prompt.arg_defaults == {"user": "guest"}


@pytest.mark.asyncio
async def test_markdown_prompt_render_simple():
    prompt_data = create_prompt_data(content="Hello world")
    prompt = MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())

    messages = await prompt.render()

    assert len(messages) == 1
    assert messages[0].role == "user"
    assert isinstance(messages[0].content, TextContent)
    assert messages[0].content.text == "Hello world"


@pytest.mark.asyncio
async def test_markdown_prompt_render_with_arguments():
    prompt_data = create_prompt_data(
        arguments=[create_argument("name", "Name", None)],
        content="Hello {name}!",
    )
    prompt = MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())

    messages = await prompt.render({"name": "Alice"})

    assert isinstance(messages[0].content, TextContent)
    assert messages[0].content.text == "Hello Alice!"


@pytest.mark.asyncio
async def test_markdown_prompt_render_with_defaults():
    prompt_data = create_prompt_data(
        arguments=[create_argument("name", "Name", "World")],
        content="Hello {name}!",
    )
    prompt = MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())

    messages = await prompt.render()

    assert isinstance(messages[0].content, TextContent)
    assert messages[0].content.text == "Hello World!"


@pytest.mark.asyncio
async def test_markdown_prompt_render_override_default():
    prompt_data = create_prompt_data(
        arguments=[create_argument("name", "Name", "World")],
        content="Hello {name}!",
    )
    prompt = MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())

    messages = await prompt.render({"name": "Alice"})

    assert isinstance(messages[0].content, TextContent)
    assert messages[0].content.text == "Hello Alice!"


@pytest.mark.asyncio
async def test_markdown_prompt_missing_required_argument():
    prompt_data = create_prompt_data(
        arguments=[create_argument("name", "Name", None)],
        content="Hello {name}!",
    )
    prompt = MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())

    with pytest.raises(ValueError, match="Missing required arguments"):
        await prompt.render()


@pytest.mark.asyncio
async def test_markdown_prompt_validate_arguments_no_args():
    prompt_data = create_prompt_data(content="Hello")
    prompt = MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())

    # Should not raise
    prompt._validate_arguments(None)
    prompt._validate_arguments({})


@pytest.mark.asyncio
async def test_markdown_prompt_multiple_arguments():
    prompt_data = create_prompt_data(
        arguments=[
            create_argument("first", "First name", None),
            create_argument("last", "Last name", "Doe"),
        ],
        content="Hello {first} {last}!",
    )
    prompt = MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())

    messages = await prompt.render({"first": "John"})

    assert isinstance(messages[0].content, TextContent)
    assert messages[0].content.text == "Hello John Doe!"


@pytest.mark.asyncio
async def test_markdown_prompt_dollar_formatter():
    prompt_data = create_prompt_data(
        arguments=[create_argument("name", "Name", None)],
        content="Hello $name!",
    )
    prompt = MarkdownPrompt.from_prompt_data(prompt_data, DollarFormatter())

    messages = await prompt.render({"name": "Alice"})

    assert isinstance(messages[0].content, TextContent)
    assert messages[0].content.text == "Hello Alice!"


@pytest.mark.asyncio
async def test_markdown_prompt_validation_invalid_argument_name():
    prompt_data = create_prompt_data(
        arguments=[create_argument("123invalid", "Invalid name", None)],
        content="Hello {user}!",
    )

    with pytest.raises(
        ValueError, match="Argument name '123invalid' contains invalid characters"
    ):
        MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())


@pytest.mark.asyncio
async def test_markdown_prompt_validation_mismatched_arguments():
    prompt_data = create_prompt_data(
        arguments=[create_argument("user", "User name", None)],
        content="Hello {name}!",  # Different parameter name
    )

    with pytest.raises(
        ValueError, match="Content arguments .* don't match provided arguments"
    ):
        MarkdownPrompt.from_prompt_data(prompt_data, BraceFormatter())


@pytest.mark.asyncio
async def test_markdown_prompt_auto_discover_args():
    prompt_data = create_prompt_data(
        arguments=[],  # No arguments in frontmatter
        content="Hello {user} from {project}!",
    )

    prompt = MarkdownPrompt.from_prompt_data(
        prompt_data, BraceFormatter(), auto_discover_args=True
    )

    assert prompt.arguments is not None
    assert len(prompt.arguments) == 2
    assert prompt.arguments[0].name == "project"  # sorted order
    assert prompt.arguments[1].name == "user"
    assert prompt.arguments[0].required is True
    assert prompt.arguments[1].required is True
    assert prompt.arg_defaults == {}


@pytest.mark.asyncio
async def test_markdown_prompt_auto_discover_args_with_existing_args():
    prompt_data = create_prompt_data(
        arguments=[create_argument("user", "User name", None)],
        content="Hello {user}!",
    )

    with pytest.raises(
        ValueError,
        match="prompt_data.arguments must be empty when auto_discover_args is enabled",
    ):
        MarkdownPrompt.from_prompt_data(
            prompt_data, BraceFormatter(), auto_discover_args=True
        )
