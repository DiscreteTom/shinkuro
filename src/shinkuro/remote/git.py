"""Git repository cloning and caching."""

import os
from pathlib import Path
from giturlparse import parse
from ..interfaces import GitInterface, DefaultGit
from .utils import get_cache_dir


def get_local_cache_path(git_url: str) -> Path:
    """
    Get the local cache path for a git repository.

    Args:
        git_url: Git repository URL

    Returns:
        Local path where the repository would be cached
    """
    cache_dir = get_cache_dir()

    parsed = parse(git_url)
    if not parsed.user or not parsed.name:
        raise ValueError(f"Cannot extract user/repo from git URL: {git_url}")

    return cache_dir / "git" / str(parsed.user) / str(parsed.name)


def clone_or_update_repo(
    git_url: str, local_path: Path, *, git: GitInterface = DefaultGit()
) -> None:
    """
    Clone or update a git repository at the specified local path.

    Args:
        git_url: Git repository URL
        local_path: Local path to clone/update the repository
        git: Git interface for git operations
    """
    if local_path.exists():
        auto_pull = os.getenv("AUTO_PULL", "false").lower() == "true"
        if auto_pull:
            git.pull(local_path)
    else:
        git.clone(git_url, local_path)
