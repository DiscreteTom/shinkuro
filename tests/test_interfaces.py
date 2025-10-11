"""Tests for interfaces.py module."""

import sys
from io import StringIO
from shinkuro.interfaces import DefaultFileSystem, DefaultLogger, DefaultGit


def test_default_filesystem_read_text(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello world", encoding="utf-8")

    fs = DefaultFileSystem()
    content = fs.read_text(test_file)

    assert content == "Hello world"


def test_default_filesystem_glob_markdown(tmp_path):
    (tmp_path / "file1.md").write_text("content1")
    (tmp_path / "file2.md").write_text("content2")
    (tmp_path / "file3.txt").write_text("content3")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file4.md").write_text("content4")

    fs = DefaultFileSystem()
    md_files = list(fs.glob_markdown(tmp_path))

    assert len(md_files) == 3
    assert all(f.suffix == ".md" for f in md_files)


def test_default_filesystem_exists(tmp_path):
    test_file = tmp_path / "exists.txt"
    test_file.write_text("content")

    fs = DefaultFileSystem()

    assert fs.exists(test_file) is True
    assert fs.exists(tmp_path / "nonexistent.txt") is False


def test_default_filesystem_is_dir(tmp_path):
    test_file = tmp_path / "file.txt"
    test_file.write_text("content")
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()

    fs = DefaultFileSystem()

    assert fs.is_dir(test_dir) is True
    assert fs.is_dir(test_file) is False


def test_default_logger_warning():
    logger = DefaultLogger()
    captured = StringIO()
    old_stderr = sys.stderr
    sys.stderr = captured

    logger.warning("test warning message")

    sys.stderr = old_stderr
    output = captured.getvalue()

    assert "Warning: test warning message" in output


def test_default_git_clone(tmp_path, monkeypatch):
    clone_called = []

    class MockRepo:
        @classmethod
        def clone_from(cls, url, path, depth):
            clone_called.append({"url": url, "path": path, "depth": depth})

    monkeypatch.setattr("shinkuro.interfaces.Repo", MockRepo)

    git = DefaultGit()
    target = tmp_path / "repo"
    git.clone("https://github.com/user/repo.git", target)

    assert len(clone_called) == 1
    assert clone_called[0]["url"] == "https://github.com/user/repo.git"
    assert clone_called[0]["path"] == target
    assert clone_called[0]["depth"] == 1
    assert target.parent.exists()


def test_default_git_pull(tmp_path, monkeypatch):
    pull_called = []

    class MockRemote:
        def pull(self):
            pull_called.append(True)

    class MockRemotes:
        origin = MockRemote()

    class MockRepo:
        def __init__(self, path):
            self.path = path
            self.remotes = MockRemotes()

    monkeypatch.setattr("shinkuro.interfaces.Repo", MockRepo)

    git = DefaultGit()
    git.pull(tmp_path)

    assert len(pull_called) == 1
