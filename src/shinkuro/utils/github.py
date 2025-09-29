"""Git repository loader with local caching."""

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


def clone_or_update_repo(git_url: str) -> str:
    """
    Clone or update a git repository and return the local path.

    Args:
        git_url: Git repository URL

    Returns:
        Local path to the cloned repository
    """
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Extract repo name using Path.stem
    repo_name = Path(git_url.rstrip("/")).stem
    if not repo_name:
        raise ValueError(f"Invalid git URL: {git_url}")

    # Remove .git suffix if present
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    # Create local directory path: ~/.shinkuro/remote/git/{repo_name}
    local_path = cache_dir / "git" / repo_name

    auto_pull = os.getenv("AUTO_PULL", "false").lower() == "true"

    try:
        if local_path.exists():
            if auto_pull:
                # Update existing repo
                repo = Repo(local_path)
                repo.remotes.origin.pull()
        else:
            # Clone repository
            Repo.clone_from(git_url, local_path, depth=1)

        return str(local_path)

    except GitCommandError as e:
        raise RuntimeError(f"Failed to clone/update repository {git_url}: {e}")
