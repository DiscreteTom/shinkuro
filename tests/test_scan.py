"""Tests for file/scan.py module."""

from pathlib import Path
from shinkuro.file.scan import (
    scan_markdown_files,
    _extract_string_field,
    _parse_argument,
    _parse_arguments,
    _parse_markdown_file,
)
from shinkuro.model import Argument
from .mocks import MockFileSystem, MockLogger
from .fixtures import create_markdown_file_content, create_test_files


def test_extract_string_field_with_string():
    logger = MockLogger()
    result = _extract_string_field(
        {"name": "test"}, "name", "default", Path("/test.md"), logger=logger
    )
    assert result == "test"
    assert len(logger.warnings) == 0


def test_extract_string_field_with_none():
    logger = MockLogger()
    result = _extract_string_field(
        {}, "name", "default", Path("/test.md"), logger=logger
    )
    assert result == "default"
    assert len(logger.warnings) == 0


def test_extract_string_field_with_non_string():
    logger = MockLogger()
    result = _extract_string_field(
        {"name": 123}, "name", "default", Path("/test.md"), logger=logger
    )
    assert result == "123"
    assert len(logger.warnings) == 1
    assert "'name' field in /test.md is not a string" in logger.warnings[0]


def test_parse_argument_valid():
    logger = MockLogger()
    arg = _parse_argument(
        {"name": "user", "description": "User name", "default": "guest"},
        Path("/test.md"),
        logger=logger,
    )
    assert arg == Argument(name="user", description="User name", default="guest")
    assert len(logger.warnings) == 0


def test_parse_argument_not_dict():
    logger = MockLogger()
    arg = _parse_argument("invalid", Path("/test.md"), logger=logger)
    assert arg is None
    assert len(logger.warnings) == 1


def test_parse_argument_missing_name():
    logger = MockLogger()
    arg = _parse_argument({"description": "test"}, Path("/test.md"), logger=logger)
    assert arg is None
    assert len(logger.warnings) == 1


def test_parse_argument_name_with_underscore():
    logger = MockLogger()
    arg = _parse_argument({"name": "_valid"}, Path("/test.md"), logger=logger)
    assert arg is not None
    assert arg.name == "_valid"


def test_parse_arguments_valid_list():
    logger = MockLogger()
    args = _parse_arguments(
        {"arguments": [{"name": "arg1"}, {"name": "arg2"}]},
        Path("/test.md"),
        logger=logger,
    )
    assert len(args) == 2
    assert args[0].name == "arg1"
    assert args[1].name == "arg2"


def test_parse_arguments_not_list():
    logger = MockLogger()
    args = _parse_arguments({"arguments": "invalid"}, Path("/test.md"), logger=logger)
    assert len(args) == 0
    assert len(logger.warnings) == 1


def test_parse_markdown_file_simple():
    logger = MockLogger()
    content = "Hello world"
    result = _parse_markdown_file(
        Path("/test/file.md"), Path("/test"), content, False, logger=logger
    )
    assert result is not None
    assert result.name == "file"
    assert result.title == "file"
    assert result.content == "Hello world"


def test_parse_markdown_file_with_frontmatter():
    logger = MockLogger()
    content = create_markdown_file_content(
        content="Hello {user}",
        name="greeting",
        title="Greeting Prompt",
        description="A greeting",
        arguments=[{"name": "user", "description": "User name"}],
    )
    result = _parse_markdown_file(
        Path("/test/file.md"), Path("/test"), content, False, logger=logger
    )
    assert result is not None
    assert result.name == "greeting"
    assert result.title == "Greeting Prompt"
    assert result.description == "A greeting"
    assert len(result.arguments) == 1
    assert result.arguments[0].name == "user"


def test_scan_markdown_files_basic():
    fs = MockFileSystem(
        create_test_files(
            {
                "/test/file1.md": "Content 1",
                "/test/file2.md": "Content 2",
            }
        )
    )
    logger = MockLogger()
    results = list(scan_markdown_files(Path("/test"), False, fs=fs, logger=logger))
    assert len(results) == 2


def test_scan_markdown_files_folder_not_exists():
    fs = MockFileSystem({})
    logger = MockLogger()
    results = list(
        scan_markdown_files(Path("/nonexistent"), False, fs=fs, logger=logger)
    )
    assert len(results) == 0
    assert len(logger.warnings) == 1
    assert "does not exist" in logger.warnings[0]


def test_scan_markdown_files_with_error():
    fs = MockFileSystem(
        create_test_files({"/test/bad.md": "---\ninvalid yaml: [\n---\nContent"})
    )
    logger = MockLogger()
    results = list(scan_markdown_files(Path("/test"), False, fs=fs, logger=logger))
    assert len(results) == 0
    assert len(logger.warnings) == 1
    assert "failed to process" in logger.warnings[0]


def test_parse_argument_non_string_name():
    logger = MockLogger()
    arg = _parse_argument({"name": True}, Path("/test.md"), logger=logger)
    assert arg is not None
    assert arg.name == "True"
    assert len(logger.warnings) == 1


def test_parse_argument_non_string_description():
    logger = MockLogger()
    arg = _parse_argument(
        {"name": "test", "description": 123}, Path("/test.md"), logger=logger
    )
    assert arg is not None
    assert arg.description == "123"
    assert len(logger.warnings) == 1


def test_parse_argument_non_string_default():
    logger = MockLogger()
    arg = _parse_argument(
        {"name": "test", "default": 123}, Path("/test.md"), logger=logger
    )
    assert arg is not None
    assert arg.default == "123"
    assert len(logger.warnings) == 1


def test_parse_markdown_file_skip_frontmatter():
    content = """---
name: "custom-name"
title: "Custom Title"
description: "Custom description"
arguments:
  - name: "user"
    description: "User name"
---

Hello {user}!"""

    md_file = Path("/test/hello.md")
    folder = Path("/test")
    logger = MockLogger()

    result = _parse_markdown_file(md_file, folder, content, True, logger=logger)

    assert result.name == "hello"
    assert result.title == "hello"
    assert result.description == "Prompt from hello.md"
    assert result.arguments == []
    assert result.content == content


def test_scan_markdown_files_skip_frontmatter():
    fs = MockFileSystem(
        {
            Path(
                "/test/hello.md"
            ): """---
name: "custom"
---
Hello world!""",
            Path("/test/nested/greet.md"): "Hi there!",
        }
    )

    results = list(scan_markdown_files(Path("/test"), True, fs=fs))

    assert len(results) == 2

    hello = next(r for r in results if r.name == "hello")
    assert hello.title == "hello"
    assert hello.description == "Prompt from hello.md"
    assert hello.arguments == []

    greet = next(r for r in results if r.name == "greet")
    assert greet.title == "greet"
    assert greet.description == "Prompt from nested/greet.md"
    assert greet.arguments == []
