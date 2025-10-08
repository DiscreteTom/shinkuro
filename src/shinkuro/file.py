"""Local file-based prompt loader."""

import frontmatter
import re
import string
import sys
from pathlib import Path
from typing import Iterator, List, Optional
from dataclasses import dataclass


@dataclass
class Argument:
    """Template argument for prompt substitution.

    Attributes:
        name: Parameter name for template substitution
        description: Human-readable description of the parameter
        default: Default value if parameter not provided
    """

    name: str
    description: str
    default: Optional[str] = None


@dataclass
class PromptData:
    """Complete prompt data loaded from markdown file.

    Attributes:
        name: Unique identifier for the prompt
        title: Display title for the prompt
        description: Brief description of prompt purpose
        arguments: Template parameters this prompt accepts
        content: Template content with validated variable substitution
    """

    name: str
    title: str
    description: str
    arguments: List[Argument]
    content: str


def scan_markdown_files(folder_path: str) -> Iterator[PromptData]:
    """
    Scan folder recursively for markdown files.

    Args:
        folder_path: Path to folder to scan

    Yields:
        PromptData for each markdown file
    """
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        print(
            f"Warning: folder path '{folder_path}' does not exist or is not a directory",
            file=sys.stderr,
        )
        return

    for md_file in folder.rglob("*.md"):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Use frontmatter name if available, convert to string if needed, otherwise use filename
            frontmatter_name = post.metadata.get("name")
            if frontmatter_name is None:
                name = md_file.stem
            elif isinstance(frontmatter_name, str):
                name = frontmatter_name
            else:
                print(
                    f"Warning: 'name' field in {md_file} is not a string, converting to string",
                    file=sys.stderr,
                )
                name = str(frontmatter_name)

            # Get title from frontmatter, convert to string if needed, default to filename
            frontmatter_title = post.metadata.get("title")
            if frontmatter_title is None:
                title = md_file.stem
            elif isinstance(frontmatter_title, str):
                title = frontmatter_title
            else:
                print(
                    f"Warning: 'title' field in {md_file} is not a string, converting to string",
                    file=sys.stderr,
                )
                title = str(frontmatter_title)

            # Get description from frontmatter, convert to string if needed
            frontmatter_description = post.metadata.get("description")
            if frontmatter_description is None:
                description = f"Prompt from {md_file.relative_to(folder)}"
            elif isinstance(frontmatter_description, str):
                description = frontmatter_description
            else:
                print(
                    f"Warning: 'description' field in {md_file} is not a string, converting to string",
                    file=sys.stderr,
                )
                description = str(frontmatter_description)

            # Get arguments from frontmatter
            frontmatter_arguments = post.metadata.get("arguments", [])
            if not isinstance(frontmatter_arguments, list):
                if frontmatter_arguments is not None:
                    print(
                        f"Warning: 'arguments' field in {md_file} is not a list, ignoring",
                        file=sys.stderr,
                    )
                frontmatter_arguments = []

            arguments = []
            for arg_data in frontmatter_arguments:
                if isinstance(arg_data, dict):
                    # Handle name field - required
                    arg_name = arg_data.get("name")
                    if arg_name is None or arg_name == "":
                        print(
                            f"Warning: argument 'name' field is missing or empty in {md_file}, skipping argument",
                            file=sys.stderr,
                        )
                        continue
                    elif not isinstance(arg_name, str):
                        print(
                            f"Warning: argument 'name' field in {md_file} is not a string, converting to string",
                            file=sys.stderr,
                        )
                        arg_name = str(arg_name)

                    # Validate arg name format
                    if not re.match(r"^[a-zA-Z0-9_]+$", arg_name):
                        print(
                            f"Warning: argument name '{arg_name}' in {md_file} contains invalid characters, skipping argument",
                            file=sys.stderr,
                        )
                        continue

                    # Handle description field
                    arg_description = arg_data.get("description", "")
                    if arg_description != "" and not isinstance(arg_description, str):
                        print(
                            f"Warning: argument 'description' field in {md_file} is not a string, converting to string",
                            file=sys.stderr,
                        )
                        arg_description = str(arg_description)

                    # Handle default field
                    arg_default = arg_data.get("default")
                    if arg_default is not None and not isinstance(arg_default, str):
                        print(
                            f"Warning: argument 'default' field in {md_file} is not a string, converting to string",
                            file=sys.stderr,
                        )
                        arg_default = str(arg_default)

                    arguments.append(
                        Argument(
                            name=arg_name,
                            description=arg_description,
                            default=arg_default,
                        )
                    )
                else:
                    print(
                        f"Warning: argument item in {md_file} is not a dict, skipping",
                        file=sys.stderr,
                    )

            content = post.content

            # Validate format fields are safe (only alphanumeric and underscore)
            formatter = string.Formatter()
            is_safe = True
            for literal_text, field_name, format_spec, conversion in formatter.parse(
                content
            ):
                if field_name and not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", field_name):
                    is_safe = False
                    break

            if not is_safe:
                print(
                    f"Warning: content in {md_file} contains unsafe template variables, skipping file",
                    file=sys.stderr,
                )
                continue  # Skip this file

            yield PromptData(name, title, description, arguments, content)
        except Exception as e:
            print(
                f"Warning: failed to process {md_file}: {e}",
                file=sys.stderr,
            )
            continue
