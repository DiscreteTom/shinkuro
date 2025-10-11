"""Main entry point for shinkuro MCP server."""

import sys
from pathlib import Path
from fastmcp import FastMCP

from .config import Config
from .file.scan import scan_markdown_files
from .prompts.markdown import MarkdownPrompt
from .remote.git import get_local_cache_path, clone_or_update_repo


def get_folder_path(config: Config) -> Path:
    """
    Determine the folder path to scan for prompts based on configuration.

    Args:
        config: Application configuration

    Returns:
        Path to folder containing markdown files

    Raises:
        ValueError: If neither FOLDER nor GIT_URL is configured
    """
    if config.git_url:
        repo_path = get_local_cache_path(config.git_url, config.cache_dir)
        clone_or_update_repo(config.git_url, repo_path, config.auto_pull)

        if config.folder:
            # Use FOLDER as subfolder within the repo
            return repo_path / config.folder
        else:
            return repo_path
    else:
        if not config.folder:
            raise ValueError(
                "Either FOLDER or GIT_URL environment variable is required"
            )
        return Path(config.folder)


def main():
    """Start the shinkuro MCP server."""
    config = Config.from_env()
    mcp = FastMCP(name="shinkuro")

    try:
        folder_path = get_folder_path(config)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    for prompt_data in scan_markdown_files(folder_path):
        prompt = MarkdownPrompt.from_prompt_data(prompt_data)
        mcp.add_prompt(prompt)

    mcp.run()


if __name__ == "__main__":
    main()
