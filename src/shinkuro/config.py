"""Configuration management for shinkuro."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .model import FormatterType


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    folder: Optional[str]
    git_url: Optional[str]
    cache_dir: Path
    auto_pull: bool
    formatter: FormatterType
    auto_discover_args: bool
    skip_frontmatter: bool

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        cache_dir_str = os.getenv("CACHE_DIR")
        if cache_dir_str:
            cache_dir = Path(cache_dir_str)
        else:
            cache_dir = Path.home() / ".shinkuro" / "remote"

        formatter_str = os.getenv("VARIABLE_FORMAT", "brace")
        try:
            formatter = FormatterType(formatter_str)
        except ValueError:
            raise ValueError(
                f"Invalid VARIABLE_FORMAT value: {formatter_str}. Must be one of: {', '.join([f.value for f in FormatterType])}"
            )

        return cls(
            folder=os.getenv("FOLDER"),
            git_url=os.getenv("GIT_URL"),
            cache_dir=cache_dir,
            auto_pull=os.getenv("AUTO_PULL", "false").lower() == "true",
            formatter=formatter,
            auto_discover_args=os.getenv("AUTO_DISCOVER_ARGS", "false").lower()
            == "true",
            skip_frontmatter=os.getenv("SKIP_FRONTMATTER", "false").lower() == "true",
        )
