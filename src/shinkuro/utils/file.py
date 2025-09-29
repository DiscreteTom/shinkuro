"""File-based prompt loader."""

import frontmatter
from pathlib import Path
from typing import Iterator, Tuple


def scan_markdown_files(folder_path: str) -> Iterator[Tuple[str, str, str]]:
    """
    Scan folder recursively for markdown files.

    Args:
        folder_path: Path to folder to scan

    Yields:
        Tuple of (name, content, description) for each markdown file
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

            # Get description from frontmatter, ensure it's a string
            desc = post.metadata.get("description")
            if isinstance(desc, str):
                description = desc
            else:
                description = f"Prompt from {md_file.relative_to(folder)}"

            yield name, content, description
        except Exception:
            continue
