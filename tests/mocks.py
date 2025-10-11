"""Shared mock implementations for testing."""

from pathlib import Path
from typing import Iterator


class MockFileSystem:
    """Mock file system for testing."""

    def __init__(self, files: dict[Path, str]):
        self.files = files

    def read_text(self, path: Path) -> str:
        return self.files[path]

    def glob_markdown(self, folder: Path) -> Iterator[Path]:
        return (p for p in self.files.keys() if p.suffix == ".md")

    def exists(self, path: Path) -> bool:
        return path in self.files or path == Path("/test")

    def is_dir(self, path: Path) -> bool:
        return path == Path("/test")


class MockLogger:
    """Mock logger for testing."""

    def __init__(self):
        self.warnings = []

    def warning(self, message: str) -> None:
        self.warnings.append(message)


class MockGit:
    """Mock git interface for testing."""

    def __init__(self):
        self.cloned = []
        self.pulled = []

    def clone(self, url: str, path: Path) -> None:
        self.cloned.append({"url": url, "path": path})

    def pull(self, path: Path) -> None:
        self.pulled.append(path)
