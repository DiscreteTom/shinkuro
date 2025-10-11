"""Interfaces for dependency injection and testing."""

import sys
from pathlib import Path
from typing import Iterator, Protocol
from git import Repo


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


class LoggerInterface(Protocol):
    """Protocol for logging operations."""

    def warning(self, message: str) -> None:
        """Log a warning message."""
        ...


class GitInterface(Protocol):
    """Protocol for git operations."""

    def clone(self, url: str, path: Path) -> None:
        """Clone a git repository."""
        ...

    def pull(self, path: Path) -> None:
        """Pull latest changes from remote."""
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


class DefaultLogger:
    """Default logger implementation using stderr."""

    def warning(self, message: str) -> None:
        print(f"Warning: {message}", file=sys.stderr)


class DefaultGit:
    """Default git implementation using GitPython."""

    def clone(self, url: str, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        Repo.clone_from(url, path, depth=1)

    def pull(self, path: Path) -> None:
        repo = Repo(path)
        repo.remotes.origin.pull()
