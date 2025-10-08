"""Main MCP server for prompt management."""

from fastmcp import FastMCP
from .file import scan_markdown_files, PromptData
from pydantic import Field
from pydantic.fields import FieldInfo
from .security import validate_python_identifier
import string


class SafeFormatter(string.Formatter):
    """String formatter that prevents attribute/item access for security."""

    def get_field(self, field_name, args, kwargs):
        """Override to prevent attribute/item access in format strings."""
        # Only allow simple field names (no dots, brackets, or other access)
        if not field_name.isidentifier():
            raise ValueError(
                f"Format field must be a simple identifier, got: {field_name}"
            )
        # Get the value from kwargs only (no positional args)
        if field_name not in kwargs:
            raise KeyError(field_name)
        return kwargs[field_name], field_name


def create_prompt_function(mcp: FastMCP, prompt_data: PromptData):
    """Create and register a prompt function using decorator pattern."""

    if not prompt_data.arguments:

        @mcp.prompt(
            name=prompt_data.name,
            title=prompt_data.title,
            description=prompt_data.description,
            tags={"shinkuro"},
            meta={},
        )
        def prompt_func() -> str:
            return prompt_data.content

    else:
        # Validate all argument names for security
        for arg in prompt_data.arguments:
            try:
                validate_python_identifier(arg.name)
            except ValueError:
                # Skip this prompt if it has invalid argument names
                return

        # Build function signature dynamically
        params = []
        defaults = []
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
                defaults.append(
                    f"""
    if isinstance({arg.name}, FieldInfo):
        {arg.name} = {escaped_arg_default}
"""
                )

        param_str = ", ".join(params)
        defaults_code = "\n".join(defaults)

        # Create function code
        escaped_name = repr(prompt_data.name)
        escaped_title = repr(prompt_data.title)
        escaped_description = repr(prompt_data.description)
        escaped_content = repr(prompt_data.content)

        # Use SafeFormatter to prevent attribute access attacks
        func_code = f"""
@mcp.prompt(name={escaped_name}, title={escaped_title}, description={escaped_description}, tags={{"shinkuro"}}, meta={{}})
def prompt_func({param_str}) -> str:
{defaults_code}
    formatter = SafeFormatter()
    return formatter.format({escaped_content}, {", ".join(f"{arg.name}={arg.name}" for arg in prompt_data.arguments)})
"""

        # Execute the function creation
        exec(
            func_code,
            locals={
                "mcp": mcp,
                "Field": Field,
                "FieldInfo": FieldInfo,
                "SafeFormatter": SafeFormatter,
            },
        )


def setup_file_prompts(mcp: FastMCP, folder_path: str) -> None:
    """Load prompts from local folder and register them with MCP server."""
    for prompt_data in scan_markdown_files(folder_path):
        create_prompt_function(mcp, prompt_data)


def create_server(folder_path: str) -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP(name="shinkuro")
    setup_file_prompts(mcp, folder_path)
    return mcp
