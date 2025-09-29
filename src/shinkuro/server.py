"""Main MCP server for prompt management."""

from fastmcp import FastMCP
from .file_loader import scan_markdown_files


def create_prompt_function(mcp: FastMCP, name: str, content: str, description: str):
    """Create and register a prompt function using decorator pattern."""

    @mcp.prompt(name=name, description=description, tags={"local"}, meta={})
    def prompt_func() -> str:
        return content

    return prompt_func


def setup_file_prompts(mcp: FastMCP, folder_path: str) -> None:
    """Load prompts from local folder and register them with MCP server."""
    for name, content, description in scan_markdown_files(folder_path):
        create_prompt_function(mcp, name, content, description)


def create_server(folder_path: str) -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP(name="shinkuro")
    setup_file_prompts(mcp, folder_path)
    return mcp
