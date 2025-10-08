"""Main entry point for shinkuro MCP server."""

import os
import sys
from .file.load import load_file_prompts
from .remote.git import get_local_cache_path, clone_or_update_repo
from fastmcp import FastMCP


def main():
    """Start the shinkuro MCP server."""
    git_url = os.getenv("GIT_URL")
    folder = os.getenv("FOLDER")

    if git_url:
        # Get local repo path and clone/update
        repo_path = get_local_cache_path(git_url)
        clone_or_update_repo(git_url, repo_path)

        if folder:
            # Use FOLDER as subfolder within the repo
            folder = str(repo_path / folder)
        else:
            folder = str(repo_path)
    elif not folder:
        print(
            "Error: Either FOLDER or GIT_URL environment variable is required",
            file=sys.stderr,
        )
        sys.exit(1)

    mcp = FastMCP(name="shinkuro")
    load_file_prompts(mcp, folder)
    mcp.run()


if __name__ == "__main__":
    main()
