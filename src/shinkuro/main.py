"""Main entry point for shinkuro MCP server."""

import sys
from pathlib import Path
from fastmcp import FastMCP

from .config import Config
from .file.load import load_file_prompts
from .remote.git import get_local_cache_path, clone_or_update_repo


def main():
    """Start the shinkuro MCP server."""
    config = Config.from_env()
    mcp = FastMCP(name="shinkuro")

    if config.git_url:
        repo_path = get_local_cache_path(config.git_url, config.cache_dir)
        clone_or_update_repo(config.git_url, repo_path, config.auto_pull)

        if config.folder:
            # Use FOLDER as subfolder within the repo
            folder_path = repo_path / config.folder
        else:
            folder_path = repo_path
    else:
        if not config.folder:
            print(
                "Error: Either FOLDER or GIT_URL environment variable is required",
                file=sys.stderr,
            )
            sys.exit(1)
        folder_path = Path(config.folder)

    load_file_prompts(mcp, folder_path)
    mcp.run()


if __name__ == "__main__":
    main()
