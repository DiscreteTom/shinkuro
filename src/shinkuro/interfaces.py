"""Interfaces for dependency injection and testing."""

from pathlib import Path
from typing import Iterator, Protocol


class FileSystemInterface(Protocol):
    """Protocol for file system operations."""

    def read_text(self, path: Path) -> str:
        """Read text content from a file."""
        ...

    def glob_markdown(self, folder: Path) -> Iterator[Path]:
        """Find all markdown files in folder recursively."""
        ...

    def exists(self, path: Path) -> bool:
        """Check if path exists."""
        ...

    def is_dir(self, path: Path) -> bool:
        """Check if path is a directory."""
        ...


class DefaultFileSystem:
    """Default file system implementation using pathlib."""

    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def glob_markdown(self, folder: Path) -> Iterator[Path]:
        return folder.rglob("*.md")

    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_dir(self, path: Path) -> bool:
        return path.is_dir()
