"""Tests for remote/git.py module."""

import pytest
from pathlib import Path
from shinkuro.remote.git import get_local_cache_path, clone_or_update_repo
from .mocks import MockGit


def test_get_local_cache_path_github():
    cache_dir = Path("/cache")
    git_url = "https://github.com/user/repo.git"

    result = get_local_cache_path(git_url, cache_dir)

    assert result == Path("/cache/git/user/repo")


def test_get_local_cache_path_ssh():
    cache_dir = Path("/cache")
    git_url = "git@github.com:user/repo.git"

    result = get_local_cache_path(git_url, cache_dir)

    assert result == Path("/cache/git/user/repo")


def test_get_local_cache_path_gitlab():
    cache_dir = Path("/cache")
    git_url = "https://gitlab.com/user/repo.git"

    result = get_local_cache_path(git_url, cache_dir)

    assert result == Path("/cache/git/user/repo")


def test_get_local_cache_path_gitlab_ssh():
    cache_dir = Path("/cache")
    git_url = "git@gitlab.com:user/repo.git"

    result = get_local_cache_path(git_url, cache_dir)

    assert result == Path("/cache/git/user/repo")


def test_get_local_cache_path_with_username():
    cache_dir = Path("/cache")
    git_url = "https://username@github.com/owner/repo.git"

    result = get_local_cache_path(git_url, cache_dir)

    assert result == Path("/cache/git/owner/repo")


def test_get_local_cache_path_with_credentials():
    cache_dir = Path("/cache")
    git_url = "https://username:token@github.com/owner/repo.git"

    result = get_local_cache_path(git_url, cache_dir)

    assert result == Path("/cache/git/owner/repo")


def test_get_local_cache_path_gitlab_with_credentials():
    cache_dir = Path("/cache")
    git_url = "https://oauth2:token@gitlab.com/owner/repo.git"

    result = get_local_cache_path(git_url, cache_dir)

    assert result == Path("/cache/git/owner/repo")


def test_get_local_cache_path_invalid_url():
    cache_dir = Path("/cache")
    git_url = "invalid-url"

    with pytest.raises(ValueError, match="Cannot extract user/repo"):
        get_local_cache_path(git_url, cache_dir)


def test_clone_or_update_repo_clone_new(tmp_path):
    git = MockGit()
    git_url = "https://github.com/user/repo.git"
    local_path = tmp_path / "repo"

    clone_or_update_repo(git_url, local_path, False, git=git)

    assert len(git.cloned) == 1
    assert git.cloned[0]["url"] == git_url
    assert git.cloned[0]["path"] == local_path
    assert len(git.pulled) == 0


def test_clone_or_update_repo_exists_no_pull(tmp_path):
    git = MockGit()
    git_url = "https://github.com/user/repo.git"
    local_path = tmp_path / "repo"
    local_path.mkdir()

    clone_or_update_repo(git_url, local_path, False, git=git)

    assert len(git.cloned) == 0
    assert len(git.pulled) == 0


def test_clone_or_update_repo_exists_with_pull(tmp_path):
    git = MockGit()
    git_url = "https://github.com/user/repo.git"
    local_path = tmp_path / "repo"
    local_path.mkdir()

    clone_or_update_repo(git_url, local_path, True, git=git)

    assert len(git.cloned) == 0
    assert len(git.pulled) == 1
    assert git.pulled[0] == local_path
