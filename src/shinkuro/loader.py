"""Prompt source loading and resolution."""

from pathlib import Path
from .remote.git import get_local_cache_path, clone_or_update_repo
from typing import Optional


def get_folder_path(
    folder: Optional[str],
    git_url: Optional[str],
    cache_dir: Path,
    auto_pull: bool,
) -> Path:
    """
    Determine the folder path to scan for prompts.

    Args:
        folder: Path to local folder or subfolder within git repo
        git_url: Git repository URL
        cache_dir: Directory to cache remote repositories
        auto_pull: Whether to refresh local cache on startup

    Returns:
        Path to folder containing markdown files

    Raises:
        ValueError: If neither folder nor git_url is provided
    """
    if git_url:
        repo_path = get_local_cache_path(git_url, cache_dir)
        clone_or_update_repo(git_url, repo_path, auto_pull)

        if folder:
            # Use folder as subfolder within the repo
            return repo_path / folder
        else:
            return repo_path
    else:
        if not folder:
            raise ValueError("Either folder or git-url must be provided")
        return Path(folder)
