"""Main entry point for shinkuro MCP server."""

import sys
from fastmcp import FastMCP

from .config import Config
from .file.scan import scan_markdown_files
from .loader import get_folder_path
from .prompts.markdown import MarkdownPrompt
from .formatters import get_formatter


def main():
    """Start the shinkuro MCP server."""
    config = Config.from_env()
    mcp = FastMCP(name="shinkuro")

    try:
        folder_path = get_folder_path(config)
        formatter = get_formatter(config.formatter)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    for prompt_data in scan_markdown_files(folder_path, config.skip_frontmatter):
        prompt = MarkdownPrompt.from_prompt_data(
            prompt_data, formatter, config.auto_discover_args
        )
        mcp.add_prompt(prompt)

    mcp.run()


if __name__ == "__main__":
    main()
