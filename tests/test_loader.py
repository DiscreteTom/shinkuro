"""Tests for loader.py module."""

import pytest
from pathlib import Path
from shinkuro.loader import get_folder_path


def test_get_folder_path_local_folder():
    result = get_folder_path(
        folder="/test/folder",
        git_url=None,
        cache_dir=Path("/cache"),
        auto_pull=False,
    )
    assert result == Path("/test/folder")


def test_get_folder_path_no_config():
    with pytest.raises(ValueError, match="Either folder or git-url"):
        get_folder_path(
            folder=None,
            git_url=None,
            cache_dir=Path("/cache"),
            auto_pull=False,
        )


def test_get_folder_path_git_only(tmp_path, monkeypatch):
    # Mock git operations
    cloned = []

    def mock_clone(url, path, auto_pull, git=None):
        cloned.append(path)
        path.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr("shinkuro.loader.clone_or_update_repo", mock_clone)

    result = get_folder_path(
        folder=None,
        git_url="https://github.com/user/repo.git",
        cache_dir=tmp_path,
        auto_pull=False,
    )

    assert result == tmp_path / "git" / "user" / "repo"
    assert len(cloned) == 1


def test_get_folder_path_git_with_subfolder(tmp_path, monkeypatch):
    # Mock git operations
    def mock_clone(url, path, auto_pull, git=None):
        path.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr("shinkuro.loader.clone_or_update_repo", mock_clone)

    result = get_folder_path(
        folder="prompts",
        git_url="https://github.com/user/repo.git",
        cache_dir=tmp_path,
        auto_pull=False,
    )

    assert result == tmp_path / "git" / "user" / "repo" / "prompts"


def test_get_folder_path_git_with_auto_pull(tmp_path, monkeypatch):
    # Mock git operations
    pulled = []

    def mock_clone(url, path, auto_pull, git=None):
        path.mkdir(parents=True, exist_ok=True)
        if auto_pull:
            pulled.append(path)

    monkeypatch.setattr("shinkuro.loader.clone_or_update_repo", mock_clone)

    result = get_folder_path(
        folder=None,
        git_url="https://github.com/user/repo.git",
        cache_dir=tmp_path,
        auto_pull=True,
    )

    assert result == tmp_path / "git" / "user" / "repo"
    assert len(pulled) == 1
