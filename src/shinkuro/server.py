"""Main MCP server for prompt management."""

from fastmcp import FastMCP
from .file import scan_markdown_files, PromptData


def create_prompt_function(mcp: FastMCP, prompt_data: PromptData):
    """Create and register a prompt function using decorator pattern."""

    if not prompt_data.arguments:

        @mcp.prompt(
            name=prompt_data.name,
            description=prompt_data.description,
            tags={"local"},
            meta={},
        )
        def prompt_func() -> str:
            return prompt_data.content

    else:
        # Build function signature dynamically
        params = []
        for arg in prompt_data.arguments:
            escaped_arg_desc = repr(arg.description)

            if arg.default is None:
                params.append(
                    f"{arg.name}: str = Field(description={escaped_arg_desc})"
                )
            else:
                escaped_arg_default = repr(arg.default)
                params.append(
                    f"{arg.name}: str = Field(description={escaped_arg_desc}, default={escaped_arg_default})"
                )

        param_str = ", ".join(params)

        # Create function code
        escaped_name = repr(prompt_data.name)
        escaped_description = repr(prompt_data.description)
        escaped_content = repr(prompt_data.content)

        func_code = f"""
from pydantic import Field
@mcp.prompt(name={escaped_name}, description={escaped_description}, tags={{"local"}}, meta={{}})
def prompt_func({param_str}) -> str:
    return {escaped_content}.format({", ".join(f"{arg.name}={arg.name}" for arg in prompt_data.arguments)})
"""

        # Execute the function creation
        exec(func_code)


def setup_file_prompts(mcp: FastMCP, folder_path: str) -> None:
    """Load prompts from local folder and register them with MCP server."""
    for prompt_data in scan_markdown_files(folder_path):
        create_prompt_function(mcp, prompt_data)


def create_server(folder_path: str) -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP(name="shinkuro")
    setup_file_prompts(mcp, folder_path)
    return mcp
