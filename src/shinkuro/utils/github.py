"""GitHub repository loader with local caching."""

import os
from pathlib import Path
from git import Repo
from git.exc import GitCommandError


def get_cache_dir() -> Path:
    """Get the cache directory for storing cloned repositories."""
    cache_dir = os.getenv("CACHE_DIR")
    if cache_dir:
        return Path(cache_dir)

    # Default to ~/.shinkuro/remote
    home = Path.home()
    return home / ".shinkuro" / "remote"


def clone_or_update_repo(github_repo: str) -> str:
    """
    Clone or update a GitHub repository and return the local path.

    Args:
        github_repo: GitHub repository in format "owner/repo"

    Returns:
        Local path to the cloned repository
    """
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Create local directory path maintaining original structure
    local_path = cache_dir / "github" / github_repo

    github_url_ssh = f"git@github.com:{github_repo}.git"
    github_url_https = f"https://github.com/{github_repo}.git"
    auto_pull = os.getenv("AUTO_PULL", "false").lower() == "true"

    try:
        if local_path.exists():
            if auto_pull:
                # Update existing repo
                repo = Repo(local_path)
                repo.remotes.origin.pull()
        else:
            # Try SSH first, fallback to HTTPS
            try:
                Repo.clone_from(github_url_ssh, local_path, depth=1)
            except GitCommandError:
                Repo.clone_from(github_url_https, local_path, depth=1)

        return str(local_path)

    except GitCommandError as e:
        raise RuntimeError(f"Failed to clone/update repository {github_repo}: {e}")
