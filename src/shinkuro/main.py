"""Main entry point for shinkuro MCP server."""

import typer
from pathlib import Path
from fastmcp import FastMCP
from typing_extensions import Annotated

from . import __version__
from .file.scan import scan_markdown_files
from .loader import get_folder_path
from .prompts.markdown import MarkdownPrompt
from .formatters import get_formatter
from .model import FormatterType
from typing import Optional


def version_callback(value: bool):
    if value:
        print(f"Shinkuro Version: {__version__}")
        raise typer.Exit()


def app(
    folder: Annotated[
        Optional[str],
        typer.Option(
            envvar="FOLDER",
            help="Path to local folder containing markdown files, or subfolder within git repo",
        ),
    ] = None,
    git_url: Annotated[
        Optional[str],
        typer.Option(
            envvar="GIT_URL",
            help="Git repository URL (supports GitHub, GitLab, SSH, HTTPS with credentials)",
        ),
    ] = None,
    cache_dir: Annotated[
        str,
        typer.Option(envvar="CACHE_DIR", help="Directory to cache remote repositories"),
    ] = "~/.shinkuro/remote",
    auto_pull: Annotated[
        bool,
        typer.Option(
            "--auto-pull",
            envvar="AUTO_PULL",
            help="Whether to refresh local cache on startup",
        ),
    ] = False,
    variable_format: Annotated[
        FormatterType,
        typer.Option(envvar="VARIABLE_FORMAT", help="Template variable format"),
    ] = FormatterType.BRACE,
    auto_discover_args: Annotated[
        bool,
        typer.Option(
            "--auto-discover-args",
            envvar="AUTO_DISCOVER_ARGS",
            help="Auto-discover template variables as required arguments",
        ),
    ] = False,
    skip_frontmatter: Annotated[
        bool,
        typer.Option(
            "--skip-frontmatter",
            envvar="SKIP_FRONTMATTER",
            help="Skip frontmatter processing and use raw markdown content",
        ),
    ] = False,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", callback=version_callback, help="Show version and exit"
        ),
    ] = None,
):
    """Shinkuro - Universal prompt loader MCP server"""
    mcp = FastMCP(name="shinkuro")

    try:
        folder_path = get_folder_path(
            folder, git_url, Path(cache_dir).expanduser(), auto_pull
        )
        formatter = get_formatter(variable_format)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    for prompt_data in scan_markdown_files(folder_path, skip_frontmatter):
        prompt = MarkdownPrompt.from_prompt_data(
            prompt_data, formatter, auto_discover_args
        )
        mcp.add_prompt(prompt)

    mcp.run()


def main():
    typer.run(app)


if __name__ == "__main__":
    main()
