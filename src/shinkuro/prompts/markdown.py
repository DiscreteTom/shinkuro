"""Markdown-based prompt implementation."""

from typing import Any

from fastmcp.prompts.prompt import Prompt, PromptArgument
from mcp.types import PromptMessage, TextContent
from pydantic import Field

from ..model import PromptData
from ..formatters import FormatterInterface, validate_variable_name


class MarkdownPrompt(Prompt):
    """A prompt that renders markdown content with variable substitution."""

    content: str = Field(description="The markdown content to render")
    arg_defaults: dict[str, str] = Field(
        default_factory=dict, description="Default values for arguments"
    )

    def __init__(self, formatter: FormatterInterface, **data):
        # Use custom __init__ and private _formatter because Pydantic cannot
        # serialize Protocol types as regular fields
        super().__init__(**data)
        self._formatter = formatter

    @classmethod
    def from_prompt_data(
        cls,
        prompt_data: PromptData,
        formatter: FormatterInterface,
        auto_discover_args: bool = False,
    ) -> "MarkdownPrompt":
        """Create MarkdownPrompt from PromptData with validation."""
        if auto_discover_args:
            # Auto-discover arguments from template variables, ignore frontmatter args
            if prompt_data.arguments:
                raise ValueError(
                    "prompt_data.arguments must be empty when auto_discover_args is enabled"
                )
            discovered_args = formatter.extract_arguments(prompt_data.content)
            arguments = [
                PromptArgument(
                    name=arg,
                    description="",
                    required=True,
                )
                for arg in sorted(discovered_args)
            ]
            arg_defaults = {}
        else:
            # Validate arguments
            for arg in prompt_data.arguments:
                if not validate_variable_name(arg.name):
                    raise ValueError(
                        f"Argument name '{arg.name}' contains invalid characters"
                    )

            # Validate content and get discovered arguments
            discovered_args = formatter.extract_arguments(prompt_data.content)
            provided_args = {arg.name for arg in prompt_data.arguments}

            if discovered_args != provided_args:
                raise ValueError(
                    f"Content arguments {discovered_args} don't match provided arguments {provided_args}"
                )

            arguments = [
                PromptArgument(
                    name=arg.name,
                    description=arg.description,
                    required=arg.default is None,
                )
                for arg in prompt_data.arguments
            ]
            arg_defaults = {
                arg.name: arg.default
                for arg in prompt_data.arguments
                if arg.default is not None
            }

        return cls(
            formatter=formatter,
            name=prompt_data.name,
            title=prompt_data.title,
            description=prompt_data.description,
            arguments=arguments,
            tags={"shinkuro"},
            content=prompt_data.content,
            arg_defaults=arg_defaults,
        )

    async def render(
        self, arguments: dict[str, Any] | None = None
    ) -> list[PromptMessage]:
        """Render the prompt with variable substitution."""
        self._validate_arguments(arguments)

        # Merge provided arguments with defaults
        render_args = self.arg_defaults.copy()
        if arguments:
            render_args.update(arguments)

        # Perform variable substitution using formatter
        content = self._formatter.format(self.content, render_args)

        return [
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=content),
            )
        ]

    def _validate_arguments(self, arguments: dict[str, Any] | None) -> None:
        """Validate that all required arguments are provided."""
        if not self.arguments:
            return

        required = {arg.name for arg in self.arguments if arg.required}
        provided = set(arguments or {})
        missing = required - provided
        if missing:
            raise ValueError(f"Missing required arguments: {missing}")
