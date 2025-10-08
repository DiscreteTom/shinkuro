"""Main MCP server for prompt management."""

from fastmcp import FastMCP
from .file import scan_markdown_files
from .prompts.markdown import MarkdownPrompt


def setup_file_prompts(mcp: FastMCP, folder_path: str) -> None:
    """Load prompts from local folder and register them with MCP server."""
    for prompt_data in scan_markdown_files(folder_path):
        prompt = MarkdownPrompt.from_prompt_data(prompt_data)
        mcp.add_prompt(prompt)


def create_server(folder_path: str) -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP(name="shinkuro")
    setup_file_prompts(mcp, folder_path)
    return mcp
