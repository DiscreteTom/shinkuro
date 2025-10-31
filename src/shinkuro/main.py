"""Main entry point for shinkuro MCP server."""

import typer
from fastmcp import FastMCP

from . import __version__
from .config import Config
from .file.scan import scan_markdown_files
from .loader import get_folder_path
from .prompts.markdown import MarkdownPrompt
from .formatters import get_formatter
from typing import Optional, Annotated


def version_callback(value: bool):
    if value:
        print(f"Shinkuro Version: {__version__}")
        raise typer.Exit()


def app(
    _version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", callback=version_callback, help="Show version and exit"
        ),
    ] = None,
):
    """Shinkuro - Universal prompt loader MCP server"""
    config = Config.from_env()
    mcp = FastMCP(name="shinkuro")

    try:
        folder_path = get_folder_path(config)
        formatter = get_formatter(config.formatter)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    for prompt_data in scan_markdown_files(folder_path, config.skip_frontmatter):
        prompt = MarkdownPrompt.from_prompt_data(
            prompt_data, formatter, config.auto_discover_args
        )
        mcp.add_prompt(prompt)

    mcp.run()


def main():
    typer.run(app)


if __name__ == "__main__":
    main()
