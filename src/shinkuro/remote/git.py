"""Git repository cloning and caching."""

from pathlib import Path
from giturlparse import parse
from ..interfaces import GitInterface, DefaultGit


def get_local_cache_path(git_url: str, cache_dir: Path) -> Path:
    """
    Get the local cache path for a git repository.

    Args:
        git_url: Git repository URL
        cache_dir: Base cache directory

    Returns:
        Local path where the repository would be cached
    """
    parsed = parse(git_url)
    owner = getattr(parsed, "owner", None)
    name = getattr(parsed, "name", None)

    if not owner or not name:
        raise ValueError(f"Cannot extract user/repo from git URL: {git_url}")

    return cache_dir / "git" / str(owner) / str(name)


def clone_or_update_repo(
    git_url: str, local_path: Path, auto_pull: bool, *, git: GitInterface = DefaultGit()
) -> None:
    """
    Clone or update a git repository at the specified local path.

    Args:
        git_url: Git repository URL
        local_path: Local path to clone/update the repository
        auto_pull: Whether to pull latest changes if repo exists
        git: Git interface for git operations
    """
    if local_path.exists():
        if auto_pull:
            git.pull(local_path)
    else:
        git.clone(git_url, local_path)
