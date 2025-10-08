from fastmcp import FastMCP
from ..prompts.markdown import MarkdownPrompt
from .scan import scan_markdown_files
from pathlib import Path


def load_file_prompts(mcp: FastMCP, folder_path: Path) -> None:
    """Load prompts from local folder and register them with MCP server."""
    for prompt_data in scan_markdown_files(folder_path):
        prompt = MarkdownPrompt.from_prompt_data(prompt_data)
        mcp.add_prompt(prompt)
