"""Tests for formatters module."""

import pytest
from shinkuro.formatters import (
    BraceFormatter,
    DollarFormatter,
    get_formatter,
    validate_variable_name,
)
from shinkuro.model import FormatterType


def test_validate_variable_name_valid():
    assert validate_variable_name("user") is True
    assert validate_variable_name("_user") is True
    assert validate_variable_name("user123") is True
    assert validate_variable_name("User") is True


def test_validate_variable_name_invalid():
    assert validate_variable_name("123user") is False
    assert validate_variable_name("user-name") is False
    assert validate_variable_name("user name") is False
    assert validate_variable_name("") is False


def test_brace_formatter_extract_arguments():
    formatter = BraceFormatter()
    arguments = formatter.extract_arguments("Hello {user} from {project}")
    assert arguments == {"user", "project"}


def test_brace_formatter_extract_arguments_invalid():
    formatter = BraceFormatter()
    with pytest.raises(ValueError, match="Invalid variable name"):
        formatter.extract_arguments("Hello {123}")


def test_brace_formatter_format():
    formatter = BraceFormatter()
    result = formatter.format("Hello {user}!", {"user": "Alice"})
    assert result == "Hello Alice!"


def test_dollar_formatter_extract_arguments():
    formatter = DollarFormatter()
    arguments = formatter.extract_arguments("Hello $user from $project")
    assert arguments == {"user", "project"}


def test_dollar_formatter_format():
    formatter = DollarFormatter()
    result = formatter.format("Hello $user!", {"user": "Alice"})
    assert result == "Hello Alice!"


def test_dollar_formatter_safe_substitute():
    formatter = DollarFormatter()
    result = formatter.format("Hello $user $missing", {"user": "Alice"})
    assert result == "Hello Alice $missing"


def test_get_formatter_brace():
    formatter = get_formatter(FormatterType.BRACE)
    assert isinstance(formatter, BraceFormatter)


def test_get_formatter_dollar():
    formatter = get_formatter(FormatterType.DOLLAR)
    assert isinstance(formatter, DollarFormatter)


def test_get_formatter_invalid():
    with pytest.raises(ValueError, match="Unknown formatter"):
        get_formatter("invalid")  # type: ignore
