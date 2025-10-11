"""Prompt source loading and resolution."""

from pathlib import Path
from .config import Config
from .remote.git import get_local_cache_path, clone_or_update_repo


def get_folder_path(config: Config) -> Path:
    """
    Determine the folder path to scan for prompts based on configuration.

    Args:
        config: Application configuration

    Returns:
        Path to folder containing markdown files

    Raises:
        ValueError: If neither FOLDER nor GIT_URL is configured
    """
    if config.git_url:
        repo_path = get_local_cache_path(config.git_url, config.cache_dir)
        clone_or_update_repo(config.git_url, repo_path, config.auto_pull)

        if config.folder:
            # Use FOLDER as subfolder within the repo
            return repo_path / config.folder
        else:
            return repo_path
    else:
        if not config.folder:
            raise ValueError(
                "Either FOLDER or GIT_URL environment variable is required"
            )
        return Path(config.folder)
