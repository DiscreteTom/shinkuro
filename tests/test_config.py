"""Tests for config.py module."""

from pathlib import Path
import pytest
from shinkuro.config import Config
from shinkuro.model import FormatterType


def test_config_from_env_with_all_values(monkeypatch):
    monkeypatch.setenv("FOLDER", "/test/folder")
    monkeypatch.setenv("GIT_URL", "https://github.com/user/repo.git")
    monkeypatch.setenv("CACHE_DIR", "/custom/cache")
    monkeypatch.setenv("AUTO_PULL", "true")
    monkeypatch.setenv("VARIABLE_FORMAT", "dollar")

    config = Config.from_env()

    assert config.folder == "/test/folder"
    assert config.git_url == "https://github.com/user/repo.git"
    assert config.cache_dir == Path("/custom/cache")
    assert config.auto_pull is True
    assert config.formatter == FormatterType.DOLLAR


def test_config_from_env_with_defaults(monkeypatch):
    monkeypatch.delenv("FOLDER", raising=False)
    monkeypatch.delenv("GIT_URL", raising=False)
    monkeypatch.delenv("CACHE_DIR", raising=False)
    monkeypatch.delenv("AUTO_PULL", raising=False)
    monkeypatch.delenv("VARIABLE_FORMAT", raising=False)

    config = Config.from_env()

    assert config.folder is None
    assert config.git_url is None
    assert config.cache_dir == Path.home() / ".shinkuro" / "remote"
    assert config.auto_pull is False
    assert config.formatter == FormatterType.BRACE


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
        formatter=FormatterType.DOLLAR,
        auto_discover_args=True,
        skip_frontmatter=False,
    )

    assert config.folder == "/test"
    assert config.git_url == "https://example.com/repo.git"
    assert config.cache_dir == Path("/cache")
    assert config.auto_pull is True
    assert config.formatter == FormatterType.DOLLAR
    assert config.auto_discover_args is True


def test_config_variable_format_brace(monkeypatch):
    monkeypatch.delenv("FOLDER", raising=False)
    monkeypatch.delenv("GIT_URL", raising=False)
    monkeypatch.setenv("VARIABLE_FORMAT", "brace")

    config = Config.from_env()
    assert config.formatter == FormatterType.BRACE


def test_config_variable_format_dollar(monkeypatch):
    monkeypatch.delenv("FOLDER", raising=False)
    monkeypatch.delenv("GIT_URL", raising=False)
    monkeypatch.setenv("VARIABLE_FORMAT", "dollar")

    config = Config.from_env()
    assert config.formatter == FormatterType.DOLLAR


def test_config_variable_format_invalid(monkeypatch):
    monkeypatch.delenv("FOLDER", raising=False)
    monkeypatch.delenv("GIT_URL", raising=False)
    monkeypatch.setenv("VARIABLE_FORMAT", "invalid")

    with pytest.raises(ValueError, match="Invalid VARIABLE_FORMAT value: invalid"):
        Config.from_env()


def test_config_auto_discover_args_default(monkeypatch):
    monkeypatch.delenv("FOLDER", raising=False)
    monkeypatch.delenv("GIT_URL", raising=False)
    monkeypatch.delenv("AUTO_DISCOVER_ARGS", raising=False)

    config = Config.from_env()
    assert config.auto_discover_args is False


def test_config_auto_discover_args_true(monkeypatch):
    monkeypatch.delenv("FOLDER", raising=False)
    monkeypatch.delenv("GIT_URL", raising=False)
    monkeypatch.setenv("AUTO_DISCOVER_ARGS", "true")

    config = Config.from_env()
    assert config.auto_discover_args is True


def test_config_skip_frontmatter_default(monkeypatch):
    monkeypatch.delenv("SKIP_FRONTMATTER", raising=False)
    config = Config.from_env()
    assert config.skip_frontmatter is False


def test_config_skip_frontmatter_true(monkeypatch):
    monkeypatch.setenv("SKIP_FRONTMATTER", "true")
    config = Config.from_env()
    assert config.skip_frontmatter is True
