"""Local file-based prompt loader."""

import frontmatter
from pathlib import Path
from typing import Iterator, List, Optional
from dataclasses import dataclass


@dataclass
class Argument:
    name: str
    description: str
    default: Optional[str] = None


@dataclass
class PromptData:
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
        return

    for md_file in folder.rglob("*.md"):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Use frontmatter name if available and is a string, otherwise use filename
            frontmatter_name = post.metadata.get("name")
            if isinstance(frontmatter_name, str):
                name = frontmatter_name
            else:
                name = md_file.stem

            content = post.content

            # Get title from frontmatter, ensure it's a string, default to filename
            title_data = post.metadata.get("title")
            if isinstance(title_data, str):
                title = title_data
            else:
                title = md_file.stem

            # Get description from frontmatter, ensure it's a string
            desc = post.metadata.get("description")
            if isinstance(desc, str):
                description = desc
            else:
                description = f"Prompt from {md_file.relative_to(folder)}"

            # Get arguments from frontmatter
            arguments_data = post.metadata.get("arguments", [])
            if not isinstance(arguments_data, list):
                arguments_data = []

            arguments = []
            for arg_data in arguments_data:
                if isinstance(arg_data, dict):
                    arguments.append(
                        Argument(
                            name=arg_data.get("name", ""),
                            description=arg_data.get("description", ""),
                            default=arg_data.get("default"),
                        )
                    )

            yield PromptData(name, title, description, arguments, content)
        except Exception:
            continue
