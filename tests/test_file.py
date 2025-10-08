"""Tests for file.py markdown scanning and error handling."""

import pytest
from pathlib import Path
from shinkuro.file import scan_markdown_files


class TestScanMarkdownFiles:
    """Tests for scan_markdown_files function."""

    def test_scan_valid_markdown_file(self, tmp_path):
        """Test scanning a valid markdown file."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\nThis is a test prompt.")

        prompts = list(scan_markdown_files(str(tmp_path)))
        assert len(prompts) == 1
        assert prompts[0].name == "test"
        assert prompts[0].content == "# Test\nThis is a test prompt."

    def test_scan_markdown_with_frontmatter(self, tmp_path):
        """Test scanning markdown with frontmatter."""
        md_file = tmp_path / "greeting.md"
        md_file.write_text(
            """---
name: hello
title: Hello Prompt
description: A greeting prompt
arguments:
  - name: name
    description: Person's name
---
Hello {name}!"""
        )

        prompts = list(scan_markdown_files(str(tmp_path)))
        assert len(prompts) == 1
        assert prompts[0].name == "hello"
        assert prompts[0].title == "Hello Prompt"
        assert prompts[0].description == "A greeting prompt"
        assert len(prompts[0].arguments) == 1
        assert prompts[0].arguments[0].name == "name"
        assert prompts[0].content == "Hello {name}!"

    def test_scan_multiple_markdown_files(self, tmp_path):
        """Test scanning multiple markdown files."""
        (tmp_path / "one.md").write_text("First prompt")
        (tmp_path / "two.md").write_text("Second prompt")
        (tmp_path / "three.md").write_text("Third prompt")

        prompts = list(scan_markdown_files(str(tmp_path)))
        assert len(prompts) == 3

    def test_scan_nested_directories(self, tmp_path):
        """Test scanning nested directories."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root.md").write_text("Root prompt")
        (subdir / "nested.md").write_text("Nested prompt")

        prompts = list(scan_markdown_files(str(tmp_path)))
        assert len(prompts) == 2

    def test_scan_nonexistent_directory(self):
        """Test scanning nonexistent directory returns empty."""
        prompts = list(scan_markdown_files("/nonexistent/path"))
        assert len(prompts) == 0

    def test_scan_file_not_directory(self, tmp_path):
        """Test scanning a file instead of directory returns empty."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("not a directory")
        prompts = list(scan_markdown_files(str(file_path)))
        assert len(prompts) == 0

    def test_malformed_markdown_logged_and_skipped(self, tmp_path, capsys):
        """Test that malformed markdown is logged and skipped."""
        # Create a valid file
        (tmp_path / "valid.md").write_text("Valid content")

        # Create a malformed file (can't read as UTF-8)
        bad_file = tmp_path / "bad.md"
        bad_file.write_bytes(b"\xff\xfe\xff\xfe")  # Invalid UTF-8

        prompts = list(scan_markdown_files(str(tmp_path)))

        # Should get the valid one
        assert len(prompts) == 1
        assert prompts[0].name == "valid"

        # Check that error was logged to stderr
        captured = capsys.readouterr()
        assert "Warning: Failed to process" in captured.err
        assert "bad.md" in captured.err

    def test_markdown_with_invalid_frontmatter_type(self, tmp_path, capsys):
        """Test handling of invalid frontmatter types."""
        md_file = tmp_path / "invalid.md"
        md_file.write_text(
            """---
name: 123
title: [not, a, string]
arguments: not_a_list
---
Content"""
        )

        prompts = list(scan_markdown_files(str(tmp_path)))
        # Should still process, using defaults for invalid types
        assert len(prompts) == 1
        # name is not a string, so should use filename
        assert prompts[0].name == "invalid"
        # title is not a string, so should use filename
        assert prompts[0].title == "invalid"

    def test_empty_markdown_file(self, tmp_path):
        """Test handling empty markdown file."""
        md_file = tmp_path / "empty.md"
        md_file.write_text("")

        prompts = list(scan_markdown_files(str(tmp_path)))
        assert len(prompts) == 1
        assert prompts[0].name == "empty"
        assert prompts[0].content == ""

    def test_markdown_with_default_argument(self, tmp_path):
        """Test markdown with argument that has a default value."""
        md_file = tmp_path / "default.md"
        md_file.write_text(
            """---
arguments:
  - name: greeting
    description: Greeting text
    default: Hello
---
{greeting} World!"""
        )

        prompts = list(scan_markdown_files(str(tmp_path)))
        assert len(prompts) == 1
        assert len(prompts[0].arguments) == 1
        assert prompts[0].arguments[0].default == "Hello"

    def test_ignore_non_markdown_files(self, tmp_path):
        """Test that non-markdown files are ignored."""
        (tmp_path / "test.txt").write_text("Not markdown")
        (tmp_path / "test.py").write_text("# Python file")
        (tmp_path / "test.md").write_text("Markdown file")

        prompts = list(scan_markdown_files(str(tmp_path)))
        assert len(prompts) == 1
        assert prompts[0].name == "test"
