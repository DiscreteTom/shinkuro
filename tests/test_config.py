"""Tests for config.py module."""

from pathlib import Path
from shinkuro.config import Config


def test_config_from_env_with_all_values(monkeypatch):
    monkeypatch.setenv("FOLDER", "/test/folder")
    monkeypatch.setenv("GIT_URL", "https://github.com/user/repo.git")
    monkeypatch.setenv("CACHE_DIR", "/custom/cache")
    monkeypatch.setenv("AUTO_PULL", "true")

    config = Config.from_env()

    assert config.folder == "/test/folder"
    assert config.git_url == "https://github.com/user/repo.git"
    assert config.cache_dir == Path("/custom/cache")
    assert config.auto_pull is True


def test_config_from_env_with_defaults(monkeypatch):
    monkeypatch.delenv("FOLDER", raising=False)
    monkeypatch.delenv("GIT_URL", raising=False)
    monkeypatch.delenv("CACHE_DIR", raising=False)
    monkeypatch.delenv("AUTO_PULL", raising=False)

    config = Config.from_env()

    assert config.folder is None
    assert config.git_url is None
    assert config.cache_dir == Path.home() / ".shinkuro" / "remote"
    assert config.auto_pull is False


def test_config_auto_pull_false_values(monkeypatch):
    monkeypatch.delenv("FOLDER", raising=False)
    monkeypatch.delenv("GIT_URL", raising=False)

    for value in ["false", "False", "FALSE", "no", "0", ""]:
        monkeypatch.setenv("AUTO_PULL", value)
        config = Config.from_env()
        assert config.auto_pull is False


def test_config_auto_pull_true_values(monkeypatch):
    monkeypatch.delenv("FOLDER", raising=False)
    monkeypatch.delenv("GIT_URL", raising=False)

    for value in ["true", "True", "TRUE"]:
        monkeypatch.setenv("AUTO_PULL", value)
        config = Config.from_env()
        assert config.auto_pull is True


def test_config_dataclass_creation():
    config = Config(
        folder="/test",
        git_url="https://example.com/repo.git",
        cache_dir=Path("/cache"),
        auto_pull=True,
    )

    assert config.folder == "/test"
    assert config.git_url == "https://example.com/repo.git"
    assert config.cache_dir == Path("/cache")
    assert config.auto_pull is True
