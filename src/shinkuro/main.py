"""Main entry point for shinkuro MCP server."""

import os
import sys
from pathlib import Path
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
                # Validate that subfolder path stays within repo
                folder_abs = Path(repo_path) / folder
                folder_resolved = folder_abs.resolve()
                repo_resolved = Path(repo_path).resolve()
                try:
                    folder_resolved.relative_to(repo_resolved)
                    folder = str(folder_resolved)
                except ValueError:
                    print(
                        "Error: FOLDER path escapes repository boundary",
                        file=sys.stderr,
                    )
                    sys.exit(1)
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
    else:
        # Validate standalone FOLDER path
        try:
            folder_path = Path(folder).resolve()
            if not folder_path.exists():
                print(f"Error: FOLDER path does not exist: {folder}", file=sys.stderr)
                sys.exit(1)
            if not folder_path.is_dir():
                print(
                    f"Error: FOLDER path is not a directory: {folder}", file=sys.stderr
                )
                sys.exit(1)
            folder = str(folder_path)
        except (OSError, RuntimeError) as e:
            print(f"Error: Invalid FOLDER path: {e}", file=sys.stderr)
            sys.exit(1)

    mcp = create_server(folder_path=folder)
    mcp.run()


if __name__ == "__main__":
    main()
