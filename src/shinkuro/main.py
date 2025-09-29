"""Main entry point for shinkuro MCP server."""

import os
import sys
from .server import create_server
from .remote.git import clone_or_update_repo


def main():
    """Start the shinkuro MCP server."""
    git_url = os.getenv("GIT_URL")
    folder = os.getenv("FOLDER")

    if git_url:
        # Clone/update git repo and use as folder
        try:
            repo_path = clone_or_update_repo(git_url)
            if folder:
                # Use FOLDER as subfolder within the repo
                folder = os.path.join(repo_path, folder)
            else:
                folder = repo_path
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif not folder:
        print(
            "Error: Either FOLDER or GIT_URL environment variable is required",
            file=sys.stderr,
        )
        sys.exit(1)

    mcp = create_server(folder_path=folder)
    mcp.run()


if __name__ == "__main__":
    main()
