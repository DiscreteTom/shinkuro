"""Markdown-based prompt implementation."""

from typing import Any

from fastmcp.prompts.prompt import Prompt, PromptArgument
from mcp.types import PromptMessage, TextContent
from pydantic import Field

from ..file import PromptData


class MarkdownPrompt(Prompt):
    """A prompt that renders markdown content with variable substitution."""

    content: str = Field(description="The markdown content to render")
    arg_defaults: dict[str, str] = Field(
        default_factory=dict, description="Default values for arguments"
    )

    @classmethod
    def from_prompt_data(cls, prompt_data: PromptData) -> "MarkdownPrompt":
        """Create MarkdownPrompt from PromptData."""
        arguments = [
            PromptArgument(
                name=arg.name,
                description=arg.description,
                required=arg.default is None,
            )
            for arg in prompt_data.arguments
        ]

        return cls(
            name=prompt_data.name,
            title=prompt_data.title,
            description=prompt_data.description,
            arguments=arguments,
            tags={"shinkuro"},
            content=prompt_data.content,
            arg_defaults={
                arg.name: arg.default
                for arg in prompt_data.arguments
                if arg.default is not None
            },
        )

    async def render(
        self, arguments: dict[str, Any] | None = None
    ) -> list[PromptMessage]:
        """Render the prompt with variable substitution."""
        # Validate required arguments
        if self.arguments:
            required = {arg.name for arg in self.arguments if arg.required}
            provided = set(arguments or {})
            missing = required - provided
            if missing:
                raise ValueError(f"Missing required arguments: {missing}")

        # Merge provided arguments with defaults
        render_args = self.arg_defaults.copy()
        if arguments:
            render_args.update(arguments)

        # Perform variable substitution
        content = self.content.format(**render_args)

        return [
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=content),
            )
        ]
