"""Tests for file/scan.py module."""

from pathlib import Path
from shinkuro.file.scan import (
    scan_markdown_files,
    _extract_string_field,
    _parse_argument,
    _parse_arguments,
    _validate_template_variables,
    _parse_markdown_file,
)
from shinkuro.model import Argument
from .mocks import MockFileSystem, MockLogger


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


def test_parse_argument_invalid_name():
    logger = MockLogger()
    arg = _parse_argument({"name": "123invalid"}, Path("/test.md"), logger=logger)
    assert arg is None
    assert "invalid characters" in logger.warnings[0]


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


def test_validate_template_variables_valid():
    assert _validate_template_variables("Hello {name}") is True
    assert _validate_template_variables("Hello {_name}") is True
    assert _validate_template_variables("Hello {name123}") is True


def test_validate_template_variables_invalid():
    assert _validate_template_variables("Hello {123}") is False
    assert _validate_template_variables("Hello {name-invalid}") is False
    assert _validate_template_variables("Hello {9var}") is False


def test_parse_markdown_file_simple():
    logger = MockLogger()
    content = "Hello world"
    result = _parse_markdown_file(
        Path("/test/file.md"), Path("/test"), content, logger=logger
    )
    assert result is not None
    assert result.name == "file"
    assert result.title == "file"
    assert result.content == "Hello world"


def test_parse_markdown_file_with_frontmatter():
    logger = MockLogger()
    content = """---
name: greeting
title: Greeting Prompt
description: A greeting
arguments:
  - name: user
    description: User name
---
Hello {user}"""
    result = _parse_markdown_file(
        Path("/test/file.md"), Path("/test"), content, logger=logger
    )
    assert result is not None
    assert result.name == "greeting"
    assert result.title == "Greeting Prompt"
    assert result.description == "A greeting"
    assert len(result.arguments) == 1
    assert result.arguments[0].name == "user"


def test_parse_markdown_file_unsafe_template():
    logger = MockLogger()
    content = "Hello {123}"
    result = _parse_markdown_file(
        Path("/test/file.md"), Path("/test"), content, logger=logger
    )
    assert result is None
    assert len(logger.warnings) == 1
    assert "unsafe template variables" in logger.warnings[0]


def test_scan_markdown_files_basic():
    fs = MockFileSystem(
        {
            Path("/test/file1.md"): "Content 1",
            Path("/test/file2.md"): "Content 2",
        }
    )
    logger = MockLogger()
    results = list(scan_markdown_files(Path("/test"), fs=fs, logger=logger))
    assert len(results) == 2


def test_scan_markdown_files_folder_not_exists():
    fs = MockFileSystem({})
    logger = MockLogger()
    results = list(scan_markdown_files(Path("/nonexistent"), fs=fs, logger=logger))
    assert len(results) == 0
    assert len(logger.warnings) == 1
    assert "does not exist" in logger.warnings[0]


def test_scan_markdown_files_with_error():
    fs = MockFileSystem({Path("/test/bad.md"): "---\ninvalid yaml: [\n---\nContent"})
    logger = MockLogger()
    results = list(scan_markdown_files(Path("/test"), fs=fs, logger=logger))
    assert len(results) == 0
    assert len(logger.warnings) == 1
    assert "failed to process" in logger.warnings[0]


def test_scan_markdown_files_skips_invalid():
    fs = MockFileSystem(
        {
            Path("/test/good.md"): "Good content",
            Path("/test/bad.md"): "Bad {123}",
        }
    )
    logger = MockLogger()
    results = list(scan_markdown_files(Path("/test"), fs=fs, logger=logger))
    assert len(results) == 1
    assert results[0].name == "good"


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
