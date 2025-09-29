"""Git repository cloning and caching."""

import os
from git import Repo
from git.exc import GitCommandError
from .utils import get_cache_dir
from giturlparse import parse


def extract_user_repo(git_url: str) -> tuple[str, str]:
    """Extract user and repo name from git URL."""

    parsed = parse(git_url)
    if not parsed.user or not parsed.name:
        raise ValueError(f"Cannot extract user/repo from git URL: {git_url}")

    return parsed.user, parsed.name


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

    # Extract user and repo name
    user, repo = extract_user_repo(git_url)

    # Create local directory path: ~/.shinkuro/remote/git/{user}/{repo}
    local_path = cache_dir / "git" / user / repo

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
