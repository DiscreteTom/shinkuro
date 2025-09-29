"""Main entry point for shinkuro MCP server."""

import os
import sys
from .server import create_server


def main():
    """Start the shinkuro MCP server."""
    folder = os.getenv("FOLDER")
    if not folder:
        print("Error: FOLDER environment variable is required", file=sys.stderr)
        sys.exit(1)

    mcp = create_server(folder_path=folder)
    mcp.run()


if __name__ == "__main__":
    main()
