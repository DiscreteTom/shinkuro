"""Local file-based prompt loader."""

import frontmatter
import re
import string
import sys
from pathlib import Path
from typing import Iterator, Optional, Any
from ..model import Argument, PromptData
from ..interfaces import FileSystemInterface, DefaultFileSystem


def _extract_string_field(
    metadata: dict, field: str, default: str, file_path: Path
) -> str:
    """Extract and validate a string field from frontmatter metadata."""
    value = metadata.get(field)
    if value is None:
        return default
    elif isinstance(value, str):
        return value
    else:
        print(
            f"Warning: '{field}' field in {file_path} is not a string, converting to string",
            file=sys.stderr,
        )
        return str(value)


def _parse_argument(arg_data: Any, file_path: Path) -> Optional[Argument]:
    """Parse a single argument from frontmatter data."""
    if not isinstance(arg_data, dict):
        print(
            f"Warning: argument item in {file_path} is not a dict, skipping",
            file=sys.stderr,
        )
        return None

    # Handle name field - required
    arg_name = arg_data.get("name")
    if arg_name is None or arg_name == "":
        print(
            f"Warning: argument 'name' field is missing or empty in {file_path}, skipping argument",
            file=sys.stderr,
        )
        return None
    elif not isinstance(arg_name, str):
        print(
            f"Warning: argument 'name' field in {file_path} is not a string, converting to string",
            file=sys.stderr,
        )
        arg_name = str(arg_name)

    # Validate arg name format
    if not re.match(r"^[a-zA-Z0-9_]+$", arg_name):
        print(
            f"Warning: argument name '{arg_name}' in {file_path} contains invalid characters, skipping argument",
            file=sys.stderr,
        )
        return None

    # Handle description field
    arg_description = arg_data.get("description", "")
    if arg_description != "" and not isinstance(arg_description, str):
        print(
            f"Warning: argument 'description' field in {file_path} is not a string, converting to string",
            file=sys.stderr,
        )
        arg_description = str(arg_description)

    # Handle default field
    arg_default = arg_data.get("default")
    if arg_default is not None and not isinstance(arg_default, str):
        print(
            f"Warning: argument 'default' field in {file_path} is not a string, converting to string",
            file=sys.stderr,
        )
        arg_default = str(arg_default)

    return Argument(name=arg_name, description=arg_description, default=arg_default)


def _parse_arguments(metadata: dict, file_path: Path) -> list[Argument]:
    """Parse arguments list from frontmatter metadata."""
    frontmatter_arguments = metadata.get("arguments", [])
    if not isinstance(frontmatter_arguments, list):
        if frontmatter_arguments is not None:
            print(
                f"Warning: 'arguments' field in {file_path} is not a list, ignoring",
                file=sys.stderr,
            )
        return []

    arguments = []
    for arg_data in frontmatter_arguments:
        arg = _parse_argument(arg_data, file_path)
        if arg:
            arguments.append(arg)
    return arguments


def _validate_template_variables(content: str) -> bool:
    """Validate that template variables are safe (alphanumeric and underscore only)."""
    formatter = string.Formatter()
    for literal_text, field_name, format_spec, conversion in formatter.parse(content):
        if field_name and not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", field_name):
            return False
    return True


def _parse_markdown_file(
    md_file: Path, folder: Path, content: str
) -> Optional[PromptData]:
    """Parse a single markdown file into PromptData."""
    post = frontmatter.loads(content)

    name = _extract_string_field(post.metadata, "name", md_file.stem, md_file)
    title = _extract_string_field(post.metadata, "title", md_file.stem, md_file)
    description = _extract_string_field(
        post.metadata,
        "description",
        f"Prompt from {md_file.relative_to(folder)}",
        md_file,
    )
    arguments = _parse_arguments(post.metadata, md_file)

    if not _validate_template_variables(post.content):
        print(
            f"Warning: content in {md_file} contains unsafe template variables, skipping file",
            file=sys.stderr,
        )
        return None

    return PromptData(name, title, description, arguments, post.content)


def scan_markdown_files(
    folder: Path, *, fs: FileSystemInterface = DefaultFileSystem()
) -> Iterator[PromptData]:
    """
    Scan folder recursively for markdown files.

    Args:
        folder_path: Path to folder to scan
        fs: File system interface for file operations

    Yields:
        PromptData for each markdown file
    """
    if not fs.exists(folder) or not fs.is_dir(folder):
        print(
            f"Warning: folder path '{str(folder)}' does not exist or is not a directory",
            file=sys.stderr,
        )
        return

    for md_file in fs.glob_markdown(folder):
        try:
            content = fs.read_text(md_file)
            prompt_data = _parse_markdown_file(md_file, folder, content)
            if prompt_data:
                yield prompt_data
        except Exception as e:
            print(
                f"Warning: failed to process {md_file}: {e}",
                file=sys.stderr,
            )
            continue
