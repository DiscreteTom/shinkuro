"""Local file-based prompt loader."""

import frontmatter
from pathlib import Path
from typing import Iterator, Optional, Any
from ..model import Argument, PromptData
from ..interfaces import (
    FileSystemInterface,
    DefaultFileSystem,
    LoggerInterface,
    DefaultLogger,
)


def _extract_string_field(
    metadata: dict,
    field: str,
    default: str,
    file_path: Path,
    *,
    logger: LoggerInterface,
) -> str:
    """Extract and validate a string field from frontmatter metadata."""
    value = metadata.get(field)
    if value is None:
        return default
    elif isinstance(value, str):
        return value
    else:
        logger.warning(
            f"'{field}' field in {file_path} is not a string, converting to string"
        )
        return str(value)


def _parse_argument(
    arg_data: Any, file_path: Path, *, logger: LoggerInterface
) -> Optional[Argument]:
    """Parse a single argument from frontmatter data."""
    if not isinstance(arg_data, dict):
        logger.warning(f"argument item in {file_path} is not a dict, skipping")
        return None

    # Handle name field - required
    arg_name = arg_data.get("name")
    if arg_name is None or arg_name == "":
        logger.warning(
            f"argument 'name' field is missing or empty in {file_path}, skipping argument"
        )
        return None
    elif not isinstance(arg_name, str):
        logger.warning(
            f"argument 'name' field in {file_path} is not a string, converting to string"
        )
        arg_name = str(arg_name)

    # Handle description field
    arg_description = arg_data.get("description", "")
    if arg_description != "" and not isinstance(arg_description, str):
        logger.warning(
            f"argument 'description' field in {file_path} is not a string, converting to string"
        )
        arg_description = str(arg_description)

    # Handle default field
    arg_default = arg_data.get("default")
    if arg_default is not None and not isinstance(arg_default, str):
        logger.warning(
            f"argument 'default' field in {file_path} is not a string, converting to string"
        )
        arg_default = str(arg_default)

    return Argument(name=arg_name, description=arg_description, default=arg_default)


def _parse_arguments(
    metadata: dict, file_path: Path, *, logger: LoggerInterface
) -> list[Argument]:
    """Parse arguments list from frontmatter metadata."""
    frontmatter_arguments = metadata.get("arguments", [])
    if not isinstance(frontmatter_arguments, list):
        if frontmatter_arguments is not None:
            logger.warning(f"'arguments' field in {file_path} is not a list, ignoring")
        return []

    arguments = []
    for arg_data in frontmatter_arguments:
        arg = _parse_argument(arg_data, file_path, logger=logger)
        if arg:
            arguments.append(arg)
    return arguments


def _parse_markdown_file(
    md_file: Path,
    folder: Path,
    content: str,
    skip_frontmatter: bool,
    *,
    logger: LoggerInterface,
) -> PromptData:
    """Parse a single markdown file into PromptData."""
    default_description = f"Prompt from {md_file.relative_to(folder)}"

    if skip_frontmatter:
        # Skip frontmatter processing, use file content as-is
        return PromptData(
            name=md_file.stem,
            title=md_file.stem,
            description=default_description,
            arguments=[],
            content=content,
        )

    post = frontmatter.loads(content)

    name = _extract_string_field(
        post.metadata, "name", md_file.stem, md_file, logger=logger
    )
    title = _extract_string_field(
        post.metadata, "title", md_file.stem, md_file, logger=logger
    )
    description = _extract_string_field(
        post.metadata,
        "description",
        default_description,
        md_file,
        logger=logger,
    )
    arguments = _parse_arguments(post.metadata, md_file, logger=logger)

    return PromptData(name, title, description, arguments, post.content)


def scan_markdown_files(
    folder: Path,
    skip_frontmatter: bool,
    *,
    fs: FileSystemInterface = DefaultFileSystem(),
    logger: LoggerInterface = DefaultLogger(),
) -> Iterator[PromptData]:
    """
    Scan folder recursively for markdown files.

    Args:
        folder_path: Path to folder to scan
        fs: File system interface for file operations
        logger: Logger interface for warning messages

    Yields:
        PromptData for each markdown file
    """
    if not fs.exists(folder) or not fs.is_dir(folder):
        logger.warning(
            f"folder path '{str(folder)}' does not exist or is not a directory"
        )
        return

    for md_file in fs.glob_markdown(folder):
        try:
            content = fs.read_text(md_file)
            prompt_data = _parse_markdown_file(
                md_file, folder, content, skip_frontmatter, logger=logger
            )
            yield prompt_data
        except Exception as e:
            logger.warning(f"failed to process {md_file}: {e}")
            continue
