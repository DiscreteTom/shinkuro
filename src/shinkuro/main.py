"""Main entry point for shinkuro MCP server."""

import os
import sys
from .file.load import load_file_prompts
from .remote.git import get_local_cache_path, clone_or_update_repo
from fastmcp import FastMCP
from pathlib import Path


def main():
    """Start the shinkuro MCP server."""
    git_url = os.getenv("GIT_URL")
    folder = os.getenv("FOLDER")

    mcp = FastMCP(name="shinkuro")

    if git_url:
        repo_path = get_local_cache_path(git_url)
        clone_or_update_repo(git_url, repo_path)

        if folder:
            # Use FOLDER as subfolder within the repo
            folder_path = repo_path / folder
        else:
            folder_path = repo_path
    else:
        if not folder:
            print(
                "Error: Either FOLDER or GIT_URL environment variable is required",
                file=sys.stderr,
            )
            sys.exit(1)
        folder_path = Path(folder)

    load_file_prompts(mcp, folder_path)
    mcp.run()


if __name__ == "__main__":
    main()
